import json
import logging

from langchain_core.language_models import BaseChatModel

from ceo.ability.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class SchedulerPrompt(Prompt):
    def __init__(self, query: str, abilities: list[Ability], ext_context: str = ''):
        self.abilities = abilities
        prompt = dict()
        for ability in self.abilities:
            prompt[ability.name] = str(ability)
        prompt = json.dumps({
            "precondition": "Below are the tools you can use (you can only use the following tools). "
                            f'Now there is a user query: "{query}".',
            "task": "What you need to do is to plan your workflow based on the [tools] and [user query].",
            "description": "User query might contains many steps, "
                           "think carefully about every step and plan your workflow based on your tools.",
            "hint_for_tool_usage": "User's query might need to use one tool more than once, "
                                   "but think carefully about how many times a tool needs to be used "
                                   "based on the practical user query, "
                                   "do not abuse or overuse any tool!",
            "hint_for_tool_choosing": "Sometimes some of the tools are irrelevant to user's query. "
                                      "Make sure to choose tools properly and wisely.",
            "output_format": "Sequential and well-organized with no additional redundant information",
            "hint_for_output_format": 'Outputs a list of names of tools, surrounded by "[ ]", split by ", ", '
                                      'you should refer to [example_output].',
            "output_example": "[tool_a.name, tool_b.name, tool_c.name, tool_d.name]",
            "tools": f"{json.dumps(prompt, ensure_ascii=False)}"
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'SchedulerPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> list[Ability]:
        results = model.invoke(self.prompt).content
        if not results.startswith('['):
            results = results[results.find('['):]
        if not results.endswith(']'):
            results = results[:results.find(']') + 1]
        results = results[1:-1].split(',')
        _fin_results = list()
        for _a_result in results:
            for ability in self.abilities:
                if ability.name == _a_result.strip():
                    _fin_results.append(ability)
        return _fin_results
