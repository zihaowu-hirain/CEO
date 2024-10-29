# CEO

`CEO` is an easy-to-use AI agent framework. Now, you have taken on the role of the chairman of the board, instruct your `CEO` to carry out the task for you.

## Installation

- From [PYPI](https://pypi.org/project/ceo-py/)

    ```shell
    pip install ceo-py
    ```

- From [Github](https://github.com/vortezwohl/CEO/releases)

    Download .whl first then run

    ```shell
    pip install ./ceo_py-0.0.1b0-py3-none-any.whl
    ```

## Demo

```python
# demo.py
import os

from ceo.brain.agent import Agent
from ceo.brain.lm import get_openai_model

os.environ['OPENAI_API_KEY'] = 'sk-...'


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


model = get_openai_model()

agent = Agent([open_file, write_file], model)

task = 'create a file in work dir called "test_file.txt" and write "hello world" into it, then read it and write "world hello" into it'

result = agent.just_do_it(task)

print(f'Agent: {result}')
```

```
new content: hello world
file content: hello world
new content: world hello

Agent: Your intention is to create a file named "test_file.txt", write "hello world" into it, 
then read it and write "world hello" into it. Based on the actions performed, 
I have successfully created the file "test_file.txt" with the content "hello world" and then overwritten it with the content "world hello". 
Therefore, I have achieved your query.
```