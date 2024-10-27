def generate_result_prompt(function_name: str, result: str, **kwargs) -> str:
    param = str()
    for key, value in kwargs.items():
            param += f'{key}={value},'
    param = param[:-1]
    prompt = f'{function_name}({param})->{result}'
    print(prompt)
    return prompt


def generate_decision_prompt(query: str, function: object) -> str:
    system_prompt = generate_action_prompt(function)
    prompt = f'<HumanQuery>{query}</HumanQuery>\nYou will respond to <HumanQuery>:\n{system_prompt}'
    print(prompt)
    return prompt


def generate_response_prompt(query: str, function_result: str | None) -> str:
    if function_result is None:
        result = 'No operation was executed.'
    else:
        result = f'The operation was executed by you: {function_result}'
    prompt = (f'# Generate response for <Query> according to the <OperationExecuted>\n'
            f'- You can only outputs a string response\n'
            f'- if an operation was executed, it was executed by you in order to help me\n'
            f'- if no operation was executed, just tell that you do not have the ability to help and give me suggestions\n'
            f'<OperationExecuted>'
            f'{result}'
            f'</OperationExecuted>\n'
            f'<Query>'
            f'{query}'
            f'</Query>\n')
    print(prompt)
    return prompt
