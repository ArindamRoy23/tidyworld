"""Default LLM and Embedding Services using LiteLLM."""

__all__ = ["DefaultLLMService", "DefaultEmbeddingService"]

from ._litellm import LiteLLMEmbeddingService, LiteLLMService


class DefaultLLMService(LiteLLMService):
  """Default LLM service using LiteLLM."""

  pass


class DefaultEmbeddingService(LiteLLMEmbeddingService):
  """Default embedding service using LiteLLM."""

  pass
