import yaml
from langchain_ollama import OllamaLLM, OllamaEmbeddings, ChatOllama


def get_chat_llm(config_location="configs/config.yaml") -> ChatOllama:
    with open(config_location) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise f"Error parsing config YAML: {exc}"

    llm_model = ChatOllama(
        model="qwen3:4b",
        base_url=config["ollama_config"]["url"],
        **config["model_params"],
    )
    return llm_model

def get_llm(config_location="configs/config.yaml") -> OllamaLLM:
    with open(config_location) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise f"Error parsing config YAML: {exc}"

    llm_model = OllamaLLM(
        model=config["ollama_config"]["llm_model"],
        base_url=config["ollama_config"]["url"],
        **config["model_params"],
    )
    return llm_model


def get_embed(config_location="configs/config.yaml"):
    with open(config_location) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise f"Error parsing config YAML: {exc}"

    embed = OllamaEmbeddings(
        model=config["ollama_config"]["embedding_model"],
        base_url=config["ollama_config"]["url"],
    )

    return embed


if __name__ == "__main__":
    model = get_llm()
    resp = model.invoke("what day is today?")
    print(resp)

    embedding_model = get_embed()
    resp = embedding_model.embed_query("hello world")
    print(resp)

    model = get_chat_llm()
    resp = model.invoke("what day is today?")
    print(resp)
