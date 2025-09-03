"""LLM Services module."""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TypeVar, Union

import numpy as np
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel

from tidyworld._models import BaseModelAlias

T_model = TypeVar("T_model", bound=Union[BaseModel, BaseModelAlias])
TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


@dataclass
class BaseLLMService:
  """Base class for Language Model implementations."""

  model: str = field(default="")
  base_url: Optional[str] = field(default=None)
  api_key: Optional[str] = field(default=None)
  config: Optional[Dict[str, Any]] = field(default=None)

  def count_tokens(self, text: str) -> int:
    """Returns the number of tokens for a given text using the encoding appropriate for the model."""
    raise NotImplementedError

  def get_model(self) -> LiteLlm:
    """Get the model name for a given model and kwargs."""
    raise NotImplementedError


@dataclass
class BaseEmbeddingService:
  """Base class for Language Model implementations."""

  model: str = field(default="")
  base_url: Optional[str] = field(default=None)
  api_key: Optional[str] = field(default=None)
  config: Optional[Dict[str, Any]] = field(default=None)

  def encode(self, text: str) -> np.ndarray[Any, np.dtype[np.float32]]:
    """Get the embedding for a given text."""
    raise NotImplementedError


class NoopAsyncContextManager:
  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type: Any, exc: Any, tb: Any):
    pass
