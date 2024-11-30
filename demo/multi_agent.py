import sys

import sympy
from dotenv import load_dotenv

from ceo import Agent, get_openai_model
from ceo.util import agentic, ability

load_dotenv()
sys.set_int_max_str_digits(10**8)

model = get_openai_model()


@ability
def calculator(expr: str) -> float | str:
    # this only accepts a single math expression
    expr = expr.replace(',', '')
    expr = expr.replace('_', '')
    try:
        try:
            return sympy.simplify(expr, rational=None)
        except ValueError as ve:
            return ve.__repr__()
    except sympy.SympifyError as se:
        return se.__repr__()


@ability
def write_file(filename: str, content: str) -> bool:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


@agentic(Agent(abilities=[calculator], brain=model, name='Jack'))
def agent1():
    return


@agentic(Agent(abilities=[write_file], brain=model, name='Tylor'))
def agent2():
    return


if __name__ == '__main__':
    agent = Agent(abilities=[agent1, agent2], brain=model, name='test')
    result = agent.assign("Here is a sphere with a radius of 5.1121 cm and pi here is 3.14159, "
                 "find the area and volume respectively, "
                 "then write the results into a file called 'result.txt'.").just_do_it()
    print(result)
