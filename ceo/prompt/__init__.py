def generate_action_prompt(function: object):
    return ('# Think if you need to use this function. '
            '\n- If you need this function, format your output into a json string '
            'which keys are the parameter names and the value is the value of each parameter. '
            '\n- If you dont need this function, output an empty json. '
            '> (You can only outputs a json without any other words) '
            '\nThe function is defined as: \n'
            '<Function>'
            f'{function.__repr__()}'
            '</Function>\n')
