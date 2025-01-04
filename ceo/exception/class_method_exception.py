from typing import Callable


class ClassMethodException(TypeError):
    def __init__(self, func: Callable):
        super().__init__(f'"{func.__qualname__}" is a method. Abilities can only be functions instead of methods')
