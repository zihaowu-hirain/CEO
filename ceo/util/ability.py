from langchain_core.language_models import BaseChatModel

from ceo import get_openai_model


def docstring_generator(func: callable, brain: BaseChatModel):
    docstring = func.__doc__
    if docstring in ('', None):
        docstring = brain

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def ability(brain: BaseChatModel):
    if callable(brain) and not isinstance(brain, BaseChatModel):
        def decorator(func):
            return docstring_generator(func, get_openai_model())
        return decorator(brain)

    def decorator(func):
        return docstring_generator(func, brain)
    return decorator


_model = get_openai_model()


@ability
def test():
    return


if __name__ == '__main__':
    print(test())
