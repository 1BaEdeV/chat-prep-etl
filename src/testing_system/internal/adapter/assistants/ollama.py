from testing_system.internal.domain.value_objects import \
    AssistantRequest, AssistantResponse
from testing_system.internal.domain.interfaces import IAssistant
import requests
import time


class OllamaAssistant(IAssistant):
    def __init__(self, 
                 model:str,
                 base_url:str,
                 ):
        self.model = model
        self.base_url = base_url
        self._ensure_model()
    
    def _ensure_model(self) -> None:
        """Model checker"""
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
        except requests.ConnectionError:
            raise RuntimeError(f"Ollama not available at {self.base_url}")
        
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        
        if self.model not in model_names:
            print(f"Downloading model {self.model}...")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                stream=True  
            ).json()
            if response.status_code != 200:
                raise RuntimeError(f"Failed to pull model: {response.text}")

    def ask(self,r : AssistantRequest) -> AssistantResponse:
        """Asking ollama model"""
        start_time = time.time()
        documents = "\n".join([
            str(r.retrieved_context[i].id)+"."+r.retrieved_context[i].content \
                for i in range(len(r.retrieved_context))
            ])
        full_prompt = f"Documents:\n{documents}\n\nUser: {r.question}"
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model":self.model,
                    "system":r.system_prompt,
                    "prompt": full_prompt,
                    "temperature": r.temperature if r.temperature is not None else 0.7,
                    "stream": False
                },
                timeout=60
            ).json()
            prompt_tokens = response.get("prompt_eval_count", 0)
            response_tokens = response.get("eval_count", 0)
            total_tokens = prompt_tokens + response_tokens
            return AssistantResponse(
                answer = response["response"],
                token_count=total_tokens,
                latency_ms = (time.time() - start_time) * 1000,
                used_prompt=full_prompt,
                error = None if response.get("done_reason") == "stop" else str(response.get("done_reason")),
                metadata=None
            )
        except Exception as e:
            return AssistantResponse(
                answer="",
                token_count=0,
                latency_ms=0,
                used_prompt=full_prompt,
                error=f"Ollama error: {str(e)}",
                metadata=None
            )