from ceo import Agent, get_openai_model
from sympy import simplify
from dotenv import load_dotenv

from ceo.util import ability

load_dotenv()


@ability
def constant_calculate(expr: str) -> float:
    return simplify(expr)


@ability
def write_file(filename: str, content: str) -> bool:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


if __name__ == '__main__':
    ceo = Agent(abilities=[constant_calculate, write_file], brain=get_openai_model(), name='test')
    ceo.assign("Here is a sphere with radius of 5.1121 cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    result = ceo.just_do_it()
    print(result)
