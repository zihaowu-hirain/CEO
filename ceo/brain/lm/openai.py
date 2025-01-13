import langchain_openai
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.125
DEFAULT_TOP_P = 1.00
DEFAULT_GPT = 'gpt-4o-mini'


def get_lm(key: str = None, name: str = DEFAULT_GPT, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P,
           base_url: str = None, stream: bool = False) -> BaseChatModel:
    if base_url is not None:
        return langchain_openai.ChatOpenAI(
            api_key=key,
            model=name,
            top_p=top_p,
            temperature=temp,
            streaming=stream,
            base_url=base_url
        )
    return langchain_openai.ChatOpenAI(
        api_key=key,
        model=name,
        top_p=top_p,
        temperature=temp,
        streaming=stream
    )
