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

## Examples

- ### Simple Task

    1. Precise Calculation: Find the surface area and volume of a sphere.

        ```python
        import logging
        import os

        from ceo import Agent, get_openai_model
        from sympy import simplify

        logging.getLogger('ceo').setLevel(logging.DEBUG)

        os.environ['OPENAI_API_KEY'] = 'sk-...'


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


        agent = Agent(abilities=[constant_calculate], brain=get_openai_model())

        result = agent.assign("Here is a sphere with radius 4.5 and pi here is 3.14159, find the area and volume respectively.").just_do_it()

        print(result)
        ```

        ```
        [DEBUG] 2024-10-30 18:08:55,522 ceo : Schedule: ['constant_calculate', 'constant_calculate']. Query: "User's intention: Calculate the surface area and volume of a sphere with a radius of 4.5 using pi value 3.14159.".
        [DEBUG] 2024-10-30 18:08:57,389 ceo : Action 1/2: I chose to calculate the expression "4 * 3.14159 * (4.5 ** 2)", which represents the area of a circle with a radius of 4.5. The result of this calculation is 254.468790000000.
        [DEBUG] 2024-10-30 18:08:59,723 ceo : Action 2/2: I chose to calculate the expression "(4/3) * 3.14159 * (4.5 ** 3)", which represents the volume of a sphere with a radius of 4.5. The result of this calculation is 381.703185.
        [DEBUG] 2024-10-30 18:09:01,781 ceo : Conclusion: Your intention is to calculate the surface area and volume of a sphere with a radius of 4.5 using the value of pi as 3.14159. I performed the calculations for both the surface area and the volume. 
        I calculated the surface area as 254.468790000000 and the volume as 381.703185. Therefore, I have achieved your intention successfully. Your intention is to calculate the surface area and volume of a sphere with a radius of 4.5 using the value of pi as 3.14159. I performed the calculations for both the surface area and the volume. I calculated the surface area as 254.468790000000 and the volume as 381.703185. Therefore, I have achieved your intention successfully.
        ```

    2. File Access: File Creation, Writing, and Reading

        ```python
        import logging
        import os

        from ceo import Agent, get_openai_model

        logging.getLogger('ceo').setLevel(logging.DEBUG)

        os.environ['OPENAI_API_KEY'] = 'sk-...'


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
        ```

        ```
        # test_file.txt
        world hello
        ```

        ```
        [DEBUG] 2024-10-30 18:32:37,044 ceo : Schedule: ['write_file', 'open_file', 'write_file']. Query: "User's intention: Create a file named "test_file.txt", write "hello world" into it, read its contents, and then write "world hello" into the same file.".
        [DEBUG] 2024-10-30 18:32:38,770 ceo : Action 1/3: I chose to write content to a file, specifically creating a file named "test_file.txt" and writing the text "hello world" into it.
        [DEBUG] 2024-10-30 18:32:40,348 ceo : Action 2/3: I chose to read the content of a file named "test_file.txt". After executing this action, I retrieved the content of the file, which is "hello world".
        [DEBUG] 2024-10-30 18:32:41,970 ceo : Action 3/3: I chose to write content to a file, specifically creating or updating the file named "test_file.txt" with the content "world hello".
        [DEBUG] 2024-10-30 18:32:43,792 ceo : Conclusion: Your intention is to create a file named "test_file.txt", write "hello world" into it, read its contents, and then write "world hello" into the same file. I have successfully achieved your intention. I created the file and wrote "hello world" into it, then I read the contents and confirmed it was "hello world", and finally, I updated the file with "world hello". Everything you wanted has been accomplished.
        ```

- ### Compound Tasks

    1. Find the surface area and volume of a sphere and write the results into a file.

        ```python
        import logging
        import os

        from ceo import Agent, get_openai_model
        from sympy import simplify

        os.environ['OPENAI_API_KEY'] = 'sk-...'
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

        ceo.assign("Here is a sphere with radius 4.5 and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")

        result = ceo.just_do_it()

        print(result)
        ```

        ```
        # result.txt
        Surface Area: 254.468790000000
        Volume: 381.703185
        ```

        ```
        [DEBUG] 2024-10-30 18:42:27,566 ceo : Schedule: ['constant_calculate', 'constant_calculate', 'write_file']. Query: "User's intention: Calculate the surface area and volume of a sphere with radius 4.5 using the formulas \( A = 4 \pi r^2 \) and \( V = \frac{4}{3} \pi r^3 \), then write the results to 'result.txt'.".
        [DEBUG] 2024-10-30 18:42:29,571 ceo : Action 1/3: I chose to calculate the expression "4 * 3.14159 * (4.5 ** 2)", which represents the area of a circle with a radius of 4.5. The result of this calculation is 254.468790000000.
        [DEBUG] 2024-10-30 18:42:31,550 ceo : Action 2/3: I chose to calculate the expression "(4/3) * 3.14159 * (4.5 ** 3)", which represents the volume of a sphere with a radius of 4.5. The result of this calculation is 381.703185.
        [DEBUG] 2024-10-30 18:42:33,607 ceo : Action 3/3: I chose to write a file, and I have written the content "Surface Area: 254.468790000000\nVolume: 381.703185" to a file named "result.txt".
        [DEBUG] 2024-10-30 18:42:35,317 ceo : Conclusion: Your intention is to calculate the surface area and volume of a sphere with a radius of 4.5 using the specified formulas, and then write the results to 'result.txt'. I have successfully achieved your intention. I calculated the surface area as 254.468790000000 and the volume as 381.703185, and I wrote these results to the file 'result.txt'.
        Your intention is to calculate the surface area and volume of a sphere with a radius of 4.5 using the specified formulas, and then write the results to 'result.txt'. I have successfully achieved your intention. I calculated the surface area as 254.468790000000 and the volume as 381.703185, and I wrote these results to the file 'result.txt'.
        ```
