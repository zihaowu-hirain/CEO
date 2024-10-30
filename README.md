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

from ceo import Agent, get_openai_model

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

ceo = Agent([open_file, write_file], model)

ceo.assign(task).just_do_it()
```

```
[DEBUG] 2024-10-30 15:24:25,789 ceo : Schedule: ['write_file', 'open_file', 'write_file']. Query: "User's intention: Create a file named "test_file.txt" in the work directory, write "hello world" into the file, read the content of the file, and write "world hello" into the file.".
[DEBUG] 2024-10-30 15:24:27,563 ceo : Action 1/3: I chose to use the tool "write_file" with the parameters {'filename': 'test_file.txt', 'content': 'hello world'}. I successfully wrote the content "hello world" to a file named "test_file.txt".
[DEBUG] 2024-10-30 15:24:29,345 ceo : Action 2/3: I chose to use the tool "open_file" with the parameter {'filename': 'test_file.txt'}. 
I opened and read the file "test_file.txt" and the content of the file is "hello world".
[DEBUG] 2024-10-30 15:24:35,374 ceo : Action 3/3: I chose to use the tool "write_file" with the parameters {'filename': 'test_file.txt', 'content': 'world hello'}. 
I have successfully written the content "world hello" to a file named "test_file.txt".
[DEBUG] 2024-10-30 15:24:36,949 ceo : Conclusion: Your intention was to create a file named "test_file.txt" in the work directory, write "hello world" into the file, read the content of the file, and write "world hello" into the file.
Based on the actions I have performed, I have successfully achieved your intention. I created the file "test_file.txt", wrote "hello world" into it, read the content of the file which was "hello world", and then wrote "world hello" into the file. So, I have successfully completed all the steps you requested.
```