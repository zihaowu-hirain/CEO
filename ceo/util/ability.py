from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo import get_openai_model
from ceo.prompt import DocstringPrompt


def docstring_generator(func: Callable, brain: BaseChatModel):
    docstring = func.__doc__
    if docstring in ('', None):
        docstring = DocstringPrompt(func).invoke(brain)

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.__doc__ = docstring
    return wrapper


def ability(brain: BaseChatModel):
    if callable(brain) and not isinstance(brain, BaseChatModel):
        def decorator(func):
            return docstring_generator(func, get_openai_model())
        return decorator(brain)

    def decorator(func):
        return docstring_generator(func, brain)
    return decorator
