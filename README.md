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

## Citation

If you are currently using `ceo` in your research, don't forget to cite it.

```latex
@software {CEO,
author = {Zihao Wu},
title = {CEO: An Intuitive and Modular AI Agent Framework for Task Automation},
publisher = {Github},
howpublished = {\url{https://github.com/vortezwohl/CEO}},
year = {2024},
date = {2024-10-25}
}
```

## Quick Start

To start building your own agent, follow the steps listed.

1. set environmental variable `OPENAI_API_KEY`

    ```
    # .env
    OPENAI_API_KEY=sk-...
    ```

2. bring in `Agent`, `@ability`, and `get_openai_model`

    - `Agent` lets you instantiate an agent 
    
    - `@ability(brain: BaseChatModel)` lets you declare a function as an ability

    ```python
    from ceo import Agent, get_openai_model
    from ceo.util import ability
    ```

3. declare functions as abilities

    ```python
    @ability
    def calculator(expr: str) -> float:
        return simplify(expr)

    @ability
    def write_file(filename: str, content: str) -> bool:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    ```

4. instantiate an agent

    You can grant abilities to agents while instantiating them.

    ```python
    agent = Agent(abilities=[write_file], brain=model, name='Zihao Wu')
    ```

    You can also grant more abilities to agents later:

    ```python
    agent.grant_ability(calculator)
    ```

    or

    ```python
    agent.grant_abilities([calculator])
    ```

    To deprive abilities:

    ```python
    agent.deprive_ability(calculator)
    ```

    or

    ```python
    agent.deprive_abilities([calculator])
    ```

5. assign a query to your agent

    ```python
    agent.assign("Here is a sphere with radius of 3.1121 cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    ```

6. leave the rest to your agent

    ```python
    response = agent.just_do_it()
    print(response)
    ```

> `ceo` also supports multi-agent system, declare a function as agent calling ability with `@agentic(agent: Agent)`, then grant it to an agent. [See example](#multi-agent-task).



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
        # stdout
        test: Your intention is to calculate the surface area and volume of a sphere with a radius of 9.987 cm using pi = 3.14159, and to save the results in a file named 'result.txt'. I have successfully achieved your intention. 

        The calculations yielded the following results:
        - The surface area of the sphere is approximately 1253.37 cm².
        - The volume of the sphere is approximately 4172.47 cm³.

        Additionally, I have written these results into 'result.txt', and the write operation was successful.
        ```