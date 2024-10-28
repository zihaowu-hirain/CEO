import json
from typing import Callable

from ceo.prompt import generate_result_prompt


class Action:
    def __init__(
            self,
            function: Callable
    ):
        self.name: str = function.__name__
        self.description: str = function.__doc__
        self.function: Callable = function
        self.parameters: dict = dict()
        for key, clazz in function.__annotations__.items():
            if key != 'return':
                self.parameters[key] = clazz.__name__

    def __repr__(self):
        return json.dumps(obj={
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters
        }, ensure_ascii=False)

    def __str__(self):
        return self.__repr__()
