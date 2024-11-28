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
        docstring_format = {
            "description": {
                "brief_description": "{Brief description of the function's purpose.}",
                "detailed_description": "{Detailed description of the function's behavior, "
                                        "including its main logic, algorithm used, and any other relevant information. "
                                        "This section can include multiple sentences and paragraphs to provide "
                                        "a comprehensive understanding of the function's functionality.}",
                "args": [{
                        "{name of param_1}": {
                            "name": "{name of param_1}",
                            "type": "{data type of param_1}",
                            "description": "{description of param_1, including its role in the function "
                                           "and the constraints for it.}"
                        }
                    }, {
                        "{name of param_2}": {
                            "name": "{name of param_2}",
                            "type": "{data type of param_2}",
                            "description": "{description of param_2, including its role in the function "
                                           "and the constraints for it.}"
                        }
                    }, {
                        "{name of param_...}": {
                            "name": "{name of param_...}",
                            "type": "{data type of param_...}",
                            "description": "{description of param_..., including its role in the function "
                                           "and the constraints for it.}"
                        }
                    }
                ],
                "returns": {
                    "type": "{data type of the return value}",
                    "description": "{description of the return value, including its meaning.}"
                }
            }
        }
        prompt = json.dumps({
            "task": "Generate description for the [function].",
            "function": function_repr,
            "output_format": "json",
            "hint_for_output_format": docstring_format
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'DocstringPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> str | Iterator:
        raw_docstring = model.invoke(self.prompt).content
        if not raw_docstring.startswith('{'):
            raw_docstring = raw_docstring[raw_docstring.find('{'):]
        if not raw_docstring.endswith('}'):
            raw_docstring = raw_docstring[:raw_docstring.find('}') + 1]
        return raw_docstring.replace('\n', '')
