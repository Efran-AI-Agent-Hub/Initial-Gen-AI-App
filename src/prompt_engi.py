from http.client import responses

from langchain_classic.chains.llm import LLMChain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_core.messages import HumanMessage, SystemMessage

MODEL = "gemma3:4b"
URL = "http://localhost:11434"


def llm_model(prompt, params):
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

    response = ollama_llm.invoke(prompt)
    return response


def main():
    params = {
        "num_predict": 128,
        "temperature": 0.5,
        "top_p": 0.2,
        "top_k": 1,
    }

    prompt = "The wind is "

    response = llm_model(prompt, params)
    print(f"prompt: {prompt}\n")
    print(f"response : {response}\n")


if __name__ == "__main__":
    main()
