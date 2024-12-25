import inspect
import json
import logging
import os
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo import get_openai_model
from ceo.prompt import DocstringPrompt

log = logging.getLogger('ceo.ability')


def ability(brain: BaseChatModel, override: bool = True, cache: bool = True, cache_dir: str = ''):
    # noinspection PyShadowingNames
    def docstring_generator(func: Callable, brain: BaseChatModel, override: bool) -> Callable:
        if override or func.__doc__ in ('', None):
            func.__doc__ = DocstringPrompt(func).invoke(brain)
            log.debug(f'Docstring generated for {func.__name__}. Docstring: "{func.__doc__}"')
        return func

    # noinspection PyShadowingNames
    def make_cache_filename(func: Callable, cache_dir: str, create_path: bool = False) -> str:
        func_source_file_long = inspect.getfile(func)
        func_source_file_short = os.path.basename(func_source_file_long)
        func_source_file_short = func_source_file_short[:func_source_file_short.rfind('.py')]
        func_source_path = os.path.dirname(func_source_file_long)
        cache_path = os.path.join(func_source_path, cache_dir)
        if create_path and not os.path.exists(cache_path):
            os.mkdir(cache_path)
        return os.path.join(cache_path, f'{func_source_file_short}.{func.__name__}.cache')

    # noinspection PyShadowingNames
    def cache_function(func: Callable, cache_dir: str) -> Callable:
        cache_file = make_cache_filename(func, cache_dir, create_path=True)
        func_doc = inspect.getdoc(func)
        try:
            func_doc = json.loads(func_doc)
        except json.decoder.JSONDecodeError:
            pass
        cache_data: dict = {
            'src': inspect.getsource(func),
            'doc': func_doc
        }
        with open(cache_file, 'wb') as f:
            cache_data_str = json.dumps(cache_data, ensure_ascii=False)
            cache_data_bytes = cache_data_str.encode('utf-8')
            f.write(cache_data_bytes)
        return func

    # noinspection PyShadowingNames
    def read_cache(func: Callable, cache_dir: str) -> dict:
        cache_file = make_cache_filename(func, cache_dir)
        cache_data: dict = dict()
        if not os.path.exists(cache_file):
            return cache_data
        with open(cache_file, 'rb') as f:
            cache_data_bytes = f.read()
            cache_data = json.loads(cache_data_bytes)
        return cache_data

    if cache_dir in ('', None):
        cache_dir = '.cache'

    if callable(brain) and not isinstance(brain, BaseChatModel):
        # noinspection DuplicatedCode
        def decorator(func):
            cache_func = read_cache(func, cache_dir)
            if cache and cache_func.get('src', None) == inspect.getsource(func):
                if override or func.__doc__ in ('', None):
                    func.__doc__ = json.dumps(cache_func.get('doc'), ensure_ascii=False)
                    return func
            func = docstring_generator(func, get_openai_model(), override)
            if cache:
                return cache_function(func, cache_dir)
            return func
        return decorator(brain)

    # noinspection DuplicatedCode
    def decorator(func):
        cache_func = read_cache(func, cache_dir)
        if cache and cache_func.get('src', None) == inspect.getsource(func):
            if override or func.__doc__ in ('', None):
                func.__doc__ = json.dumps(cache_func.get('doc'), ensure_ascii=False)
                return func
        func = docstring_generator(func, brain, override)
        if cache:
            return cache_function(func, cache_dir)
        return func
    return decorator
