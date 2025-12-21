from typing import Iterator, AsyncIterator
import asyncio

from langchain_classic.chains.llm import LLMChain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_core.messages import HumanMessage, SystemMessage

MODEL = "gemma3:4b"
URL = "http://localhost:11434"
STREAM_MODE_OPTIONS = ["messages"]

print_lock = asyncio.Lock()


class UnifiedLLMResponse:
    """
    Wrapper class that provided unified interface for LLM response
    """

    def __init__(self, iterator: AsyncIterator[str], is_streaming):
        self._iterator = iterator
        self._is_streaming = is_streaming
        self._cached_response = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._iterator.__anext__()

    async def collect(self) -> str:
        if self._cached_response is not None:
            return self._cached_response

        chunks = []
        async for chunk in self._iterator:
            chunks.append(chunk)
        self._cached_response = "".join(chunks)
        return self._cached_response


async def llm_model(prompt: str, params: dict, stream_mode: bool = False):
    default_params = {
        "num_predict": 256,  # Ollama's equivalent to max_new_tokens
        "temperature": 0.5,  # Randomness (0.0 = deterministic, 1.0 = creative)
        "top_p": 0.2,  # Nucleus sampling
        "top_k": 1,  # Top-k sampling
    }

    for k, v in params.items():
        default_params[k] = v

    ollama_llm = OllamaLLM(
        model=MODEL,
        base_url=URL,
        **default_params,
    )

    if stream_mode:
        response = ollama_llm.astream(prompt)
        async for chunk in response:
            yield chunk
    else:
        response = await ollama_llm.ainvoke(prompt)
        yield response


async def process_response(params, prompt, stream_mode: bool = False):
    response_obj = UnifiedLLMResponse(
        llm_model(prompt, params, stream_mode=stream_mode), is_streaming=stream_mode
    )
    response = await response_obj.collect()
    async with print_lock:
        print(f"PROMPT: {prompt}")
        print(f"RESPONSE:\n {response}\n")


async def ex1_single(params):
    # single request
    stream_mode = False
    prompt = "The wind is "
    print("SINGLE REQUEST:")
    await process_response(params, prompt, stream_mode=stream_mode)
    print()


async def ex2_single_stream(params):
    # single request streaming
    stream_mode = True
    prompt = "The wind is "
    print("SINGLE STREAM REQUEST:")
    await process_response(params, prompt, stream_mode=stream_mode)
    print()


async def ex3_concurrent(params):
    # single request streaming
    stream_mode = False
    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    tasks = [process_response(params, prompt, stream_mode) for prompt in prompts]
    print("CONCURRENT REQUESTS:")
    responses = await asyncio.gather(*tasks)
    print()


async def ex4_concurrent_stream(params):
    # single request streaming
    stream_mode = True
    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    tasks = [process_response(params, prompt, stream_mode) for prompt in prompts]
    print("CONCURRENT REQUESTS:")
    responses = await asyncio.gather(*tasks)
    print()


if __name__ == "__main__":
    params = {
        "num_predict": 128,
        "temperature": 0.5,
        "top_p": 0.2,
        "top_k": 1,
    }
    print("=" * 10 + "\n")
    asyncio.run(ex1_single(params=params))
    print("=" * 10 + "\n")
    asyncio.run(ex2_single_stream(params=params))
    print("=" * 10 + "\n")
    asyncio.run(ex3_concurrent(params=params))
    print("=" * 10 + "\n")
    asyncio.run(ex4_concurrent_stream(params=params))
