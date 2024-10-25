def generate_action_prompt(function: object) -> str:
    return ('# Think if you need to use this function. '
        '\n- If you need this function, specify the parameters and format your output into a json string '
        'which keys are the parameter names and the value is the value of each parameter. '
        '\n- If you dont need this function, output an empty json. '
        '\n- (You only gives the parameter in a standalone json) '
        '\n- (You can only outputs a json without any other words) '
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


def generate_decision_prompt(query: str, function: object) -> str:
    system_prompt = generate_action_prompt(function)
    return f'<HumanQuery>{query}</HumanQuery>\nYou will respond to <HumanQuery>:\n{system_prompt}\n'


def generate_response_prompt(query: str, function_result: str | None) -> str:
    if function_result is None:
        result = 'No operation was executed.'
    else:
        result = f'The operation was executed: {function_result}'
    return (f'# Generate response for <Query> according to the <Result>\n'
            f'> (You can only outputs a string response, if no operation was executed, just tell that you could not answer my query) \n'
            f'<Result>'
            f'{result}'
            f'</Result>'
            f'<Query>'
            f'{query}'
            f'</Query>\n')

