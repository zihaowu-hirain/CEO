import logging

from dotenv import load_dotenv

from ceo import Agent, get_openai_model
from sympy import simplify

load_dotenv()
log = logging.getLogger("ceo")
log.setLevel(logging.DEBUG)


def constant_calculate(expr: str) -> float:
    """
    calculate the result of a math expression of constant numbers.
    :param:
        expr (str): a math expression of constant numbers.
    :return:
        float: the result of the expression.
    :example:
        constant_calculate("1 + 3 + 2") -> 6.0
    """
    return simplify(expr)


ceo = Agent(abilities=[constant_calculate], brain=get_openai_model())

result = ceo.assign("Here is a sphere with radius 4.5 and pi here is 3.14159, find the area and volume respectively.").just_do_it()

print(result)
