from typing import List
from testing_system.internal.domain.entities import MetricValue, Question, Answer, MetricType


class Eval:
    """The measurer of the experiment"""
    """
        The evaluation method
        input: Question, Answer
        output: List[MetricValue] 

        check all the entities in the
        testing_system/internal/domain/entities.py
        """
    
    def __init__(self):
        self.judge = None #TODO

    def execute(self, q: Question, a: Answer) -> List[MetricValue]:
        metrics = []

        #latency(время ответа)
        metrics.append(
            MetricValue(
                type = MetricType.LATENCY,
                value = a.latency_ms,
                metadata=None
            )
        )

        #token_count
        metrics.append(
            MetricValue(
                type = MetricType.TOKEN_COUNT,
                value = a.token_count,
                metadata=None
            )
        )

        if q.retrieved_context_id and a.retrieved_context:
            relevant_found = set(q.retrieved_context_id) & set(a.retrieved_context)

            #precision
            #кол-во правильных из всех найденных
            precision = len(relevant_found)/ len(a.retrieved_context)
            metrics.append(
            MetricValue(
                type = MetricType.PRECISION,
                value = precision,
                metadata=None
            )
        )
            #recall
            #кол-во правильных из всех документов
            recall = len(relevant_found) / len(q.retrieved_context_id)
            metrics.append(
            MetricValue(
                type = MetricType.RECALL,
                value = recall,
                metadata=None
            )
        )



        return metrics