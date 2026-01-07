# Simple python script testing asking questions to LLM

from typing import List
from time import perf_counter

from langchain_ollama import OllamaLLM

from setup import get_llm

import asyncio
from src.prompt_engi import process_response, process_prompt_template


class LLMStreamTester:
    def __init__(self, model: OllamaLLM):
        self.model = model

    async def execute_prompt(self, prompts: List[str], msg=None, stream_mode=False):
        if msg:
            print(msg)
        if len(prompts) == 1:
            await process_response(self.model, prompts[0], stream_mode=stream_mode)
        else:
            print_lock = asyncio.Lock()
            tasks = [
                process_response(self.model, prompt, stream_mode, print_lock)
                for prompt in prompts
            ]
            print("CONCURRENT REQUESTS:")
            await asyncio.gather(*tasks)


async def check_output_stream():
    llm = get_llm()
    llm_tester = LLMStreamTester(llm)
    prompts = ["The wind is "]
    msg = "SINGLE REQUEST:"
    stream_mode = False
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    prompts = ["The wind is "]
    msg = "SINGLE STREAM REQUEST:"
    stream_mode = True
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    msg = "CONCURRENT REQUESTS:"
    stream_mode = False
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    prompts = ["The wind is ", "what color is the sky?", "whats 2+2?"]
    msg = "CONCURRENT REQUESTS:"
    stream_mode = True
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)


async def check_output_prompts():
    llm = get_llm()
    llm_tester = LLMStreamTester(llm)
    stream_mode = True

    # ? Simple statement or request
    # Useful for exploring model capabilities and checking how it responds with minimal input
    msg = "BASIC PROMPTS:"
    prompts = [
        "The future of artificial intelligence is",
        "Once upon a time in a distant galaxy",
        "The benefits of sustainable energy include",
    ]
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    # ? Prompts with no examples or prior specific training on tasks.
    # Tests  model's ability to understand instructions and apply knowledge to new context w/o demonstration
    # llm = get_llm()
    # llm_tester = LLMStreamTester(llm)
    msg = "ZERO-SHOT PROMPTS:"
    prompts = [
        """Classify the following moview review as positive or negative:
        'Demon Slayer: Infinity Castle is everything I hoped for and more. From start to finish, it's an emotional rollercoaster that delivers breathtaking animation, incredible action sequences, and heart-piercing storytelling. Ufotable has once again raised the bar for what an anime movie can achieve.
        The visuals are absolutely jaw-dropping. Every scene inside the Infinity Castle feels alive, with a haunting atmosphere and rich details that pull you into the chaos. The fight choreography is some of the best I've ever seen, perfectly balancing raw intensity with emotional depth. The sound design and soundtrack amplify every moment, making the battles and quieter scenes equally unforgettable.
        What really hit me was the emotional weight of the story. Watching the characters push past their limits and make heartbreaking sacrifices left me speechless. You can feel the stakes in every moment, and by the end, I was both wrecked and inspired.
        This isn't just a movie. It's an experience. A triumph for the Demon Slayer series and a landmark in anime cinema. Whether you're a longtime fan or new to the series, Infinity Castle will stay with you long after the credits roll.'
        """,
        "In one paragraph, summarize the current state of climate change in relation to geo politics",
        "Translate the following phrase from English to Spanish: 'Can a person have too many cats? Of cource not!'",
    ]
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    # ? Prompt provides single example for task before asking to perform task
    # Provides model format and template for desired output
    # Useful for guiding model to desired result w/o providing many examples.
    msg = "ONE-SHOT PROMPTS:"
    prompts = [
        """
        Here is an example of a formal email: 
        '
        Dear Mr. Thompson,
        I would like to request a brief meeting later this week to discuss our progress on Project Alpha. Please let me know if you have any availability on Thursday afternoon.
        Best regards, Jane Doe
        '
        Based on the that, write a formal email requesting to reschudle a meeting due to conflicting deadlines
        """,
        """
        Here is an example technical concept (API (Application Programming Interface)) explained simply:
        '
        Think of an API like a waiter in a restaurant. You (the user) tell the waiter what you want from the menu, the waiter takes that request to the kitchen (the system), and then brings the food back to you. You don't need to know how the stove works; you just need to talk to the waiter.
        '
        Based on that, give a simple explaination of Blockchain
        """,
    ]
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    # ? Prompt provides several examples before asking for task
    # Provides clearer patter for model to better understand desired output, style, format, & reasoning
    # Effective for complex tasks that require nuance
    msg = "FEW-SHOT PROMPTS:"
    prompts = [
        """
        Here's some examples of product reviews and their analysis
        
        Example 1: Review: "The shoes arrived two days early and were packaged beautifully!" Analysis: Positive | Shipping
        Example 2: Review: "The sole of the boot started peeling off after only one week of light wear." Analysis: Negative | Product
        Example 3: Review: "I tried calling their support line five times, but I was kept on hold for an hour." Analysis: Negative | Customer Service
        
        Based on the examples, what is the analysis of the following review:
        "The fabric is incredibly soft and the fit is perfect, but it took nearly a month to get to my house."
        """
    ]
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    # ? Prompt encourages model to break down complex problem step by step.
    # Helps model arrive to correct solution
    msg = "CHAIN OF THOUGHT (CoT) PROMPTS:"
    prompts = [
        """
        Consider the problem: 'A store has 14 sandwiches. They sold 5 sandwiches today and got a new delivery of 8. 
        How many sandwiches are there now?’
        Break down each step of your calculation
        """
    ]
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)

    # ? Prompts that ask model to generate multiple solutions to same question then evaluate different approaches for result to determine most consistent/reliable result.
    # Enhances model accuracy by leveraging models ability to tackle problem from multiple angles.
    # Gives model comparison points
    msg = "SELF CONSISTENCY PROMPTS:"
    prompts = [
        """
        When I was 8, my sister was half of my age. Now I am 70, what age is my sister?
        Provide three independent calculations and explanations, then determine the most consistent result.
        """
    ]
    await llm_tester.execute_prompt(prompts=prompts, msg=msg, stream_mode=stream_mode)


async def check_output_templates():
    llm = get_llm()

    # ? Text Summarization
    template_str = "Summarize the {content} in one sentence."
    input_list = [
        {
            "content": """
        The rapid advancement of technology in the 21st century has transformed various industries, including healthcare, education, and transportation. 
        Innovations such as artificial intelligence, machine learning, and the Internet of Things have revolutionized how we approach everyday tasks and complex problems. 
        For instance, AI-powered diagnostic tools are improving the accuracy and speed of medical diagnoses, while smart transportation systems are making cities more efficient and reducing traffic congestion. 
        Moreover, online learning platforms are making education more accessible to people around the world, breaking down geographical and financial barriers. 
        These technological developments are not only enhancing productivity but also contributing to a more interconnected and informed society.
    """
        }
    ]

    await process_prompt_template(llm, template_str, input_list, concurrent=True)

    # ? Quick Answer

    template_str = """
    Answer the {question} based on the {content}.
    Respond "Unsure about answer" if not sure about the answer.
    
    Answer:
    """

    input_list = [
        {
            "question": "Which planets in the solar system are rocky and solid?",
            "content": """
            The solar system consists of the Sun, eight planets, their moons, dwarf planets, and smaller objects like asteroids and comets. 
            The inner planets—Mercury, Venus, Earth, and Mars—are rocky and solid. 
            The outer planets—Jupiter, Saturn, Uranus, and Neptune—are much larger and gaseous.
        """,
        }
    ]

    await process_prompt_template(llm, template_str, input_list, concurrent=True)

    # ? Code Generation
    llm = get_llm()
    template_str = """
   Generate an SQL query based on the {description}
    
    SQL Query:
    
    """

    input_list = [
        {
            "description": """
            Retrieve the names and email addresses of all customers from the 'customers' table who have made a purchase in the last 30 days. 
            The table 'purchases' contains a column 'purchase_date'
        """
        }
    ]

    await process_prompt_template(llm, template_str, input_list, concurrent=True)


if __name__ == "__main__":
    start = perf_counter()
    asyncio.run(check_output_stream())
    asyncio.run(check_output_prompts())
    asyncio.run(check_output_templates())
    end = perf_counter()
    print(f"Elapsed time: {end - start} seconds")
