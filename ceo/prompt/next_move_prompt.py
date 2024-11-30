import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


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
                    "action": "Provide this ability."
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
            "hint_for_output_format": 'the ability should be after all the thought processes and '
                                      'be surrounded by "[ ]".',
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'NextMovePrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
