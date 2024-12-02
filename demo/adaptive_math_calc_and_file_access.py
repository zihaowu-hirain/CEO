from ceo import AdaptiveAgent, get_openai_model
from sympy import simplify
from dotenv import load_dotenv

from ceo.util import ability

load_dotenv()


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
    ceo = AdaptiveAgent(abilities=[calculator], brain=get_openai_model(), name='test', p=0.05, beta=1.5)
    ceo.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    result = ceo.just_do_it()
    print(result)
