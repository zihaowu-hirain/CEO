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
            prompt[ability.name] = ability.to_dict()
        prompt = json.dumps({
            "precondition": "Below are the <tools(abilities)> you can use "
                            "(you can only use the following <tools(abilities)>). "
                            f'Now there is a <user_query>.',
            "user_query": query,
            "task": "What you need to do is to plan your workflow based on the <tools(abilities)> and <user_query>.",
            "description": "<user_query> might contains many steps, "
                           "think carefully about every step and plan your workflow "
                           "based on your tools in <tools(abilities)>.",
            "hint_for_tool_usage": "<user_query> sometimes need to use one specific tool(s) more than once, "
                                   "you need to estimate as accurately as possible "
                                   "the number of times specific tools need to be used "
                                   "to properly achieve the <user_query>!",
            "hint_for_tool_choosing": "Sometimes some of the tools are irrelevant to <user_query>. "
                                      "Make sure to choose tools properly and wisely.",
            "output_format": "{your_thinking_process}\n"
                             "schedule:{your_schedule_as_a_list_of_tool_names}",
            "hint_for_output": 'firstly, output your thinking process step by step clear and organized.'
                               'secondly, outputs a list(python_list_format) of names of tools, '
                               'surrounded by "[ ]", split by ", ", '
                               'you can refer to <output_example>.',
            "output_example": "1.First, I need to determine which ingredients to purchase, "
                              "which requires checking a recipe or personal preferences to decide.\n"
                              "2.After determining the ingredients, "
                              "I need to go to the market or supermarket to buy the required ingredients.\n"
                              "3.After purchasing the ingredients, I need to bring them home.\n"
                              "4.Once home, I need to wash and prepare the ingredients.\n"
                              "5.After preparation, I start cooking.\n"
                              "6.After cooking is complete, I need to arrange the dishes on the dining table.\n"
                              "schedule:"
                              "[go_to_market, payment_purchase, go_home, do_wash, do_cook, arrange_dished_on_table]",
            "tools(abilities)": prompt
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'SchedulerPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> list[Ability]:
        results = model.invoke(self.prompt).content
        if not results.startswith('['):
            results = results[results.rfind('['):]
        if not results.endswith(']'):
            results = results[:results.rfind(']') + 1]
        results = results[1:-1].split(',')
        _fin_results = list()
        for _a_result in results:
            for ability in self.abilities:
                if ability.name == _a_result.strip():
                    _fin_results.append(ability)
        return _fin_results
