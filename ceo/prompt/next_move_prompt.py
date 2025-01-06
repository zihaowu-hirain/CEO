import json
import logging

from langchain_core.language_models import BaseChatModel

from ceo.ability import Ability
from ceo.prompt.prompt import Prompt
from ceo.exception.too_dumb_exception import TooDumbException

log = logging.getLogger('ceo.prompt')

SEPARATOR = '--SEP--'
END = '--END--'
MISSION_COMPLETE = '-mission-complete-'
MISSION_FAILED = '-mission-failed-'

OUTPUT_EXAMPLE = """
Step 1: In the provided history, the events related to the user's query are as follows, listed chronologically:
    1. The user calculated the radius of the sphere using the expression "(3 * 174.9 / 15.9 * 2.77)", resulting in a radius of approximately 91.41 cm.
    2. The user then calculated the surface area of the sphere using the formula "4 * 3.14159 * (91.41^2)", resulting in a surface area of approximately 105001.841348316 cm².
    From the history, we extract the following information related to the user's query:
    1. The radius of the sphere has been successfully calculated as 91.41 cm.
    2. The surface area has been calculated as approximately 105001.84 cm².
    3. However, the volume of the sphere has not yet been calculated, and there is no record of writing the results into the file 'result.txt'.
    Based on these details, the subsequent steps to complete are:
    1. Calculate the volume of the sphere using the formula "(4/3) * pi * radius^3".
    2. Write the results of the surface area and volume into a file called 'result.txt'.
Step 2: The user query is to find the area and volume of a sphere with a specific radius and write the results into a file. 
    According to the history, the radius and surface area have been calculated, but the volume calculation and file writing have not been completed. 
    Therefore, the user query has not been fully and properly accomplished.
Step 3: The unfinished parts of the user query are the calculation of the volume and writing the results to 'result.txt'. 
    The abilities I possess include "calculator" for performing calculations and "write_file" for writing content to a file. Both abilities can fulfill the unfinished parts of the user query.
Step 4: Since the user's query is not fully accomplished, and I have the ability to calculate the volume and write to a file, my next move is to calculate the volume of the sphere. 
    I will use the "calculator" ability with the expression "(4/3) * 3.14159 * (91.41^3)" to compute the volume, as this aligns with the user's request to find the volume of the sphere.
    After calculating the volume, I will then write both the surface area and volume results into 'result.txt' using the "write_file" ability.
Step 5: This step is not applicable because the user query has not been fully accomplished, and I have the ability to continue progressing.
Step 6: This step is not applicable because the user query has not been fully accomplished.

""" + SEPARATOR + """
params:{
  "{name_of_param}": "(4/3) * 3.14159 * (91.41^3)"
}
ability:[calculator]
""" + END


class NextMovePrompt(Prompt):
    def __init__(self, query: str,
                 abilities: list[Ability],
                 history: dict | None = None,
                 ext_context: str = ''):
        self.abilities = abilities
        abilities_dict: dict = dict()
        for ability in self.abilities:
            abilities_dict[ability.name] = ability.to_dict()
        if history in ('', '[]', '()', '{}', {}, [], (), None):
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
                             '"{name_of_param_1}":{value_for_param_1},'
                             '"{name_of_param_2}":{value_for_param_2},'
                             '"{name_of_param_...}":{value_for_param_...}'
                             '}\n'
                             f'ability:[ability.name]\n{END}',
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
            "hint_for_end_pattern": f'The "{END}" pattern marks the end of your whole response, '
                                    f'no more words are allowed after "{END}" pattern. '
                                    f'The "{END}" pattern is absolutely important, do not forget to place it '
                                    'in the end of your response.',
            "hint_for_ability_output_format": 'The ability should be after the params. '
                                              'The ability name should be surrounded by "[ ]".',
            "output_example": OUTPUT_EXAMPLE,
            "hint_for_output": 'You must strictly follow the format in <output_format>! '
                               'You should refer to example in <output_example>!'
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'NextMovePrompt: {self.prompt}')

    # noinspection PyUnusedLocal
    def invoke(self, model: BaseChatModel, max_retry: int = 5) -> tuple[Ability, dict] | bool:
        result: str = str()
        count: int = 0
        exclamation = '!'
        tmp_prompt = self.prompt
        while True:
            # noinspection DuplicatedCode
            if count > 0:
                if count <= max_retry:
                    log.warning(f'NextMovePromptWarn: incorrectly formatted. Retry: {count}')
                else:
                    log.warning(f'NextMovePromptWarn: max retry exceeded.')
                    raise TooDumbException(model)
            count += 1
            result = model.invoke(tmp_prompt).content
            log.debug(f"Next move thought process: \n{result}")
            _accurate_action_str = result[result.rfind(SEPARATOR) + len(SEPARATOR):result.rfind(END)]
            if (result.count(SEPARATOR) == 1
                    and result.count(END) == 1
                    and _accurate_action_str.count('ability:') == 1
                    and _accurate_action_str.count('params:') == 1):
                break
            tmp_prompt = (f'{self.prompt}\nAttention_{count}: '
                          f'You must strictly follow the format in <output_format>{count * 2 * exclamation} '
                          f'You should refer to example in <output_example>{count * 2 * exclamation}')
        result = _accurate_action_str
        params = json.loads(result[result.find('{'):result.rfind('}') + 1].strip())
        result = result[result.rfind('}') + 1:]
        ability_name: str = result[result.find('['):result.rfind(']') + 1].strip()[1:-1]
        if ability_name.__contains__(MISSION_COMPLETE):
            return True
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability, params
        return False
