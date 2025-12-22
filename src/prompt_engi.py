from typing import Iterator, AsyncIterator
import asyncio

from langchain_classic.chains.llm import LLMChain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableSequence,
    RunnableLambda,
)
from langchain_core.messages import HumanMessage, SystemMessage

MODEL = "gemma3:4b"
URL = "http://localhost:11434"
STREAM_MODE_OPTIONS = ["messages"]


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


async def process_response(
    params, prompt, stream_mode: bool = False, print_lock: asyncio.Lock = None
):
    chunks = []
    async for chunk in UnifiedLLMResponse(llm_model(prompt, params, stream_mode), stream_mode):
        chunks.append(chunk)
    full_response = "".join(chunks)


    if print_lock:
        async with print_lock:
            print(f"PROMPT: {prompt}")
            print(f"RESPONSE: {full_response}")
            print("\n" + ("-" * 10) + "LLM RESPONSE COMPLETE", flush=True)
    else:
        print(f"PROMPT: {prompt}")
        print(f"RESPONSE: {full_response}")
        print("\n" + ("-" * 10) + "LLM RESPONSE COMPLETE", flush=True)


async def basic_prompts():
    params = {
        "num_predict": 128,
        "temperature": 0.5,
        "top_p": 0.2,
        "top_k": 1,
    }

    stream_mode = True
    print_lock = asyncio.Lock()
    prompts = [
        "The future of artificial intelligence is",
        "Once upon a time in a distant galaxy",
        "The benefits of sustainable energy include",
    ]

    tasks = [
        process_response(params, prompt, stream_mode=stream_mode, print_lock=print_lock)
        for prompt in prompts
    ]
    await asyncio.gather(*tasks)


def format_prompt(variables):
    # return prompt.format(**variables)
    prompt = variables["prompt"]
    return [prompt.format(**variables)]


def basic_prompt_template():
    joke_template = """Tell me a {adjective} joke about {content}"""
    prompt_template = PromptTemplate.from_template(joke_template)
    params = {
        "num_predict": 128,
        "temperature": 0.5,
        "top_p": 0.2,
        "top_k": 1,
    }

    ollama_llm = OllamaLLM(
        model=MODEL,
        base_url=URL,
        **params,
    )

    joke_chain = RunnableLambda(format_prompt) | ollama_llm | StrOutputParser()

    response = joke_chain.invoke(
        {"prompt": prompt_template, "adjective": "sad", "content": "fish"}
    )
    print(response)


if __name__ == "__main__":
    # asyncio.run(basic_prompts())
    basic_prompt_template()
