import inspect
import json
import logging
from collections.abc import Iterator
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class DocstringPrompt(Prompt):
    def __init__(self, function: Callable, ext_context: str = ''):
        signature = inspect.signature(function)
        f_name: str = function.__name__
        f_parameters: dict = dict()
        f_returns: str = str(signature.return_annotation)
        for name, param in signature.parameters.items():
            f_parameters[name] = str(param.annotation)
        function_repr = json.dumps(obj={
            'name': f_name,
            'parameters': f_parameters,
            'returns': f_returns
        }, ensure_ascii=False)
        docstring_format = '''
        {Brief description of the function's purpose.}

        {Detailed description of the function's behavior, including its main logic, algorithm used, 
        and any other relevant information. This section can include multiple sentences and 
        paragraphs to provide a comprehensive understanding of the function's functionality.}
    
        Args:
            {param1} {(type)}: {Description of param1, including its role in the function and any constraints.}
            {param2} {(type)}: {Description of param2, including its role in the function and any constraints.}
    
        Returns:
            {type}: {Description of the return value, including its type and any relevant information.}
    
        Raises:
            {exception_type}: {Description of the circumstances under which the exception is raised.}
            {exception_type}: {Description of another type of exception that can be raised, if applicable.}
        '''
        prompt = ('Task: Generate docstring for this function.\n'
                  f'Function: {function_repr}\n'
                  f'Output format (docstring format): {docstring_format}\n')
        super().__init__(prompt, ext_context)
        log.debug(f'DocstringPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> str | Iterator:
        return model.invoke(self.prompt).content
