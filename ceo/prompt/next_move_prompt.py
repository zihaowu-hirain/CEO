import json
import logging

from langchain_core.language_models import BaseChatModel

from ceo.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')

OUTPUT_EXAMPLE = """
Step 1: In the history, the events that have already occurred include "buying two tomatoes" and "going home." 
        These two events are prerequisites for the user query, indicating that the user has completed the purchase of tomatoes and has returned home. 
        The next steps to complete are to cook the tomatoes using a frying pan and to place the cooked tomatoes on the dining table.

Step 2: The user query is "Help me buy two tomatoes, then after getting home, cook the tomatoes using a frying pan, 
        and finally place the cooked tomatoes on the dining table." According to the history, the first two parts have been completed, 
        but the last two parts (cooking and placing) are still pending. Therefore, the user query has not been fully and properly accomplished.

Step 3: The unfinished parts of the user query are "cook the tomatoes using a frying pan" and "place the cooked tomatoes on the dining table." 
        The abilities I possess include "go_home()", "do_cook(ingredient: str, cooking_utensils: str) -> bool", and "arrange_dished()". 
        Among these, "do_cook" can complete the cooking task, 
        while "arrange_dished" can complete the placing task. Thus, my abilities can fulfill the unfinished parts of the user query.

Step 4: Among my abilities, "do_cook" is the most relevant because it directly pertains to the process of cooking the tomatoes. 
        After selecting this ability, I will use "tomatoes" and "frying pan" as parameters for cooking.

Step 5: This step is not applicable because the user query has not been fully accomplished, 
        and I have the ability to continue progressing.

Step 6: This step is not applicable because the user query has not been fully accomplished.

params:{
  "ingredient": "tomatoes",
  "cooking_utensils": "frying pan"
}

ability:[do_cook]
"""


class NextMovePrompt(Prompt):
    def __init__(self, query: str,
                 abilities: list[Ability], history: str = '',
                 ext_context: str = ''):
        self.abilities = abilities
        if history == '':
            history = "Nothing happened before you."
        prompt = json.dumps({
            "precondition": "Below are the abilities you have(you can only use the following abilities)."
                            "[history] shows events happened before you. And there is a [user_query].",
            "user_query": f'"{query}"',
            "abilities": self.abilities,
            "history": history,
            "instructions_you_must_follow_step_by_step": [{
                    "step": 1,
                    "action": "Find events in the [history] that are related to the current [user_query], "
                              "and list them in the order they occurred by time."
                }, {
                    "step": 2,
                    "action": "Analyse whether the [user_query] has been fully and properly accomplished, "
                              "and provide your analysis process and basis."
                }, {
                    "step": 3,
                    "condition": "If the [user_query] has not been fully properly accomplished",
                    "action": "Analyse whether your [abilities] can complete the unfinished part of the [user_query], "
                              "and provide the basis for your analysis process."
                }, {
                    "step": 4,
                    "condition": "If the [user_query] has not been fully properly accomplished and "
                                 "there is an ability in your [abilities] "
                                 "that can further advance the accomplishment of the [user_query]",
                    "action": "Choose and provide the most relevant ability as your next move"
                              "(only one single ability can be chosen), "
                              "and comprehensively explain your next move.",
                    "after_you_have_chosen_the_one_most_relevant_ability_as_next_move":
                        "Generate values of parameters for the ability(function) to achieve [next move]. "
                        "Before you generate values of parameters, explain why you give these values to params.",
                }, {
                    "step": 5,
                    "condition": "If the [user_query] has not been fully properly accomplished and "
                                 "there is no ability in your [abilities] "
                                 "that can further advance the accomplishment of the [user_query]",
                    "action": 'Provide a special ability called "-mission-failed-" (which is not a real ability).'
                }, {
                    "step": 6,
                    "condition": "If the [user_query] has been fully properly accomplished",
                    "action": 'Provide a special ability called "-mission-complete-" (which is not a real ability).'
                }
            ],
            "output_format": "{step1_thought_process}\n{step2_thought_process}\n"
                             "{step3_thought_process}\n{step4_thought_process}\n"
                             "{step5_thought_process}\n{step6_thought_process}\n"
                             'params:{'
                             '{name_of_param_1}:{value_for_param_1},'
                             '{name_of_param_2}:{value_for_param_2},'
                             '{name_of_param_...}:{value_for_param_...}'
                             '}\n'
                             "ability:[ability.name]",
            "hint_for_thought_process_output": "Thought processes of all steps(from 1 to 6) should be output.",
            "hint_for_ability_choosing": "You can only choose and provide the most relevant one ability as your next move."
                                         "Only one single ability can be chosen.",
            "hint_for_params_output_format": 'The params should be after all the thought processes and before the ability. '
                                             'The params should be formatted as json.'
                                             'The params only gives the params for the chosen one ability.',
            "hint_for_ability_output_format": 'The ability should be after the params. '
                                              'The ability name should be surrounded by "[ ]".',
            "output_example": OUTPUT_EXAMPLE
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'NextMovePrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> tuple[Ability, dict] | bool:
        result: str = model.invoke(self.prompt).content
        ability_name: str = result[result.rfind('['):][:result.rfind(']') + 1].strip()[1:-1]
        params: dict = json.loads(result[result.rfind('{'):][:result.rfind('}') + 1].strip())
        if ability_name.__contains__('-mission-complete-'):
            return True
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability, params
        return False
