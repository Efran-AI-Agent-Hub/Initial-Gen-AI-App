from src.setup import get_llm


if __name__ == "__main__":
    llm = get_llm()

    resp = llm.invoke("what day is today")
    print(resp)
