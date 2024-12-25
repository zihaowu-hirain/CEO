import json
import logging

from langchain_core.language_models import BaseChatModel

from ceo.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')

SEPARATOR = '--SEP--'
MISSION_COMPLETE = '-mission-complete-'
MISSION_FAILED = '-mission-failed-'

OUTPUT_EXAMPLE = """
Step 1: In the provided history, the events related to the user's query are as follows, listed chronologically:
        1. Buying two tomatoes: This event is the first in the sequence and is directly related to the user's query as it involves the acquisition of the main ingredient needed for the subsequent steps.
        2. Going home: Following the purchase, the user returns home, which is a necessary step before proceeding with the cooking process.
        
        From the history, we extract the following information related to the user's query:
        1. The user has successfully completed the purchase of tomatoes.
        2. The user is now at home, which is the location where the next steps of the process will take place.
        
        Based on these details, the subsequent steps to complete are:
        1. Cook the tomatoes using a frying pan.
        2. Place the cooked tomatoes on the dining table.

Step 2: The user query is "Help me buy two tomatoes, then after getting home, cook the tomatoes using a frying pan, 
        and finally place the cooked tomatoes on the dining table." According to the history, the first two parts have been completed, 
        but the last two parts (cooking and placing) are still pending. Therefore, the user query has not been fully and properly accomplished.

Step 3: The unfinished parts of the user query are "cook the tomatoes using a frying pan" and "place the cooked tomatoes on the dining table." 
        The abilities I possess include "go_home()", "do_cook(ingredient: str, cooking_utensils: str) -> bool", and "arrange_dished()". 
        Among these, "do_cook" can complete the cooking task, 
        while "arrange_dished" can complete the placing task. Thus, my abilities can fulfill the unfinished parts of the user query.

Step 4: Since the user's query is not fully accomplished, and I have the ability to cook and arrange dishes, 
        my next move is to cook the tomatoes. I will use the "do_cook" ability with "tomatoes" as the ingredient and "frying pan" as the cooking utensil 
        because these parameters align with the user's request to cook the tomatoes using a frying pan.

Step 5: This step is not applicable because the user query has not been fully accomplished, 
        and I have the ability to continue progressing.

Step 6: This step is not applicable because the user query has not been fully accomplished.

""" + SEPARATOR + """

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
        abilities_dict: dict = dict()
        for ability in self.abilities:
            abilities_dict[ability.name] = ability.to_dict()
        if history in ('', '[]', '()', '{}', {}, []):
            history = "Nothing happened before you."
        prompt = json.dumps({
            "precondition": "Below are the abilities you have(you can only use the following abilities)."
                            "<history> shows events happened before you. And there is a <user_query>.",
            "user_query": query,
            "abilities": abilities_dict,
            "history": history,
            "instructions_you_must_follow_step_by_step": [{
                    "step": 1,
                    "first_action": "List all events in the <history> related to <user_query> "
                                    "respectively and chronologically.",
                    "second_action": "Extract and list all key information related to <user_query> from <history> "
                                     "formatted one by one respectively.",
                    "additional": "For any details mentioned in <history> about <user_query>, "
                                  "you should preserve them in full, "
                                  "especially specific information with accuracy requirements "
                                  "such as numbers, dates, etc."
                }, {
                    "step": 2,
                    "action": "Analyse whether the <user_query> has been fully and properly accomplished "
                              "according to your report in <step_1>, "
                              "and provide your analysis process and basis."
                }, {
                    "step": 3,
                    "condition": "If the <user_query> has not been fully properly accomplished",
                    "action": "Analyse whether your <abilities> can complete the unfinished part of the <user_query>, "
                              "and provide the basis according to your report in <step_1>."
                }, {
                    "step": 4,
                    "condition": "If the <user_query> has not been fully properly accomplished and "
                                 "there is an ability in your <abilities> "
                                 "that can further advance the accomplishment of the <user_query> based on <history>.",
                    "first_action": "Plan and explain your next move based on <history> "
                                    "for further advancing the <user_query>.",
                    "second_action": "Choose and provide the ability according to your next move"
                                     "(only one single ability can be chosen)",
                    "third_action": "After you have chosen the ability as next move, "
                                    "generate values of parameters for the ability(function) to achieve <next move>, "
                                    "before you generate values of parameters, "
                                    "explain why you give these values to params.",
                }, {
                    "step": 5,
                    "condition": "If the <user_query> has not been fully properly accomplished and "
                                 "there is no ability in your <abilities> "
                                 "that can further advance the accomplishment of the <user_query>",
                    "action": f'Provide a special ability called "{MISSION_FAILED}" (which is not a real ability).'
                }, {
                    "step": 6,
                    "condition": "If the <user_query> has been fully and properly accomplished "
                                 "according to <history> and <user_query>",
                    "action": f'Provide a special ability called "{MISSION_COMPLETE}" (which is not a real ability).'
                }
            ],
            "output_format": "{step1_thought_process}\n{step2_thought_process}\n"
                             "{step3_thought_process}\n{step4_thought_process}\n"
                             "{step5_thought_process}\n{step6_thought_process}\n"
                             f"{SEPARATOR}\n"
                             'params:{'
                             '{name_of_param_1}:{value_for_param_1},'
                             '{name_of_param_2}:{value_for_param_2},'
                             '{name_of_param_...}:{value_for_param_...}'
                             '}\n'
                             "ability:[ability.name]",
            "hint_for_thought_process_output": "Thought processes of all steps(from 1 to 6) should be output.",
            "hint_for_ability_choosing": "Only one single ability can be chosen.",
            "hint_for_params_output_format": f'The "{SEPARATOR}" pattern should be after '
                                             f'all the thought processes and before the <params and ability>.'
                                             f'The params should be after the "{SEPARATOR}" pattern.'
                                             'The params should be formatted as json.'
                                             'The params only gives the params for the chosen one ability.'
                                             'The ability should be after params.',
            "hint_for_separation_pattern": f'The "{SEPARATOR}" pattern which separates <thought processes> and '
                                           '<params and ability> is absolutely important, do not forget to place it.',
            "hint_for_ability_output_format": 'The ability should be after the params. '
                                              'The ability name should be surrounded by "[ ]".',
            "output_example": OUTPUT_EXAMPLE
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'NextMovePrompt: {self.prompt}')

    # noinspection PyUnusedLocal
    def invoke(self, model: BaseChatModel, stream: bool = False) -> tuple[Ability, dict] | bool:
        result: str = str()
        count: int = 0
        while True:
            if count > 0:
                log.warning(f'NextMovePromptWarn: incorrectly formatted. Retry: {count}')
            count += 1
            result = model.invoke(self.prompt).content
            log.debug(f"Next move thought process: \n{result}")
            if not result.count(SEPARATOR) == 1:
                self.prompt = (f'{self.prompt} Attention: do not forget to output a {SEPARATOR} '
                               f'before the <params and ability>, '
                               f'and do not output more than one {SEPARATOR}.')
                continue
            result = result[result.rfind(SEPARATOR):]
            if result.count('ability:') == 1 and result.count('params:') == 1:
                break
            self.prompt = (f'{self.prompt} Attention: '
                           'You can only provide the ability to be used in the next step,'
                           ' and only one ability can be provided for the next step.')
        params = json.loads(result[result.find('{'):result.rfind('}') + 1].strip())
        result = result[result.rfind('}') + 1:]
        ability_name: str = result[result.find('['):result.rfind(']') + 1].strip()[1:-1]
        if ability_name.__contains__(MISSION_COMPLETE):
            return True
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability, params
        return False
