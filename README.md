<div align="center">
    <p>
        <img src="https://github.com/vortezwohl/CEO/releases/download/icon/ceo-icon-inv.png" alt="CEO" height="105">
    </p>
    <p style="font-weight: 200; font-size: 19px">
        An ultra-lightweight agentic AI framework based on the <a href="https://arxiv.org/abs/2210.03629">ReAct</a> paradigm, supporting mainstream LLMs and is stronger than <a href="https://github.com/openai/swarm">Swarm</a>.
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
title = {CEO: An ultra-lightweight agentic AI framework based on the ReAct paradigm},
publisher = {Github},
howpublished = {\url{https://github.com/vortezwohl/CEO-Agentic-AI-Framework}},
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
            radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
            pi = 3.14159
            output_file = 'result.txt'
            query = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
            result = ceo.assign(query).just_do_it()  # area = 95910378.2949379, volume = 88322713378.13666
            print(result)
        ```

        ```
        # result.txt
        Surface Area: 95910378.29 cm², Volume: 88322713378.14 cm³
        ```

        ```
        # stdout
        [DEBUG] 2025-01-10 00:47:01,702 ceo : Agent: CEO; Expected steps: 4; Query: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-10 00:47:12,923 ceo : Agent: CEO; Memory size: 1; Memory update: I used the calculator ability to evaluate the expression '(10.01 * 10.36 * 3.33 / 2 * 16)', and the result shows '2762.66390400000', which indicates the computed value of the expression.;
        [DEBUG] 2025-01-10 00:47:21,705 ceo : Agent: CEO; Memory size: 2; Memory update: I used the calculator ability to evaluate the expression '4 * 3.14159 * (2762.66390400000^2)', and the result shows '95910378.2949379', which indicates the calculated value of the expression.;
        [DEBUG] 2025-01-10 00:47:32,679 ceo : Agent: CEO; Memory size: 3; Memory update: I used the calculator ability to evaluate the expression '(4/3) * 3.14159 * (2762.663904^3)', and the result shows '88322713378.1367', which indicates the computed volume of a sphere with the given radius.;
        [DEBUG] 2025-01-10 00:47:51,210 ceo : Agent: CEO; Memory size: 4; Memory update: I used the write_file ability to write the content 'Surface Area: 95910378.29 cm², Volume: 88322713378.14 cm³' to the file named 'result.txt'. The result confirms that the content has been successfully written to the specified file.;
        [DEBUG] 2025-01-10 00:48:04,048 ceo : Agent: CEO; Step count: 4; Time used: 66.80771009996533 seconds;
        {'success': True, 'response': "To assess whether the <query> has been fully achieved, I will outline the recorded actions from <history> and compare them to the <query>:\n\n1. **Calculating the Radius**: The CEO calculated the expression `(10.01 * 10.36 * 3.33 / 2 * 16)` and obtained the radius value of `2762.66390400000` cm.\n2. **Calculating Surface Area**: The CEO then calculated the surface area using the formula `4 * π * r²`, resulting in `95910378.2949379 cm²`.\n3. **Calculating Volume**: The CEO calculated the volume using the formula `(4/3) * π * r³`, resulting in `88322713378.1367 cm³`.\n4. **Writing to File**: Finally, the CEO wrote the results into a file named `result.txt`, confirming that the content 'Surface Area: 95910378.29 cm², Volume: 88322713378.14 cm³' was successfully written.\n\nConclusion: Based on the above assessment, the <query> has been fully achieved. All steps, including calculations for surface area and volume, as well as writing the results to the specified file, were completed successfully.\n\n--END--", 'misc': {'time_used': 66.80771009996533, 'step_count': 4}}
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
            radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
            pi = 3.14159
            output_file = 'result.txt'
            query = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
            result = ceo.assign(query).just_do_it()  # area = 95910378.2949379, volume = 88322713378.13666
            print(result)
        ```

        > In multi-agent collaboration scenario, you can assign different personalities to each distinct agent. For example, in the aforementioned script, Jack's capability is to perform calculations. I want him to try more and explore more, so Jack's personality is set to `Personality.INQUISITIVE`. On the other hand, Taylor's capability is to create and write files. For operations involving interaction with the external file system, I want him to be more cautious, so Taylor's personality is set to `Personality.PRUDENT`.

        ```
        # result.txt
        Surface Area: 95910378.2949379 cm²
        Volume: 88322713378.1367 cm³
        ```

        ```
        # stdout
        [DEBUG] 2025-01-10 00:44:29,502 ceo : Agent: CEO; Expected steps: 4; Query: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-10 00:44:39,414 ceo : Agent: Jack; Memory brought in: 0;
        [DEBUG] 2025-01-10 00:44:43,504 ceo : Agent: Jack; Expected steps: 3; Query: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-10 00:44:52,277 ceo : Agent: Jack; Memory size: 1; Memory update: I used the calculator ability to evaluate the expression '(10.01 * 10.36 * 3.33 / 2 * 16)', and the result shows '2762.66390400000', which indicates the simplified result of the mathematical calculation.;
        [DEBUG] 2025-01-10 00:45:12,044 ceo : Agent: Jack; Memory size: 2; Memory update: I used the calculator ability to evaluate the expression '4 * 3.14159 * (2762.66390400000^2)', and the result shows '95910378.2949379', which indicates the calculated value of the mathematical expression.;
        [DEBUG] 2025-01-10 00:45:26,512 ceo : Agent: Jack; Memory size: 3; Memory update: I used the calculator ability to evaluate the expression '(4/3) * 3.14159 * (2762.66390400000^3)', and the result shows '88322713378.1367', which indicates the calculated volume of a sphere with a radius of approximately 2762.66.;
        [DEBUG] 2025-01-10 00:45:40,782 ceo : Agent: Jack; Step count: 3; Time used: 61.36751270014793 seconds;
        [DEBUG] 2025-01-10 00:45:48,740 ceo : Agent: CEO; Memory size: 1; Memory update: I initiated a conversation with Jack to ask for a favor. However, the result indicates failure, as the calculations for the radius, surface area, and volume were completed, but the final step of writing the results to 'result.txt' was not recorded.;
        [DEBUG] 2025-01-10 00:46:00,920 ceo : Agent: Tylor; Memory brought in: 1;
        [DEBUG] 2025-01-10 00:46:07,284 ceo : Agent: Tylor; Expected steps: 1; Query: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-10 00:46:24,339 ceo : Agent: Tylor; Memory size: 2; Memory update: I used the write_file ability to write the specified content about surface area and volume to the file named 'result.txt'. The result confirms that the content was successfully written to the file.;
        [DEBUG] 2025-01-10 00:46:40,338 ceo : Agent: Tylor; Step count: 1; Time used: 39.416911099804565 seconds;
        [DEBUG] 2025-01-10 00:46:47,927 ceo : Agent: CEO; Memory size: 2; Memory update: I used the __AgenticAbility__talk_to_Tylor ability to ask Tylor for a favor, which involved assessing the completion of a query related to calculations and file writing. The result indicates that all tasks were successfully completed, including calculations for radius, surface area, and volume, and the results were written to 'result.txt'.;
        [DEBUG] 2025-01-10 00:47:02,209 ceo : Agent: CEO; Step count: 2; Time used: 155.96004600008018 seconds;
        {'success': True, 'response': "To assess whether the <query> has been fully achieved, I will outline the recorded actions from <history> and compare them to the <query>:\n\n1. **Calculating the Radius**: The expression for the radius was evaluated as \\( (10.01 * 10.36 * 3.33 / 2 * 16) \\), resulting in approximately \\( 2762.663904 \\) cm. This was successfully calculated.\n\n2. **Calculating the Surface Area**: The surface area of the sphere was calculated using the formula \\( 4 * \\pi * r^2 \\), where \\( r \\) is the radius. The calculation yielded approximately \\( 95910378.2949379 \\) cm².\n\n3. **Calculating the Volume**: The volume of the sphere was calculated using the formula \\( \\frac{4}{3} * \\pi * r^3 \\), resulting in approximately \\( 88322713378.1367 \\) cm³.\n\n4. **Writing Results to File**: Initially, there was no record of writing the calculated area and volume into a file called 'result.txt'. However, Tylor later confirmed that the content was successfully written to the file.\n\nConclusion: Based on the above assessment, the <query> has been fully achieved. All calculations were completed, and the results were successfully written to 'result.txt'. \n--END--", 'misc': {'time_used': 155.96004600008018, 'step_count': 2}}
        ```
