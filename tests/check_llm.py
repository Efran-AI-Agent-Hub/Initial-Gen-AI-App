from typing import List

import asyncio
from src.prompt_engi import process_response

class LLMStreamTester:
    def __init__(self, params):
        self.params = params

    async def execute_prompt(self, prompts: List[str], msg = None, stream_mode = False):
        if msg:
            print(msg)
        if len(prompts) == 1:
            await process_response(self.params, prompts[0], stream_mode=stream_mode)
        else:
            print_lock = asyncio.Lock()
            tasks = [process_response(self.params, prompt, stream_mode, print_lock) for prompt in prompts]
            print("CONCURRENT REQUESTS:")
            await asyncio.gather(*tasks)



def check_output_stream():
    params = {
        "num_predict": 128,
        "temperature": 0.5,
        "top_p": 0.2,
        "top_k": 1,
    }

    llm_tester = LLMStreamTester(params)
    prompts = ["The wind is "]
    msg = "SINGLE REQUEST:"
    stream_mode = False
    # asyncio.run(llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode))

    prompts = ["The wind is "]
    msg = "SINGLE STREAM REQUEST:"
    stream_mode = True
    asyncio.run(llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode))

    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    msg = "CONCURRENT REQUESTS:"
    stream_mode = False
#     asyncio.run(llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode))

    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    msg = "CONCURRENT REQUESTS:"
    stream_mode = True
    asyncio.run(llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode))

def check__output_prompts():
    params = {
        "num_predict": 128,
        "temperature": 0.5,
        "top_p": 0.2,
        "top_k": 1,
    }

    llm_tester = LLMStreamTester(params)

    print("=" * 10 + "\n")
    prompts = [
            "The future of artificial intelligence is",
            "Once upon a time in a distant galaxy",
            "The benefits of sustainable energy include"
        ]
    msg = "BASIC PROMPTS:"
    stream_mode = True
    asyncio.run(llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode))


if __name__ == "__main__":
    # check_output_stream()
    check__output_prompts()
