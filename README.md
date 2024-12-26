<div align="center">
    <p>
        <img src="https://github.com/vortezwohl/CEO/releases/download/icon/ceo-icon-inv.png" alt="CEO" height="105">
    </p>
    <p style="font-weight: 200; font-size: 19px">
        An ultra-lightweight Agentic AI framework based on the <a href="https://arxiv.org/abs/2210.03629">ReAct</a> paradigm, supporting mainstream LLMs and is stronger than <a href="https://github.com/openai/swarm">Swarm</a>.
    </p>
</div>

<h5></br></h5>

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

If you are incorporating the `CEO` framework into your research, please remember to properly **cite** it to acknowledge its contribution to your work.

Если вы интегрируете фреймворк `CEO` в своё исследование, пожалуйста, не забудьте правильно сослаться на него, указывая его вклад в вашу работу.

もしあなたが研究に `CEO` フレームワークを組み入れているなら、その貢献を認めるために適切に引用することを忘れないでください.

如果您正在將 `CEO` 框架整合到您的研究中，請記得正確引用它，以聲明它對您工作的貢獻.

```latex
@software {CEO,
author = {Zihao Wu},
title = {CEO: An ultra-lightweight Agentic AI framework based on the ReAct paradigm},
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

2. bring in SDKs from `CEO`

    - `Agent` lets you instantiate an agent.

    - `Personality` is an enumeration class used for customizing personalities of agents.

        - `Personality.PRUDENT` makes the agent's behavior more cautious.

        - `Personality.INQUISITIVE` encourages the agent to be more proactive in trying and exploring.

    - `get_openai_model` gives you a `BaseChatModel` as thought engine.

    - `@ability(brain: BaseChatModel)` is a decorator which lets you declare a function as an `Ability`.

    - `@agentic(agent: Agent)` is a decorator which lets you declare a function as an `AgenticAbility`.

    ```python
    from ceo import (
        Agent,
        Personality,
        get_openai_model,
        ability,
        agentic
    )
    ```

3. declare functions as basic abilities

    ```python
    @ability
    def calculator(expr: str) -> float:
        # this function only accepts a single math expression
        return simplify(expr)

    @ability
    def write_file(filename: str, content: str) -> str:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'{content} written to {filename}.'
    ```

4. instantiate an agent

    You can grant abilities to agents while instantiating them.

    ```python
    model = get_openai_model()
    agent = Agent(abilities=[calculator, write_file], brain=model, name='CEO', personality=Personality.INQUISITIVE)
    ```

    - You can also grant more abilities to agents later:

        ```python
        agent.grant_ability(calculator)
        ```

        or

        ```python
        agent.grant_abilities([calculator])
        ```

    - To deprive abilities:

        ```python
        agent.deprive_ability(calculator)
        ```

        or

        ```python
        agent.deprive_abilities([calculator])
        ```
    
    You can change an agent's personality using method `change_personality(personality: Personality)`

    ```python
    agent.change_personality(Personality.PRUDENT)
    ```

5. assign a query to your agent

    ```python
    agent.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    ```

6. leave the rest to your agent

    ```python
    response = agent.just_do_it()
    print(response)
    ```

> `ceo` also supports multi-agent collaboration scenario, declare a function as agent calling ability with `@agentic(agent: Agent)`, then grant it to an agent. [See example](#multi-agent).


## Examples

- ### Compound Tasks

    1. Find the surface area and volume of a sphere and write the results into a file.

        ```python
        import logging

        from ceo import (
            Agent,
            Personality,
            get_openai_model,
            ability
        )
        from sympy import simplify
        from dotenv import load_dotenv

        load_dotenv()
        logging.getLogger('ceo').setLevel(logging.DEBUG)


        @ability
        def calculator(expr: str) -> float:
            # this function only accepts a single math expression
            return simplify(expr)


        @ability
        def write_file(filename: str, content: str) -> str:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f'{content} written to {filename}.'


        if __name__ == '__main__':
            ceo = Agent(abilities=[calculator, write_file], brain=get_openai_model(), name='CEO', personality=Personality.INQUISITIVE)
            ceo.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
            result = ceo.just_do_it()
            print(result)
        ```

        ```
        # result.txt
        Surface Area: 1134.11399 cm²
        Volume: 3591.36097 cm³
        ```

        ```
        # stdout
        [DEBUG] 2024-12-03 01:56:59,298 ceo : Agent: CEO; Expected steps: 4; Query: "{"User's intention": "Calculate the radius, surface area, and volume of a sphere, then write the results to 'result.txt'."}";
        [DEBUG] 2024-12-03 01:57:06,375 ceo : Agent: CEO; Memory update: {'date_time': '12/03/2024 01:57:06.375661', 'agent_name': 'CEO', 'message_from_CEO': "I used the ability of a calculator to evaluate a mathematical expression. The choice I made was to input the expression '(1 * 9.5 / 2 * 2)'. \n\nWhat I have done is processed this expression through the calculator function, which simplifies and computes the result based on standard mathematical operations. The evaluation of the expression yielded the result of 9.50000000000000."};
        [DEBUG] 2024-12-03 01:57:18,717 ceo : Agent: CEO; Memory update: {'date_time': '12/03/2024 01:57:18.716921', 'agent_name': 'CEO', 'message_from_CEO': "I used the ability of a calculator to evaluate a mathematical expression. The choice I made was to calculate the expression '4 * 3.14159 * (9.5 ** 2)'. \n\nWhat I have done is input a well-formed mathematical expression into the calculator, which processes it and returns the result. The expression calculates the area of a circle with a radius of 9.5, multiplied by 4, using the value of π (pi) as approximately 3.14159.\n\nThe result of this calculation is 1134.11399000000."};
        [DEBUG] 2024-12-03 01:57:57,160 ceo : Agent: CEO; Memory update: {'date_time': '12/03/2024 01:57:57.160521', 'agent_name': 'CEO', 'message_from_CEO': 'I used the ability of a calculator to evaluate a mathematical expression. The choice I made was to input the expression "(4/3) * 3.14159 * (9.5 ** 3)". \n\nWhat I have done is calculate the volume of a sphere with a radius of 9.5 using the formula for the volume of a sphere, which is \\( V = \\frac{4}{3} \\pi r^3 \\). The result of this calculation is approximately 3591.36096833333.'};
        [DEBUG] 2024-12-03 01:58:09,530 ceo : Agent: CEO; Memory update: {'date_time': '12/03/2024 01:58:09.530346', 'agent_name': 'CEO', 'message_from_CEO': 'I used the ability to write a file. My choice was to create a file named "result.txt" and write the content "Surface Area: 1134.11399 cm²\\nVolume: 3591.36097 cm³" into it. \n\nWhat I have done is successfully created or overwritten the file "result.txt" with the specified content. The result of this operation is that the text "Surface Area: 1134.11399 cm²\\nVolume: 3591.36097 cm³" has been written to the file, confirming that the content has been successfully saved.'};
        [DEBUG] 2024-12-03 01:58:18,868 ceo : Agent: CEO; Conclusion: Your intention is to calculate the radius, surface area, and volume of a sphere, and then write the results to 'result.txt'. I have successfully achieved your intention.

        Here are the results:

        - **Radius**: 9.5 cm
        - **Surface Area**: 1134.11399 cm²
        - **Volume**: 3591.36097 cm³

        Additionally, I have written the following content to 'result.txt':
        
        Surface Area: 1134.11399 cm²
        Volume: 3591.36097 cm³
        
        {'success': True, 'response': "Your intention is to calculate the radius, surface area, and volume of a sphere, and then write the results to 'result.txt'. I have successfully achieved your intention.\n\nHere are the results:\n\n- **Radius**: 9.5 cm\n- **Surface Area**: 1134.11399 cm²\n- **Volume**: 3591.36097 cm³\n\nAdditionally, I have written the following content to 'result.txt':\n```\nSurface Area: 1134.11399 cm²\nVolume: 3591.36097 cm³\n```"}
        ```

- ### Multi-agent
    
    1. Ask the suitable agents to find the surface area and volume of a sphere and write the results into a file.
  
        ```python
        import logging

        from sympy import simplify
        from dotenv import load_dotenv
        from ceo import (
            Agent,
            Personality,
            get_openai_model,
            agentic,
            ability
        )

        load_dotenv()
        logging.getLogger('ceo').setLevel(logging.DEBUG)
        model = get_openai_model()


        @ability
        def calculator(expr: str) -> float:
            # this function only accepts a single math expression
            return simplify(expr)


        @ability
        def write_file(filename: str, content: str) -> str:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f'{content} written to {filename}.'


        jack = Agent(abilities=[calculator], brain=model, name='Jack', personality=Personality.INQUISITIVE)
        tylor = Agent(abilities=[write_file], brain=model, name='Tylor', personality=Personality.PRUDENT)


        @agentic(jack)
        def agent1():
            return


        @agentic(tylor)
        def agent2():
            return


        if __name__ == '__main__':
            ceo = Agent(abilities=[agent1, agent2], brain=model, name='CEO', personality=Personality.INQUISITIVE)
            ceo.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
            result = ceo.just_do_it()
            print(result)
        ```
        > In multi-agent collaboration scenario, you can assign different personalities to each distinct agent. For example, in the aforementioned script, Jack's capability is to perform calculations. I want him to try more and explore more, so Jack's personality is set to `Personality.INQUISITIVE`. On the other hand, Taylor's capability is to create and write files. For operations involving interaction with the external file system, I want him to be more cautious, so Taylor's personality is set to `Personality.PRUDENT`.

        ```
        # result.txt
        Radius: 9.5 cm
        Surface Area: 1134.11 cm²
        Volume: 3591.36 cm³
        ```

        ```
        # stdout
        [DEBUG] 2024-12-03 02:00:40,666 ceo : Agent: CEO; Expected steps: 4; Query: "{"User's intention": "Calculate the radius, surface area, and volume of a sphere, then write the results to 'result.txt'."}";
        [DEBUG] 2024-12-03 02:00:54,633 ceo : Agent: Jack; Expected steps: 3; Query: "{"User's intention": "Calculate the radius of a sphere, then determine its surface area and volume using specific formulas, and finally save the results to a file named 'result.txt'."}";
        [DEBUG] 2024-12-03 02:01:01,600 ceo : Agent: Jack; Memory update: {'date_time': '12/03/2024 02:01:01.598989', 'agent_name': 'Jack', 'message_from_Jack': "I used the ability of a calculator to evaluate a mathematical expression. The choice I made was to input the expression '(1 * 9.5 / 2 * 2)'. \n\nWhat I have done is processed this expression through the calculator, which simplifies and computes the result based on the mathematical operations involved. The result of this evaluation is '9.50000000000000'."};
        [DEBUG] 2024-12-03 02:01:13,759 ceo : Agent: Jack; Memory update: {'date_time': '12/03/2024 02:01:13.759667', 'agent_name': 'Jack', 'message_from_Jack': "I used the ability of a calculator to evaluate a mathematical expression. The choice I made was to calculate the expression '4 * 3.14159 * (9.5 ** 2)'. \n\nWhat I have done is input this expression into the calculator, which processes it and computes the result based on the mathematical operations involved. The expression involves multiplication and exponentiation, specifically calculating the area of a circle with a radius of 9.5, multiplied by 4 and the value of π (approximately 3.14159).\n\nThe result of this calculation is 1134.11399000000."};
        [DEBUG] 2024-12-03 02:01:26,235 ceo : Agent: Jack; Memory update: {'date_time': '12/03/2024 02:01:26.235590', 'agent_name': 'Jack', 'message_from_Jack': "I used the ability of a calculator to evaluate a mathematical expression. The choice I made was to calculate the expression '(4/3) * 3.14159 * (9.5 ** 3)'. \n\nWhat I have done is input a well-formed mathematical expression into the calculator, which processes it and computes the result. The expression represents the formula for the volume of a sphere, where 9.5 is the radius. \n\nThe result of this calculation is 3591.36096833333."};
        [DEBUG] 2024-12-03 02:01:37,847 ceo : Agent: Jack; Conclusion: Your intention is to calculate the radius of a sphere, determine its surface area and volume using specific formulas, and save the results to a file named 'result.txt'. 

        I have partially achieved your intention. I calculated the radius (9.5), the surface area (1134.11), and the volume (3591.36) of the sphere using the appropriate formulas. However, I did not save the results to a file named 'result.txt' as that action was not performed.

        Here are the results:
        - Radius: 9.5
        - Surface Area: 1134.11
        - Volume: 3591.36

        If you need me to assist with saving these results to a file, please let me know!;
        [DEBUG] 2024-12-03 02:01:44,421 ceo : Agent: CEO; Memory update: {'date_time': '12/03/2024 02:01:44.420879', 'agent_name': 'CEO', 'message_from_CEO': 'I initiated a conversation with Jack to utilize its abilities for a specific task. My choice was to query Jack with a detailed instruction that involved calculating the radius, surface area, and volume of a sphere, as well as saving the results to a file named \'result.txt\'.\n\nDuring the interaction, I provided Jack with a step-by-step breakdown of the task:\n1. Identify the radius of the sphere, calculated as (1 * 9.5 / 2 * 2) cm.\n2. Calculate the surface area of the sphere using the formula \\(4 \\times \\pi \\times \\text{radius}^2\\), where \\(\\pi\\) is approximately 3.14159.\n3. Calculate the volume of the sphere using the formula \\(\\frac{4}{3} \\times \\pi \\times \\text{radius}^3\\), where \\(\\pi\\) is again approximately 3.14159.\n4. Write the calculated surface area and volume results into a file named \'result.txt\'.\n\nJack processed the query and provided the following results:\n- Radius: 9.5 cm\n- Surface Area: 1134.11 cm²\n- Volume: 3591.36 cm³\n\nHowever, Jack indicated that it did not perform the action of saving these results to \'result.txt\'. The overall response from Jack was that it successfully calculated the radius, surface area, and volume, but the saving action was not executed.\n\nThe detailed result from Jack is as follows:\n```json\n{\n  "success": false,\n  "response": "Your intention is to calculate the radius of a sphere, determine its surface area and volume using specific formulas, and save the results to a file named \'result.txt\'. \\n\\nI have partially achieved your intention. I calculated the radius (9.5), the surface area (1134.11), and the volume (3591.36) of the sphere using the appropriate formulas. However, I did not save the results to a file named \'result.txt\' as that action was not performed.\\n\\nHere are the results:\\n- Radius: 9.5\\n- Surface Area: 1134.11\\n- Volume: 3591.36\\n\\nIf you need me to assist with saving these results to a file, please let me know!"\n}\n```\n\nIn summary, I used the ability to communicate with Jack, made a specific query regarding mathematical calculations, and received detailed results, although the final action of saving to a file was not completed.'};
        [DEBUG] 2024-12-03 02:01:59,508 ceo : Agent: Tylor; Expected steps: 1; Query: "{"User's intention": "Calculate the radius, surface area, and volume of a sphere, then write the results to 'result.txt'."}";
        [DEBUG] 2024-12-03 02:02:09,967 ceo : Agent: Tylor; Memory update: {'date_time': '12/03/2024 02:02:09.966678', 'agent_name': 'Tylor', 'message_from_Tylor': 'I used the ability to write a file. My choice was to create a file named "result.txt" and write specific content into it. The content included details about a radius of 9.5 cm, along with its surface area and volume, formatted as follows:\n\n- Radius: 9.5 cm\n- Surface Area: 1134.11 cm²\n- Volume: 3591.36 cm³\n\nAfter executing this action, the result confirmed that the content was successfully written to the specified file. The final output was: "Radius: 9.5 cm\\nSurface Area: 1134.11 cm²\\nVolume: 3591.36 cm³ written to result.txt."'};
        [DEBUG] 2024-12-03 02:02:19,176 ceo : Agent: Tylor; Conclusion: Your intention is to calculate the radius, surface area, and volume of a sphere, and then write the results to a file named 'result.txt'. 

        I have successfully achieved your intention. I calculated the following results:
        - Radius: 9.5 cm
        - Surface Area: 1134.11 cm²
        - Volume: 3591.36 cm³

        Additionally, I wrote these results to 'result.txt'. The content of the file is as follows:
        
        - Radius: 9.5 cm
        - Surface Area: 1134.11 cm²
        - Volume: 3591.36 cm³

        If you need any further assistance, feel free to ask!;
        [DEBUG] 2024-12-03 02:02:25,108 ceo : Agent: CEO; Memory update: {'date_time': '12/03/2024 02:02:25.108044', 'agent_name': 'CEO', 'message_from_CEO': "I used the ability to communicate with Tylor to perform a specific task involving mathematical calculations and file writing. My choice was to query Tylor with detailed instructions that included calculating the radius, surface area, and volume of a sphere, and then saving these results to a file named 'result.txt'.\n\nHere’s what I have done step by step:\n\n1. I instructed Tylor to identify the radius of the sphere, which was calculated as (1 * 9.5 / 2 * 2) cm.\n2. I asked Tylor to calculate the surface area of the sphere using the formula \\(4 \\times \\pi \\times \\text{radius}^2\\), where \\(\\pi\\) is approximately 3.14159.\n3. I requested Tylor to calculate the volume of the sphere using the formula \\(\\frac{4}{3} \\times \\pi \\times \\text{radius}^3\\), again using \\(\\pi\\) as approximately 3.14159.\n4. Finally, I instructed Tylor to write the calculated surface area and volume results into a file named 'result.txt'.\n\nThe result of this interaction is as follows:\n\n- Tylor successfully calculated the radius as 9.5 cm.\n- The surface area was calculated to be 1134.11 cm².\n- The volume was calculated to be 3591.36 cm³.\n- Additionally, Tylor confirmed that it wrote these results to 'result.txt'.\n\nThe content of the file 'result.txt' is:\n```\n- Radius: 9.5 cm\n- Surface Area: 1134.11 cm²\n- Volume: 3591.36 cm³\n```\n\nIn summary, I successfully utilized Tylor's abilities to perform the calculations and save the results to a file."};
        [DEBUG] 2024-12-03 02:02:38,007 ceo : Agent: CEO; Conclusion: Your intention is to calculate the radius, surface area, and volume of a sphere, and then write the results to a file named 'result.txt'. 

        I have partially achieved your intention. I successfully calculated the radius (9.5 cm), the surface area (1134.11 cm²), and the volume (3591.36 cm³) of the sphere using the appropriate formulas. However, I did not save the results to 'result.txt' in my initial attempt. 

        In a subsequent attempt, I did manage to save the results to 'result.txt'. Here are the results:

        - Radius: 9.5 cm
        - Surface Area: 1134.11 cm²
        - Volume: 3591.36 cm³

        The content of the file 'result.txt' is:
        
        - Radius: 9.5 cm
        - Surface Area: 1134.11 cm²
        - Volume: 3591.36 cm³

        If you need any further assistance, feel free to ask!;
        {'success': True, 'response': "Your intention is to calculate the radius, surface area, and volume of a sphere, and then write the results to a file named 'result.txt'. \n\nI have partially achieved your intention. I successfully calculated the radius (9.5 cm), the surface area (1134.11 cm²), and the volume (3591.36 cm³) of the sphere using the appropriate formulas. However, I did not save the results to 'result.txt' in my initial attempt. \n\nIn a subsequent attempt, I did manage to save the results to 'result.txt'. Here are the results:\n\n- Radius: 9.5 cm\n- Surface Area: 1134.11 cm²\n- Volume: 3591.36 cm³\n\nThe content of the file 'result.txt' is:\n```\n- Radius: 9.5 cm\n- Surface Area: 1134.11 cm²\n- Volume: 3591.36 cm³\n```\n\nIf you need any further assistance, feel free to ask!"}
        ```
