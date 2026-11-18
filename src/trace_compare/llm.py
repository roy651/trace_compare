"""Single-call LLM client over LiteLLM. Any LiteLLM model string works.

Credentials, in order of precedence:
- LLM_BASE_URL (with LLM_API_KEY): calls go to that OpenAI-compatible endpoint (a gateway, a
  proxy, a local server) and the model name is passed through unchanged.
- LLM_API_KEY alone: the key is sent to the provider named by the model string.
- Neither: the provider's own variables apply (ANTHROPIC_API_KEY, OPENAI_API_KEY, ...).
"""

import os
import re

import litellm

# Drop parameters a provider does not accept (for example "seed").
litellm.drop_params = True

# Claude 4.x models reject the temperature parameter.
_CLAUDE4_RE = re.compile(r"claude-(opus|sonnet|haiku)-4[-_]", re.IGNORECASE)


def _model_supports_temperature(model: str) -> bool:
    return not _CLAUDE4_RE.search(model)


class LLMClient:
    def __init__(self, model: str, temperature: float = 0, max_tokens: int = 15000, seed: int | None = 47):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.last_usage: dict | None = None

    def complete(self, prompt: str, system_message: str) -> str:
        completion_args = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
        }

        if _model_supports_temperature(self.model):
            completion_args["temperature"] = self.temperature

        if self.seed is not None:
            completion_args["seed"] = self.seed

        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        if api_key:
            completion_args["api_key"] = api_key
        if base_url:
            completion_args["base_url"] = base_url
            completion_args["custom_llm_provider"] = "openai"

        response = litellm.completion(**completion_args)

        if getattr(response, "usage", None):
            self.last_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return response.choices[0].message.content
