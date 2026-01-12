from typing import Iterator, AsyncIterator, Dict, List
import asyncio
from time import perf_counter

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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


async def llm_model_response(llm: OllamaLLM, prompt: str, stream_mode: bool = False):
    if stream_mode:
        response = llm.astream(prompt)
        async for chunk in response:
            yield chunk
    else:
        response = await llm.ainvoke(prompt)
        yield response


async def process_response(
    llm: OllamaLLM, prompt, stream_mode: bool = False, print_lock: asyncio.Lock = None
):
    chunks = []
    async for chunk in UnifiedLLMResponse(
        llm_model_response(llm, prompt, stream_mode), stream_mode
    ):
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


async def process_prompt_template(
    llm: OllamaLLM,
    template_str: str,
    input_list: List[Dict[str, str]],
    concurrent: bool = False,
):
    prompt_template = PromptTemplate.from_template(template_str)
    chain = prompt_template | llm | StrOutputParser()

    if concurrent:
        results = await chain.abatch(input_list)
    else:
        results = []
        for input in input_list:
            results.append(chain.invoke(input))

    for prompt, resp in zip(input_list, results):
        print("PROMPT:", prompt_template.invoke(prompt))
        print("RESPONSE:", resp)


if __name__ == "__main__":
    start = perf_counter()
    end = perf_counter()
    print(f"Elapsed time: {end - start} seconds")
