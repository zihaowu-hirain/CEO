import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')

output_example = """
Step 1: In the history, I have identified two events related to the current user query. 
        First, "buying two tomatoes" has been completed, and second, "returning home" has also taken place. 
        These two events are listed in the order they occurred, with the purchase of tomatoes first, followed by returning home.
        
Step 2: Analyzing the user query "Help me buy two tomatoes, 
        then after returning home, use kitchen utensils to cook the tomatoes, 
        and finally place the cooked tomatoes on the dining table." According to the history, 
        we have completed the steps of buying tomatoes and returning home. However, 
        the steps of cooking the tomatoes and placing the cooked tomatoes on the dining table have not yet been carried out.
        
Step 3: Comparing my abilities with the unfinished part of the user query. 
        I possess the abilities "go_home", "do_cook", and "arrange_dished". 
        Since "go_home" has already been completed, it is no longer needed. 
        The "do_cook" ability can be used to cook the tomatoes, 
        and the "arrange_dished" ability can be used to place the cooked tomatoes on the dining table.
        
Step 4: Based on the analysis, I can choose the "do_cook" ability to cook the tomatoes, 
        and then use the "arrange_dished" ability to place the cooked tomatoes on the dining table. 
        These two abilities are the most suitable choices to complete the user's request.
        
Step 5: As I have found abilities that can complete the user's request,
        there is no need for the special ability "-mission-failed-".
        
Step 6: Since the user's request has not been fully completed, 
        there is no need for the special ability "-mission-complete-".

ability: [do_cook]
"""


class NextMovePrompt(Prompt):
    def __init__(self, query: str,
                 abilities: list[Ability], memory: str = '',
                 ext_context: str = ''):
        self.abilities = abilities
        prompt = json.dumps({
            "precondition": "Below are the abilities you have(you can only use the following abilities)."
                            "[history] shows events happened before you. And there is a [user_query].",
            "user_query": f'"{query}"',
            "abilities": self.abilities,
            "history": memory,
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
                    "action": "Choose and provide the most relevant ability as your next move."
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
            "output_format": "{step1_thought_process}\n"
                             "{step2_thought_process}\n"
                             "{step3_thought_process}\n"
                             "{step4_thought_process}\n"
                             "{step5_thought_process}\n"
                             "{step6_thought_process}\n"
                             "ability:[ability.name]",
            "hint_for_ability_choosing": "You can only choose and provide the most relevant ability as your next move.",
            "hint_for_output_format": 'the ability should be after all the thought processes and '
                                      'be surrounded by "[ ]".',
            "output_example": output_example
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'NextMovePrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
