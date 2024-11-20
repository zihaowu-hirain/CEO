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
        import logging

        from ceo import Agent, get_openai_model
        from ceo.util import ability
        from sympy import simplify
        from dotenv import load_dotenv

        load_dotenv()
        log = logging.getLogger("ceo")
        log.setLevel(logging.DEBUG)

        @ability
        def constant_calculate(expr: str) -> float:
            return simplify(expr)

        @ability
        def write_file(filename: str, content: str) -> bool:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        ceo = Agent(abilities=[constant_calculate, write_file], brain=get_openai_model(), name='test')
        ceo.assign("Here is a sphere with radius 3.1121 and pi here is (3.14159), find the area and volume respectively then write the results into a file called 'result.txt'.")
        ceo.just_do_it()
        ```

        ```
        # result.txt
        Surface Area: 121.707287767968
        Volume: 126.255083420897
        ```

        ```
        [DEBUG] 2024-11-21 00:34:34,348 ceo : Agent: test, Schedule: ['constant_calculate', 'constant_calculate', 'write_file']. Query: "User's intention: Calculate the surface area and volume of a sphere with radius 3.1121 using specified formulas and write the results to 'result.txt'.".
        [DEBUG] 2024-11-21 00:34:37,017 ceo : Agent: test, Action 1/3: I chose to use the tool to evaluate a mathematical expression. Specifically, I input the expression '4*3.14159*3.1121**2' into the function designed to compute the result of mathematical expressions. The result of this calculation was 121.707287767968.
        [DEBUG] 2024-11-21 00:34:39,399 ceo : Agent: test, Action 2/3: I chose to use the tool to evaluate a mathematical expression. Specifically, I input the expression '4/3*3.14159*3.1121**3' into the function designed to compute the result of mathematical expressions. The result of this calculation is 126.255083420897.
        [DEBUG] 2024-11-21 00:34:41,764 ceo : Agent: test, Action 3/3: I chose to use the tool to write a file. Specifically, I provided the filename "result.txt" and the content "Surface Area: 121.707287767968\nVolume: 126.255083420897". The operation was successful, and the result indicates that the content was successfully written to the file. The result is "True".
        [DEBUG] 2024-11-21 00:34:47,074 ceo : Agent: test, Conclusion: Your intention is to calculate the surface area and volume of a sphere with a radius of 3.1121 and write the results to 'result.txt'. I have successfully achieved your intention. 

        The calculations I performed are as follows:
        - Surface Area: 121.707287767968
        - Volume: 126.255083420897

        These results have been written to 'result.txt' as requested.
        ```

- ### Multi-agent Task
    
    1. Ask the suitable agents to find the surface area and volume of a sphere and write the results into a file.
  
        ```python
        import logging
        import sys

        import sympy
        from dotenv import load_dotenv
        from ceo import Agent, get_openai_model
        from ceo.util import agentic, ability

        load_dotenv()
        log = logging.getLogger("ceo")
        log.setLevel(logging.DEBUG)
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

        
        agent = Agent(abilities=[agent1, agent2], brain=model, name='test')
        agent.assign("Here is a sphere with radius 5 meters and pi here is 3.14159, "
                    "find the area and volume respectively, "
                    "then write the results into a file called 'result.txt'.").just_do_it()
        ```

        ```
        # result.txt
        Surface Area: 1017.88
        Volume: 3053.63
        ```

        ```
        [DEBUG] 2024-11-19 15:06:34,586 ceo : Agent: CEO (Default), Schedule: ['talk_to_jack', 'talk_to_jack', 'talk_to_tylor']. Query: "User's intention: Calculate the surface area and volume of a sphere with radius 9 using the formulas \( A = 4\pi r^2 \) and \( V = \frac{4}{3}\pi r^3 \), then write the results to 'result.txt'.".
        [DEBUG] 2024-11-19 15:06:41,849 ceo : Agent: Jack, Schedule: ['calculator', 'calculator', 'calculator']. Query: "User's intention: Calculate the surface area and volume of a sphere with radius 9 using specified formulas and save the results to 'result.txt'.".
        [DEBUG] 2024-11-19 15:06:44,002 ceo : Agent: Jack, Action 1/3: I chose to use the calculator tool to evaluate the mathematical expression "4*3.14159*9^2". This expression involves multiplying 4 by the value of π (approximately 3.14159) and then by the square of 9. The result of this calculation is 1017.87516000000.
        [DEBUG] 2024-11-19 15:06:47,162 ceo : Agent: Jack, Action 2/3: I chose to use the calculator tool to evaluate the mathematical expression "4/3*3.14159*9^3". This expression calculates the volume of a sphere with a radius of 9 units, using the formula for the volume of a sphere (V = 4/3 * π * r^3). The result of this calculation is 3053.62548000000.
        [DEBUG] 2024-11-19 15:06:52,331 ceo : Agent: Jack, Action 3/3: I attempted to use the calculator tool to evaluate a mathematical expression that included two floating-point numbers: "1017.87516000000, 3053.62548000000". However, I mistakenly included a comma between the two numbers, which is not a valid format for the expression. The calculator tool returned an error message indicating that it could not parse the input due to invalid syntax.

        The result of my attempt is: SympifyError("could not parse '1017.87516000000 3053.62548000000'", SyntaxError('invalid syntax', ('<string>', 1, 28, "Float ('1017.87516000000' )Float ('3053.62548000000' )", 1, 33)))
        [DEBUG] 2024-11-19 15:06:54,776 ceo : Agent: Jack, Conclusion: Your intention is to calculate the surface area and volume of a sphere with a radius of 9 and save the results to 'result.txt'. I successfully calculated the surface area as approximately 1017.88 and the volume as approximately 3053.63. However, I failed to save these results to 'result.txt' because I encountered an error when trying to format the output due to an invalid syntax in my attempt to combine the results.

        Here are the results you wanted:
        - Surface Area: 1017.88
        - Volume: 3053.63

        Unfortunately, I did not achieve your intention to save these results to a file.
        [DEBUG] 2024-11-19 15:06:58,303 ceo : Agent: CEO (Default), Action 1/3: I initiated a conversation with Jack to perform calculations related to the surface area and volume of a sphere with a radius of 9. I provided Jack with the formulas for both calculations: the surface area \( A = 4\pi r^2 \) and the volume \( V = \frac{4}{3}\pi r^3 \), using \( \pi \) as 3.14159. 

        Jack successfully calculated the surface area as approximately 1017.88 and the volume as approximately 3053.63. However, he encountered an error when attempting to save these results to a file named 'result.txt' due to an invalid syntax in the output formatting.

        The results are as follows:
        - Surface Area: 1017.88
        - Volume: 3053.63

        Unfortunately, the intention to save these results to a file was not achieved.
        [DEBUG] 2024-11-19 15:07:03,367 ceo : Agent: Jack, Schedule: []. Query: "User's intention: Create or open 'result.txt', write the surface area (1017.88) and volume (3053.63) into it, then save and close the file.".
        [DEBUG] 2024-11-19 15:07:04,561 ceo : Agent: CEO (Default), Action 2/3: I initiated a conversation with Jack, asking him to write the calculated surface area (1017.88) and volume (3053.63) results into a file named 'result.txt'. The result of this action was "None", indicating that no file was created or written to.
        [DEBUG] 2024-11-19 15:07:09,622 ceo : Agent: Tylor, Schedule: ['write_file', 'write_file']. Query: "User's intention: Create or open 'result.txt', write the surface area (1017.88) and volume (3053.63) into it, then save and close the file.".
        [DEBUG] 2024-11-19 15:07:12,482 ceo : Agent: Tylor, Action 1/2: I chose to use the tool to write content to a file. Specifically, I created a file named "result.txt" and wrote the following content to it: "Surface Area: 1017.88\nVolume: 3053.63". The result of this operation was successful, indicated by the output "True".
        [DEBUG] 2024-11-19 15:07:14,954 ceo : Agent: Tylor, Action 2/2: I chose to write content to a file named "result.txt". I wrote the following content to the file: "Surface Area: 1017.88\nVolume: 3053.63". The result of this operation was successful, indicated by the result being "True".
        [DEBUG] 2024-11-19 15:07:16,748 ceo : Agent: Tylor, Conclusion: Your intention is to create or open 'result.txt', write the surface area (1017.88) and volume (3053.63) into it, then save and close the file. I have successfully achieved your intention by creating the file and writing the specified content into it. The content written was: "Surface Area: 1017.88\nVolume: 3053.63". The operation was successful, so your request has been fulfilled.
        [DEBUG] 2024-11-19 15:07:21,079 ceo : Agent: CEO (Default), Action 3/3: I initiated a conversation with Tylor, an AI agent, to request the creation of a file named 'result.txt' that would contain the calculated surface area and volume values. Specifically, I asked Tylor to write the surface area (1017.88) and volume (3053.63) results into this file. 

        The result of this operation was that Tylor successfully created the file and wrote the specified content into it. The content written was: "Surface Area: 1017.88\nVolume: 3053.63". The operation was confirmed to be successful, fulfilling my request.

        {the_choice_you_made}: {'query': "Write the calculated surface area (1017.88) and volume (3053.63) results into a file named 'result.txt'."}, {what_you_have_done}: I instructed Tylor to create a file and write the surface area and volume into it, which was successfully completed.
        [DEBUG] 2024-11-19 15:07:23,699 ceo : Agent: CEO (Default), Conclusion: Your intention is to calculate the surface area and volume of a sphere with a radius of 9 using the formulas \( A = 4\pi r^2 \) and \( V = \frac{4}{3}\pi r^3 \), and then write the results to 'result.txt'. 

        I successfully calculated the surface area as approximately 1017.88 and the volume as approximately 3053.63. Additionally, I instructed Tylor to create the file 'result.txt' and write the calculated results into it. This operation was completed successfully.

        Here are the results:
        - Surface Area: 1017.88
        - Volume: 3053.63

        The results have been written to 'result.txt'.
        ```