import sys

import sympy
from dotenv import load_dotenv

from ceo import BaseAgent, get_openai_model
from ceo.util import agentic, ability

load_dotenv()
sys.set_int_max_str_digits(10**8)

model = get_openai_model()


@ability
def calculator(expr: str) -> float | str:
    # this function only accepts a single math expression
    try:
        try:
            return f'{expr} equals to {sympy.simplify(expr, rational=None)}'
        except ValueError as ve:
            return ve.__repr__()
    except sympy.SympifyError as se:
        return se.__repr__()


@ability
def write_file(filename: str, content: str) -> str:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'{content} written to {filename}.'


@agentic(BaseAgent(abilities=[calculator], brain=model, name='Jack'))
def agent1():
    return


@agentic(BaseAgent(abilities=[write_file], brain=model, name='Tylor'))
def agent2():
    return


if __name__ == '__main__':
    agent = BaseAgent(abilities=[agent1, agent2], brain=model, name='test')
    result = agent.assign("Here is a sphere with a radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, "
                 "find the area and volume respectively, "
                 "then write the results into a file called 'result.txt'.").just_do_it()
    print(result)
