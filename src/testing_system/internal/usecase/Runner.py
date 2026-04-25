import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
from typing import List
from datetime import datetime, timezone

from testing_system.internal.domain.entities import Answer, Experiment, MetricValue, Question
from testing_system.internal.domain.interfaces import \
    IAssistant, IRetriever, IRegistry
from testing_system.internal.usecase.Eval import Eval
from testing_system.internal.usecase.ProcessQuery import Processor


class Runner:
    """Main testing pipeline"""
    def __init__(self, 
                 registry: IRegistry,
                 assistant: IAssistant, 
                 retriever: IRetriever,
                 top_k: int,
                 num_process_workers: int = 1,
                 num_eval_workers: int = 1,
                 use_threads: bool = True
                 ):
        self.logger = logging.getLogger(__name__)
        self.registry = registry
        self.assistant = assistant
        self.retriever = retriever
        self.processor = Processor(self.assistant, self.retriever)
        self.eval = Eval()
        self.top_k = top_k
        #   for asyncio
        self.num_process_workers = num_process_workers
        self.num_eval_workers = num_eval_workers
        self.use_threads = use_threads

        self.process_queue = asyncio.Queue()
        self.eval_queue = asyncio.Queue()
    
    def _exist(self, experiment: Experiment) -> Experiment:
        """Checks the existence of the configuration in Registry"""
        return self.registry.check(experiment=experiment)

    def _run_process(self, q: Question) -> Answer:
        response = self.processor.execute(
            question = q.text, 
            top_k = self.top_k, 
            system_prompt = q.metadata.get("system_prompt", None),
            temperature = q.metadata.get("temperature", None),
            metadata=None
        )
        return Answer(
            id = q.id,
            text = response.answer,
            retrieved_context=q.retrieved_context_id,
            token_count=response.token_count,
            latency_ms=response.latency_ms,
            metadata=None
        )
    
    def _run_eval(self, q: Question, a: Answer) -> List[MetricValue]:
        return self.eval.execute(q, a)

    async def _process_worker(self, executor):
        while True:
            query = await self.process_queue.get()
            try:
                loop = asyncio.get_running_loop()
                processed = await loop.run_in_executor(executor, self._run_process, query)
                self.experiment.add_answer(processed)
                await self.eval_queue.put((query,processed))
            except Exception as e:
                self.logger.error(f"Process failed for exp {query.id}: {e}")
            finally:
                self.process_queue.task_done()
    
    async def _eval_worker(self, executor):
        while True:
            q,a = await self.eval_queue.get()
            try:
                loop = asyncio.get_running_loop()
                evaluated = await loop.run_in_executor(executor, self._run_eval, q, a)
                self.logger.info(f"Query {q.id} completed")
                
                for m in evaluated:
                    self.experiment.add_metric(m)
            except Exception as e:
                self.logger.error(f"Eval failed for query {q.id}: {e}")
            finally:
                self.eval_queue.task_done()

    async def run(self,experiment: Experiment) -> Experiment:
        """
        Main for Runner
        input: Experiment
        output: Experiment
        For every Experiment checks the existence in registry(logger),
        runs only unseen configurations.
        Processing every single query, evaluates 

        Usage example:
        runner = Runner(...,
                num_process_workers=1,
                num_eval_workers=1,
                use_threads=True) 
        await runner.run(experiment)
        """
        
        experiment_from_registry = self._exist(experiment=experiment)
        if experiment_from_registry != None:
            return experiment_from_registry
        '''
        TODO
        Maybe there are some causes to save not Experiments,
        but only Q-A without ids to retrieve metrics and answer for every 
        seen question configuration? 
        '''

        self.experiment = experiment

        #start_time
        self.experiment.started_at = datetime.now(timezone.utc)
        

        for q in self.experiment.questions:
            await self.process_queue.put(q)

        if self.use_threads:
            executor_class = ThreadPoolExecutor
        else:
            executor_class = ProcessPoolExecutor

        max_workers = max(self.num_process_workers, self.num_eval_workers)
        with executor_class(max_workers=max_workers) as executor:
            process_tasks = [
                asyncio.create_task(self._process_worker(executor))
                for _ in range(self.num_process_workers)
            ]
            eval_tasks = [
                asyncio.create_task(self._eval_worker(executor))
                for _ in range(self.num_eval_workers)
            ]

            await self.process_queue.join()
            await self.eval_queue.join()

            for task in process_tasks + eval_tasks:
                task.cancel()
            await asyncio.gather(*process_tasks, *eval_tasks, return_exceptions=True)

        #end_time
        self.experiment.finished_at = datetime.now(timezone.utc)
        return self.experiment
