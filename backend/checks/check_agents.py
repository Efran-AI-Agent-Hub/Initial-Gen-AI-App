from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain.agents import create_agent

from utils.setup import get_llm


@tool
def static_weather_resp(location: str):
    """Returns the current weather for a given location."""
    # ? Note: Placeholder --> real app would call weather API
    return f"The weather in {location} is 75F"


@tool
def python_calculator(code: str):
    """
    Useful for when you need to perform calculations or execute Python code.
    Input must be valid Python code.
    """
    reply = PythonREPL()
    return reply.run(code)


def simple_tool():
    tools = [static_weather_resp, python_calculator]
    llm = get_llm(model_type="chat")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""You are a helpful assistant with access to tools. 
        Always use the python_calculator for math and get_weather for locations.""",
    )

    prompt = (
        "What is the weather in Austin, Texas, and what is that temperature squared?"
    )
    resp = agent.invoke({"messages": [("user", prompt)]})
    print("RESPONSE:", resp)

    prompt = "a = 3; b = 1; print(a+b)"
    resp = agent.invoke({"messages": [("user", prompt)]})
    print("RESPONSE:", resp)


if __name__ == "__main__":
    simple_tool()
    print("done")
