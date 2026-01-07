import yaml
from langchain_ollama import OllamaLLM, OllamaEmbeddings, ChatOllama


def get_llm(config_location="configs/config.yaml", model_type="llm") -> ChatOllama | OllamaLLM | OllamaEmbeddings:
    if model_type not in ["llm", "embed", "chat"]:
        raise f"Invalid type {type}. Must be either 'llm' or 'embed' or 'chat'"

    with open(config_location) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise f"Error parsing config YAML: {exc}"

    if model_type == "embed":
        llm_model = OllamaEmbeddings(
            model=config["ollama_config"]["embedding_model"],
            base_url=config["ollama_config"]["url"],
        )
    elif model_type == "chat":
        llm_model = ChatOllama(
            model=config["ollama_config"]["chat_model"],
            base_url=config["ollama_config"]["url"],
            **config["model_params"],
            reasoning=config["ollama_config"]["chat_reasoning"]
        )
    else:
        llm_model = OllamaLLM(
            model=config["ollama_config"]["llm_model"],
            base_url=config["ollama_config"]["url"],
            **config["model_params"],
        )

    return llm_model



if __name__ == "__main__":
    model = get_llm()
    resp = model.invoke("what day is today?")
    print(resp)

    embedding_model = get_llm(model_type="embed")
    resp = embedding_model.embed_query("hello world")
    print(resp)

    model = get_llm(model_type="chat") # get_chat_llm()
    resp = model.invoke("What is 2+2?")
    print(resp.content)
