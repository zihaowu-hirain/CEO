import langchain_openai
from langchain_core.language_models import BaseChatModel


def get_lm(key: str, name: str, temp: float, top_p: float, stream: bool = False) -> BaseChatModel:
    return langchain_openai.ChatOpenAI(
        api_key=key,
        model=name,
        top_p=top_p,
        temperature=temp,
        streaming=stream
    )
