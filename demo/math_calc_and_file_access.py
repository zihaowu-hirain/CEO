import logging

from ceo import Agent, get_openai_model, ability
from sympy import simplify
from dotenv import load_dotenv

load_dotenv()
logging.getLogger('ceo').setLevel(logging.DEBUG)


@ability
def calculator(expr: str) -> float:
    # this function only accepts a single math expression
    return simplify(expr)


@ability
def write_file(filename: str, content: str) -> bool:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


if __name__ == '__main__':
    ceo = Agent(abilities=[calculator, write_file], brain=get_openai_model(), name='Copilot')
    ceo.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    result = ceo.just_do_it()
    print(result)
