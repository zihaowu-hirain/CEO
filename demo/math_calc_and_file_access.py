import logging

from ceo import (
    Agent,
    Personality,
    get_openai_model,
    ability
)
from sympy import simplify
from dotenv import load_dotenv

load_dotenv()
logging.getLogger('ceo').setLevel(logging.DEBUG)


@ability
def calculator(expr: str) -> float:
    # this function only accepts a single math expression
    return simplify(expr)


@ability
def write_file(filename: str, content: str) -> str:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'{content} written to {filename}.'


if __name__ == '__main__':
    ceo = Agent(abilities=[calculator, write_file], brain=get_openai_model(), name='CEO', personality=Personality.INQUISITIVE)
    radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
    pi = 3.14159
    output_file = 'result.txt'
    query = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
    result = ceo.assign(query).just_do_it()  # area = 95910378.2949379, volume = 88322713378.13666
    print(result)
