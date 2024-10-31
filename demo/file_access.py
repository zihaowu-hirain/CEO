import logging

from dotenv import load_dotenv

from ceo import Agent, get_openai_model

logging.getLogger('ceo').setLevel(logging.DEBUG)

load_dotenv()


def open_file(filename: str) -> str:
    """
    Read the content of a file.

    :param filename: The path to the file to be read.
    :return: The content of the file as a string.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        return content


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


model = get_openai_model()

task = 'create a file in work dir called "test_file.txt" and write "hello world" into it, then read it and write "world hello" into it'

ceo = Agent([open_file, write_file], model)

ceo.assign(task).just_do_it()
