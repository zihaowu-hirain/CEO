import inspect
import json
from typing import Callable


class Ability:
    def __init__(self, function: Callable):
        signature = inspect.signature(function)
        self.name: str = function.__name__
        self.description: str = inspect.getdoc(function)
        self.function: Callable = function
        self.parameters: dict = dict()
        self.returns: str = str(signature.return_annotation)
        for name, param in signature.parameters.items():
            self.parameters[name] = str(param.annotation)

    def __repr__(self):
        return json.dumps(obj={
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'returns': self.returns
        }, ensure_ascii=False)

    def __str__(self):
        return self.__repr__()
