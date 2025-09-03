from tidyworld import TidyWorld
from tidyworld._llm._litellm import LiteLLMEmbeddingService, LiteLLMService


async def test_litellmservice_async():
  """Test the LiteLLMService async method."""
  llm = LiteLLMService(model="ollama/gemma3:270m", config={"api_base": "http://host.docker.internal:11434"})
  response = await llm.get_response_async(messages=[{"content": "Write an essay about Delhi", "role": "user"}])
  print("*****************Async LLM Response*****************")
  print(response)


def test_litellmservice_sync():
  """Test the LiteLLMService sync method."""
  llm = LiteLLMService(model="ollama/gemma3:270m", config={"api_base": "http://host.docker.internal:11434"})
  response = llm.get_response(messages=[{"content": "Write an essay about Delhi", "role": "user"}])
  print("*****************Sync LLM Response*****************")
  print(response)


async def test_embedding_async():
  """Test the LiteLLMEmbeddingService async method."""
  embedding_service = LiteLLMEmbeddingService(
    model="ollama/all-minilm", config={"api_base": "http://host.docker.internal:11434"}
  )
  texts = ["Hello, world!", "This is a test.", "Multiple embeddings at once."]
  embeddings = await embedding_service.encode_async(texts)
  print("*****************Async Embedding Response*****************")
  print(f"Async embeddings shape: {embeddings.shape}")  # Should be (3, embedding_dim)


def test_tidyworld_insert():
  """Test the TidyWorld insert method."""
  tidyworld = TidyWorld()
  tidyworld.insert(content=["Hello, world!", "This is a test."], metadata=[{"source": "test"}, {"source": "test"}])


def test_embedding_sync():
  """Test the LiteLLMEmbeddingService sync method."""
  embedding_service = LiteLLMEmbeddingService(
    model="ollama/all-minilm", config={"api_base": "http://host.docker.internal:11434"}
  )
  texts = ["Hello, world!", "This is a test.", "Multiple embeddings at once."]
  embeddings = embedding_service.encode(texts)
  print("*****************Sync Embedding Response*****************")
  print(f"Sync embeddings shape: {embeddings.shape}")  # Should be (3, embedding_dim)


if __name__ == "__main__":
  # asyncio.run(test_litellmservice_async())
  # test_litellmservice_sync()
  # asyncio.run(test_embedding_async())
  # test_embedding_sync()
  test_tidyworld_insert()
