from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo import get_openai_model
from ceo.prompt import DocstringPrompt


def docstring_generator(func: Callable, brain: BaseChatModel):
    if func.__doc__ in ('', None):
        func.__doc__ = DocstringPrompt(func).invoke(brain)
    return func


def ability(brain: BaseChatModel):
    if callable(brain) and not isinstance(brain, BaseChatModel):
        def decorator(func):
            return docstring_generator(func, get_openai_model())
        return decorator(brain)

    def decorator(func):
        return docstring_generator(func, brain)
    return decorator