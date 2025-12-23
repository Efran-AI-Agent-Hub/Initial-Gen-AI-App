import yaml
from langchain_ollama import OllamaLLM


def get_llm(config_location="configs/config.yaml") -> OllamaLLM:
    # llm_model = OllamaLLM()
    with open(config_location) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise f"Error parsing config YAML: {exc}"

    llm_model = OllamaLLM(
        model=config["ollama_config"]["model"],
        base_url=config["ollama_config"]["url"],
        **config["model_params"],
    )

    return llm_model


if __name__ == "__main__":
    model = get_llm()

    result = model.invoke("what day is today?")
    print(result)
