# Simply python script testing memory of llm

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Any

from setup import get_llm


def simple_chat():
    llm = get_llm()

    template = """Answer the user's question based on the following history:
    History: {history}
    Question: {question}
    """

    # prompt = ChatPromptTemplate.from_template(template)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])

    history = InMemoryChatMessageHistory()
    history.add_ai_message("Hello. What's your name and how old are you?")
    history.add_user_message("I am 25 years old. My name is Steve")


    print(history.messages)

    mem_chain = (
        {"chat_history": lambda x : history.messages, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    resp = mem_chain.invoke("What's my name and how old am I?")

    print(resp)

def simulate_convo(chain: RunnableSerializable[Any, str], history: InMemoryChatMessageHistory, chat_input):
    for question in chat_input:
        resp = chain.invoke(question)
        print("RESPONSE:\n", resp)
        history.add_user_message(question)
        history.add_ai_message(resp)
        print("HISTORY\n:", history.messages)



def conv_with_mem():
    llm = get_llm()

    history = InMemoryChatMessageHistory()
    history.add_ai_message("Hello, I am a super helpful AI named Bob")
    history.add_user_message("Hello Bob, my name is Steve and I'm from Texas")

    print("Current Convo History:", history.messages)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are a helpful assistant. Answer the user's question based on the following history: in the format
         == Your Question is: {question}
         ++ My Answer is: [You answer goes here]
         """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])

    chat_chain = (
        {"chat_history": lambda x : history.messages, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


    chat_input_list = ["What was your name again?",
                       "My favorite sport is Baseball, what is yours?",
                       "How many states are in the US? Also, what is my and your name?",
                       "What's my favorite sport again? What's your favorite sport"]

    simulate_convo(chat_chain, history, chat_input_list)


if __name__ == "__main__":

    # simple_chat()
    conv_with_mem()
    print("done")