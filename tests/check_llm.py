import asyncio
from src.prompt_engi import process_response


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
    print_lock = asyncio.Lock()

    tasks = [process_response(params, prompt, stream_mode,print_lock) for prompt in prompts]
    print("CONCURRENT REQUESTS:")
    responses = await asyncio.gather(*tasks)
    print()


async def ex4_concurrent_stream(params):
    # single request streaming
    stream_mode = True
    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    print_lock = asyncio.Lock()

    tasks = [process_response(params, prompt, stream_mode, print_lock) for prompt in prompts]
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
