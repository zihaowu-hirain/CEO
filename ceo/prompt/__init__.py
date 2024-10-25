def generate_action_prompt(function: object) -> str:
        return ('# Think if you need to use this function. '
            '\n- If you need this function, format your output into a json string '
            'which keys are the parameter names and the value is the value of each parameter. '
            '\n- If you dont need this function, output an empty json. '
            '> (You can only outputs a json without any other words) '
            '\nThe function is defined as: \n'
            '<Function>'
            f'{function.__repr__()}'
            '</Function>\n')


def generate_result_prompt(function_name: str, result: str, **kwargs) -> str:
        param = str()
        for key, value in kwargs.items():
                param += f'{key}={value},'
        param = param[:-1]
        return f'{function_name}({param})->{result}\n'

