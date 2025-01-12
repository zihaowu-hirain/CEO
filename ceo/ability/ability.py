import asyncio
import copy
import inspect
import json
import threading

from typing_extensions import Callable


class Ability:
    def __init__(self, function: Callable):
        signature = inspect.signature(function)
        doc_str = inspect.getdoc(function)
        self._name: str = function.__name__
        self._description: str | dict = str()
        self._function: Callable = function
        self._parameters: dict = dict()
        self._returns: any = signature.return_annotation
        for name, param in signature.parameters.items():
            self._parameters[name] = str(param.annotation)
        try:
            self._description = json.loads(doc_str)
            self._description = self._description.get('description', self._description)
        except json.decoder.JSONDecodeError:
            self._description = doc_str

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self):
        return self.__repr__()

    def __call__(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self._function):
            __res = None

            def __func(loop: asyncio.AbstractEventLoop):
                nonlocal __res, args, kwargs
                __res = loop.run_until_complete(self._function(*args, **kwargs))

            __thread = threading.Thread(
                target=__func,
                args=(asyncio.new_event_loop(),)
            )
            __thread.start()
            __thread.join(timeout=None)
            return __res
        return self._function(*args, **kwargs)

    def to_dict(self) -> dict:
        param_list: list = list()
        unnecessary_params: tuple = ('args', 'kwargs')
        for name, _ in self._parameters.items():
            if name not in unnecessary_params:
                param_list.append(name)
        return {
            'ability_name': self._name,
            'description': self._description,
            'parameters_required': param_list,
            'returns': str(self._returns)
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> dict:
        return copy.deepcopy(self._parameters)

    @property
    def returns(self) -> any:
        return self._returns

    @property
    def function(self) -> Callable:
        return copy.deepcopy(self._function)
