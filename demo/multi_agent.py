import logging
import sys

import sympy
from dotenv import load_dotenv

from ceo import Agent, get_openai_model

load_dotenv()
log = logging.getLogger("ceo")
log.setLevel(logging.DEBUG)

model = get_openai_model()

sys.set_int_max_str_digits(10**8)


def calculator(expr: str) -> float | str:
    """
    What does this function do: Evaluates a mathematical expression and returns the result or an error message.

    When to use this function: Don't calculate any math problems by yourself, you are not good at math,
    you must use this function to calculate **all** the math calculations, this is the rule you must follow seriously.

    Args:
        expr (str): A string representing the mathematical expression to be evaluated (Which only contains const numbers).
        The expression can be simplified and should not contain commas or underscores.

    Returns:
        float | str: The result of the evaluated expression as a float, or an error message as a string.

    Examples:
        calculator('2.2+7*10') => 72.2
    """
    expr = expr.replace(',', '')
    expr = expr.replace('_', '')
    try:
        try:
            return sympy.simplify(expr, rational=None)
        except ValueError as ve:
            return ve.__repr__()
    except sympy.SympifyError as se:
        return se.__repr__()


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


def talk_to_jack(query: str) -> str:
    """
        Initiates a conversation with 'Jack', an AI agent with mathematical calculation abilities.
        Just initiates only a single conversation with Jack, you can solve any math problem.

        Args:
            query (str): The input query to be processed by Jack.

        Returns:
            str: Jack's response to the query.
    """
    _agent = Agent(abilities=[calculator], brain=model, name='Jack')
    return _agent.assign(query).just_do_it()



def talk_to_tylor(query: str) -> str:
    """
        Initiates a conversation with 'Tylor', an AI agent with file access abilities.

        Args:
            query (str): The input query to be processed by Tylor.

        Returns:
            str: Tylor's response to the query.
    """
    _agent = Agent(abilities=[write_file], brain=model, name='Tylor')
    return _agent.assign(query).just_do_it()


if __name__ == '__main__':
    agent = Agent(abilities=[talk_to_jack, talk_to_tylor], brain=model)
    agent.assign("Here is a sphere with radius 9 and pi here is 3.14159, "
                 "find the area and volume respectively, "
                 "then write the results into a file called 'result.txt'.").just_do_it()
