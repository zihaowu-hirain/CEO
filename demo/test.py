from ceo.brain.agent import Agent
from ceo.brain.lm import get_openai_model


def open_file(filename: str) -> str:
    """
    open and read a file
    :param filename:
    :return file content:
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        print('file content:', content)
        return content


def write_file(filename: str, content: str) -> bool:
    """
    write a file, if file not exists, will create it
    :param filename:
    :param content:
    :return success or not:
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
        print('new content:', content)
    return True


model = get_openai_model(key="", name="gpt-3.5-turbo-1106")

agent = Agent([open_file, write_file], model)

task = 'create a file in work dir called "test_file.txt" and write "hello world" into it, then read it and write "world hello" into it'

result = agent.just_do_it(task)

print(result)
