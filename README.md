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

## These Projects Are Built With `ceo-py`

- [CEO-Alfred-TheProcessManager](https://github.com/vortezwohl/CEO-Alfred-TheProcessManager)

- [CEO-Tomohiro](https://github.com/vortezwohl/CEO-Tomohiro)

- [CEO-Captain](https://github.com/vortezwohl/CEO-Captain)

## Examples

- ### Compound Tasks

    1. Find the surface area and volume of a sphere and write the results into a file.

        ```python
        from ceo import Agent, get_openai_model
        from sympy import simplify
        from dotenv import load_dotenv

        from ceo.util import ability

        load_dotenv()


        @ability
        def constant_calculate(expr: str) -> float:
            return simplify(expr)


        @ability
        def write_file(filename: str, content: str) -> bool:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True


        if __name__ == '__main__':
            ceo = Agent(abilities=[constant_calculate, write_file], brain=get_openai_model(), name='test')
            ceo.assign("Here is a sphere with radius of 3.1121 cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
            result = ceo.just_do_it()
            print(result)
        ```

        ```
        # result.txt
        Surface Area: 121.707287767968 cm²
        Volume: 126.255083420897 cm³
        ```

        ```
        # stdout
        test: Your intention is to calculate the surface area and volume of a sphere with a radius of 3.1121 cm using pi as 3.14159, and to save the results in 'result.txt'. I have successfully achieved your intention. 

        The calculations I performed are as follows:
        - Surface Area: 121.707287767968 cm²
        - Volume: 126.255083420897 cm³

        I also saved these results in 'result.txt'.
        ```

- ### Multi-agent Task
    
    1. Ask the suitable agents to find the surface area and volume of a sphere and write the results into a file.
  
        ```python
        import sys

        import sympy
        from dotenv import load_dotenv

        from ceo import Agent, get_openai_model
        from ceo.util import agentic, ability

        load_dotenv()
        sys.set_int_max_str_digits(10**8)

        model = get_openai_model()


        @ability
        def calculator(expr: str) -> float | str:
            expr = expr.replace(',', '')
            expr = expr.replace('_', '')
            try:
                try:
                    return sympy.simplify(expr, rational=None)
                except ValueError as ve:
                    return ve.__repr__()
            except sympy.SympifyError as se:
                return se.__repr__()


        @ability
        def write_file(filename: str, content: str) -> bool:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True


        @agentic(Agent(abilities=[calculator], brain=model, name='Jack'))
        def agent1():
            return


        @agentic(Agent(abilities=[write_file], brain=model, name='Tylor'))
        def agent2():
            return


        if __name__ == '__main__':
            agent = Agent(abilities=[agent1, agent2], brain=model, name='test')
            result = agent.assign("Here is a sphere with a radius of 9.987 cm and pi here is 3.14159, "
                        "find the area and volume respectively, "
                        "then write the results into a file called 'result.txt'.").just_do_it()
            print(result)
        ```

        ```
        # result.txt
        Calculated Surface Area: 1253.37 cm²
        Calculated Volume: 4172.47 cm³
        ```

        ```
        test: Your intention is to calculate the surface area and volume of a sphere with a radius of 9.987 cm using pi = 3.14159, and to save the results in a file named 'result.txt'. I have successfully achieved your intention. 

        The calculations yielded the following results:
        - The surface area of the sphere is approximately 1253.37 cm².
        - The volume of the sphere is approximately 4172.47 cm³.

        Additionally, I have written these results into 'result.txt', and the write operation was successful.
        ```