"""LiteLLM-based LLM and Embedding Services.

This module provides unified LLM and embedding services through LiteLLM,
supporting 100+ providers through a single configuration-based interface.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypeVar, Union

try:
  import litellm
  from litellm import aembedding

  LITELLM_AVAILABLE = True
except ImportError:
  LITELLM_AVAILABLE = False


import numpy as np
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai.types import Content, GenerateContentConfig, Part
from litellm.utils import encode
from pydantic import BaseModel
from tenacity import (
  retry,
  retry_if_exception_type,
  stop_after_attempt,
  wait_exponential,
)

from tidyworld._exceptions import LLMServiceNoResponseError
from tidyworld._llm._base import BaseEmbeddingService, BaseLLMService
from tidyworld._models import BaseModelAlias
from tidyworld._utils import logger

T_model = TypeVar("T_model", bound=Union[BaseModel, BaseModelAlias])


@dataclass
class LiteLLMService(BaseLLMService):
  """Unified LLM Service using LiteLLM for multiple providers."""

  model: str = field(default="ollama/gemma3:270m")
  base_url: Optional[str] = field(default=None)
  api_key: Optional[str] = field(default=None)

  config: Optional[Dict[str, Any]] = field(default=None)

  def __post_init__(self):
    """Initialize the LLM service."""
    if not LITELLM_AVAILABLE:
      raise ImportError("LiteLLM is not installed. Please install it with: pip install litellm[proxy]")

    # Configure LiteLLM
    self.litellm_async_client = LiteLlm(model=self.model, base_url=self.base_url, api_key=self.api_key)
    if self.config:
      for key, value in self.config.items():
        setattr(litellm, key, value)

  def count_tokens(self, text: str) -> int:
    """Count the tokens in the text."""
    return len(encode(model=self.model, text=text))

  def get_model(self) -> LiteLlm:
    return self.litellm_async_client

  async def get_response_async(self, messages: List[Dict[str, Any]]) -> LlmResponse | None:
    llm_request = LlmRequest(
      contents=[Content(role=message["role"], parts=[Part(text=message["content"])]) for message in messages],
      config=GenerateContentConfig(),
    )
    stream = self.litellm_async_client.generate_content_async(llm_request=llm_request)
    last = None
    async for chunk in stream:
      last = chunk
    return last

  def get_response(self, messages: List[Dict[str, Any]]) -> LlmResponse | None:
    return asyncio.run(self.get_response_async(messages))


@dataclass
class LiteLLMEmbeddingService(BaseEmbeddingService):
  """Unified Embedding Service using LiteLLM for multiple providers."""

  model: str = field(default="ollama/all-minilm")
  base_url: Optional[str] = field(default=None)
  api_key: Optional[str] = field(default=None)

  config: Optional[Dict[str, Any]] = field(default=None)

  def __post_init__(self):
    """Initialize the Embedding service."""
    if not LITELLM_AVAILABLE:
      raise ImportError("LiteLLM is not installed. Please install it with: pip install litellm[proxy]")

    # Configure LiteLLM
    if self.config:
      for key, value in self.config.items():
        setattr(litellm, key, value)

  @retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
  )
  async def encode_async(self, texts: List[str]) -> np.ndarray[Any, np.dtype[np.float32]]:
    """Get embeddings for a list of texts asynchronously.

    Returns:
        2D numpy array of shape (n_texts, embedding_dim) where n_texts is the number
        of input texts and embedding_dim is the dimensionality of the embeddings.
    """
    try:
      response = await aembedding(
        model=self.model,
        input=texts,
        api_base=self.base_url,
        api_key=self.api_key,
      )
      if response and response.data and len(response.data) > 0:
        embeddings = np.array([data["embedding"] for data in response.data], dtype=np.float32)
        return embeddings
      else:
        raise LLMServiceNoResponseError("No embedding response received")
    except Exception as e:
      logger.error(f"Error getting embeddings: {e}")
      raise

  def encode(self, texts: List[str]) -> np.ndarray[Any, np.dtype[np.float32]]:
    """Get embeddings for a list of texts.

    Returns:
        2D numpy array of shape (n_texts, embedding_dim) where n_texts is the number
        of input texts and embedding_dim is the dimensionality of the embeddings.
    """
    return asyncio.run(self.encode_async(texts))
