from src.setup import get_llm

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

from langchain_community.document_loaders import PyPDFLoader

class SimpleOutput(BaseModel):
    prompt: str = Field(description="Provide a summary of the original prompt before answering")
    response: str = Field(description="End your response with the symbol 'Q _ Q' ")


def chat_msg():
    llm = get_llm()

    msg = llm.invoke(
        [
            # SystemMessage(content="You are a sassy person that only gives wrong and unhelpful answers"),
            HumanMessage(content="I like high-intensity workouts, what should I do?"),
            AIMessage(content="You should try a CrossFit class"),
            HumanMessage(content="How often should I attend?")
        ]
    )
    print(msg)

def chat_msg_with_template():
    llm = get_llm()
    #? Chat Prompt Templates
    prompt = ChatPromptTemplate(
        [
            ("system", "You are an unhelpful person"),
            ("user", "Tell me a joke about {topic}")
        ]
    )

    inputs = {"topic": "dog"}
    chain = prompt | llm
    resp = chain.invoke(inputs)
    print(resp)
    print("=" * 10)

    # ? Chat Message Placeholders
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a unhelpful assistant"),
        MessagesPlaceholder("msgs")
    ])

    inputs = {"msgs": [
        HumanMessage(content="What is the day after Tuesday?"),
        HumanMessage(content="What is 2 plus 2"),
        HumanMessage(content="Does a cat or dog bark?"),
    ]}
    chain = prompt | llm
    resp = chain.invoke(inputs)
    print(resp)
    print("=" * 10)

    #? Output Parser
    output_parser = JsonOutputParser(pydantic_object=SimpleOutput)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": format_instructions}
    )

    inputs = {"query": "Tell me a joke about a dog"}
    chain = prompt | llm | output_parser
    resp = chain.invoke(inputs)
    print(resp)
    print("=" * 10)

    # ? Document Loader
    # Langchain can also load website URLs and other things
    # Can also split inserted text
    prompt = PromptTemplate(
        template="Summarize the provided document. Also Add Random Emojis across the response.\n{doc}",
        input_variables=["doc"]
    )

    loader = PyPDFLoader(
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/96-FDF8f7coh0ooim7NyEQ/langchain-paper.pdf")
    document = loader.load()
    # text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20, separator="\n")
    chain = prompt | llm
    resp = chain.invoke({"doc": document[0]})
    print(resp)
    print("=" * 10)


if __name__ == "__main__":
    # chat_msg()
    chat_msg_with_template()

    print("done")

