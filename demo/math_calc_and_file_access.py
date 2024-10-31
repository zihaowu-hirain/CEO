import logging

from ceo import Agent, get_openai_model
from sympy import simplify
from dotenv import load_dotenv

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


def write_file(filename: str, content: str) -> bool:
    """
    Write content to a file, creating the file if it does not exist.

    :param filename: The path to the file to be written.
    :param content: The content to be written to the file.
    :return: True if the write operation is successful.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


ceo = Agent(abilities=[constant_calculate, write_file], brain=get_openai_model())

ceo.assign("Here is a sphere with radius 3.1121 and pi here is (3.14159), find the area and volume respectively then write the results into a file called 'result.txt'.")

print(ceo)

# ceo.deprive_abilities([write_file, constant_calculate])

result = ceo.just_do_it()

print(ceo)

print(result)
