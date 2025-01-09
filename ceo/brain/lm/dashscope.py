import langchain_community.chat_models.tongyi
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.125
DEFAULT_TOP_P = 1.00
DEFAULT_QWEN = 'qwen-plus'


def get_lm(key: str = None, name: str = DEFAULT_QWEN, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P,
           stream: bool = False) -> BaseChatModel:
    return langchain_community.chat_models.tongyi.ChatTongyi(
        dashscope_api_key=key,
        model=name,
        top_p=top_p,
        temperature=temp,
        streaming=stream
    )