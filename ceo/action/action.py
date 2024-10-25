import json
from typing import Callable

from ceo.prompt import generate_action_prompt, generate_result_prompt


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
            if key != 'return':
                self.parameters[key] = clazz.__name__

    def __repr__(self):
        return json.dumps(obj={
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters
        }, ensure_ascii=False)

    def __str__(self):
        return generate_action_prompt(self)

    def invoke(self, **kwargs):
        return self.function(**kwargs)

    def invoke_formatted(self, **kwargs):
        return generate_result_prompt(
            function_name=self.name,
            result=self.invoke(**kwargs),
            **kwargs
        )

    def invoke_from_string(self, param_str: str):
        kwargs = json.loads(param_str)
        return self.invoke(**kwargs)

    def invoke_from_string_formatted(self, param_str: str):
        kwargs = json.loads(param_str)
        return self.invoke_formatted(**kwargs)
