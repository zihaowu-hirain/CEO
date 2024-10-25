import json
from typing import Callable

from ceo.prompt import generate_action_prompt


class Action:
    def __init__(
            self,
            description: str,
            function: Callable
    ):
        self.name: str = function.__name__
        self.description: str = description
        self.function: Callable = function
        self.parameters: dict = dict()
        for key, clazz in function.__annotations__.items():
            self.parameters[key] = clazz.__name__

    def __repr__(self):
        return json.dumps(obj={
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters
        }, ensure_ascii=False)

    def __str__(self):
        return self.__repr__()


    def invoke(self, **kwargs):
        return self.function(**kwargs)


# def test(a: int, b: float):
#     return a + b
#
#
# if __name__ == '__main__':
#     print(Action('test', test).invoke(**{'a':1, 'b':2}))
#     print(generate_action_prompt(Action('test', test)))

