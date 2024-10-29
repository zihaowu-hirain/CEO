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
    pip install ./ceo_py-x.x.x-py3-none-any.whl
    ```

## Demo

```python
# demo.py
import logging
import os

from ceo.brain.agent import Agent
from ceo.brain.lm import get_openai_model

logging.getLogger('ceo').setLevel(logging.DEBUG)

os.environ['OPENAI_API_KEY'] = 'sk-...'


def open_file(filename: str) -> str:
    """
    open and read a file
    :param filename:
    :return file content:
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
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
    return True


model = get_openai_model()

task = 'create a file in work dir called "test_file.txt" and write "hello world" into it, then read it and write "world hello" into it'

Agent([open_file, write_file], model).just_do_it(task)
```

```
[DEBUG] 2024-10-29 21:59:13,415 ceo : Schedule: ['write_file', 'open_file', 'write_file']. Query: "create a file in work dir called "test_file.txt" and write "hello world" into it, then read it and write "world hello" into it".
[DEBUG] 2024-10-29 21:59:15,196 ceo : Action 1/3: I chose to use the tool "write_file" with the parameters {'filename': 'test_file.txt', 'content': 'hello world'}. I successfully wrote the content "hello world" to a file named "test_file.txt".
[DEBUG] 2024-10-29 21:59:17,130 ceo : Action 2/3: I chose to use the tool "open_file" with the parameter {'filename': 'test_file.txt'}. 
I opened and read the file "test_file.txt" and the content of the file is "hello world".
[DEBUG] 2024-10-29 21:59:19,602 ceo : Action 3/3: I chose to use the tool "write_file" with the parameters {'filename': 'test_file.txt', 'content': 'world hello'}. 
I have successfully written the content "world hello" to a file named "test_file.txt".
[DEBUG] 2024-10-29 21:59:21,811 ceo : Conclusion: Your intention was to create a file called "test_file.txt", write "hello world" into it, then read it and write "world hello" into it. 
Based on the actions I have performed, I have successfully achieved your query. 
I created the file "test_file.txt" and wrote "hello world" into it, then read it to confirm the content, and finally wrote "world hello" into the same file. Your query has been successfully completed.
```