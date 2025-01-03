import os

import langchain_openai
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.125
DEFAULT_TOP_P = 1.00
DEFAULT_GPT = 'gpt-4o-mini'
API_KEY = os.environ.get('OPENAI_API_KEY', None)


def get_lm(key: str = API_KEY, name: str = DEFAULT_GPT, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P,
           stream: bool = False) -> BaseChatModel:
    return langchain_openai.ChatOpenAI(
        api_key=key,
        model=name,
        top_p=top_p,
        temperature=temp,
        streaming=stream
    )
