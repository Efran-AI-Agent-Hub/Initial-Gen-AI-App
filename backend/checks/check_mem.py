# Simply python script testing memory of llm

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Any

from utils.setup import LLMSettings
from functools import partial


def simple_chat():
    settings = LLMSettings()
    llm = settings.get_llm_model()

    template = """Answer the user's question based on the following history:
    History: {history}
    Question: {question}
    """

    # prompt = ChatPromptTemplate.from_template(template)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    history = InMemoryChatMessageHistory()
    history.add_ai_message("Hello. What's your name and how old are you?")
    history.add_user_message("I am 25 years old. My name is Steve")

    print(history.messages)

    mem_chain = (
        {"chat_history": lambda x: history.messages, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    resp = mem_chain.invoke("What's my name and how old am I?")

    print(resp)


def simulate_convo(
    chain: RunnableSerializable[Any, str],
    history: InMemoryChatMessageHistory,
    chat_input,
):
    for question in chat_input:
        resp = chain.invoke(question)
        print("RESPONSE:\n", resp)
        history.add_user_message(question)
        history.add_ai_message(resp)
        print("HISTORY\n:", history.messages)


def get_session_history(store, session_id: str):
    if session_id not in store:
        history = InMemoryChatMessageHistory()
        history.add_ai_message("Hello, I am a super helpful AI named Bob")
        history.add_user_message("Hello Bob, my name is Steve and I'm from Texas")
        store[session_id] = history
    return store[session_id]


def conv_with_mem():
    session_store = {}
    settings = LLMSettings()
    llm = settings.get_llm_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            #! Warning: Using a custom format for LLM response. Make sure custom format doesn't confuse LLM response since it's being appended to history
            (
                "system",
                """You are a helpful assistant. Answer the user's question based on the following history: in the format
         == Your Question is: {question}
         ++ My Answer is: [You answer goes here]
         """,
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    history_factory = partial(get_session_history, session_store)

    chain_with_history = RunnableWithMessageHistory(
        chain,
        history_factory,
        input_messages_key="question",
        history_messages_key="history",
    )

    config = {"configurable": {"session_id": "steve_from_texas"}}

    chat_input_list = [
        "What was your name again?",
        "My favorite sport is Baseball, what is yours?",
        "How many states are in the US? Also, what is my and your name?",
        "What's my favorite sport again? What's your favorite sport",
    ]

    for question in chat_input_list:
        resp = chain_with_history.invoke({"question": question}, config=config)
        print(f"RESPONSE:\n{resp}\n")


if __name__ == "__main__":
    # simple_chat()
    conv_with_mem()
    print("done")
