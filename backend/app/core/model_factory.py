from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def parse_model_id(model_id: str) -> tuple[str, str]:
    if "/" in model_id:
        provider, model = model_id.split("/", 1)
        return provider.lower(), model
    return "openai", model_id


def get_chat_model(model_id: str, streaming: bool = False) -> BaseChatModel:
    provider, model = parse_model_id(model_id)
    if provider == "anthropic":
        return ChatAnthropic(
            model=model,
            temperature=0,
            streaming=streaming,
        )
    return ChatOpenAI(
        model=model,
        temperature=0,
        streaming=streaming,
    )


def get_embedding_model(model_id: str) -> Embeddings:
    return OpenAIEmbeddings(model=model_id)
