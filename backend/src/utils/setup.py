import yaml
from typing import Literal
from langchain_ollama import OllamaLLM, OllamaEmbeddings, ChatOllama
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.constants import ENV_FILE

class LLMSettings(BaseSettings):
    config_path:str = Field(..., description="Path to config file")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="llm_",
        extra="allow"
    )

    def load_config(self):
        with open(self.config_path) as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise f"Error parsing config YAML: {exc}"
        return config

    def get_llm_model(self) -> OllamaLLM:
        config = self.load_config()
        llm_model = OllamaLLM(
            model=config["ollama_config"]["llm_model"],
            base_url=config["ollama_config"]["url"],
            **config["model_params"],
        )
        return llm_model

    def get_chat_model(self) -> ChatOllama:
        config = self.load_config()
        chat_model = ChatOllama(
            model=config["ollama_config"]["chat_model"],
            base_url=config["ollama_config"]["url"],
            **config["model_params"],
            reasoning=config["ollama_config"]["chat_reasoning"],
        )
        return chat_model

    def get_embed_model(self) -> OllamaEmbeddings:
        config = self.load_config()
        embed_model = OllamaEmbeddings(
            model=config["ollama_config"]["embedding_model"],
            base_url=config["ollama_config"]["url"],
        )
        return embed_model


if __name__ == "__main__":
    settings = LLMSettings()
    print(settings)

    model = settings.get_llm_model()
    resp = model.invoke("what day is today?")
    print(resp)
    print("+" * 20)

    embedding_model = settings.get_embed_model()
    resp = embedding_model.embed_query("hello world")
    print(resp)
    print("+" * 20)

    model = settings.get_chat_model()  # get_chat_llm()
    resp = model.invoke("What is 2+2?")
    print(resp.content)
    print("+" * 20)
