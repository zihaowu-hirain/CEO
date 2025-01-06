import json
import logging

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class QueryResolverPrompt(Prompt):
    def __init__(self, query: str, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": 'There is a user query shown below at <user_query>',
            "user_query": query,
            "task": "What you need to do is to tell user's intention based on <user_query>.",
            "additional_important": "For any details mentioned in <user_query>, you should preserve them in full, "
                                    "especially specific information with accuracy requirements "
                                    "such as all numbers occur, parameter, location, "
                                    "date/time, name, proper noun, entity, etc...",
            "hint_for_thinking": "Deduce and analyse the <user_query> step by step. "
                                 "Keep track of the steps' interdependence and orderliness.",
            "output_format": {
                "step_{n}": "(Condition) {action_of_step_{n}}"
            },
            "hint_1_for_output": "Break user's intention(s) down into multiple minimum steps as granular as possible. "
                                 "Keep track of the steps' interdependence and orderliness again.",
            "hint_2_for_output": 'You must strictly follow the format in <output_format>! '
                                 'You can refer to example in <output_example>!',
            "output_example": {
                "step_1": "(Start) Open the door",
                "step_2": "(After: door opened) Go into the room",
                "step_3": "(After: walked in the room) Find the toys in the room",
                "step_...": "(After: found toys)..."
            }
        }, ensure_ascii=False)
        self.__query = query
        super().__init__(prompt, ext_context)
        log.debug(f'QueryResolverPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> tuple[str, str]:
        _dont_do_anything = "Don't do anything."
        if self.__query == '':
            return _dont_do_anything, _dont_do_anything
        user_query_by_step = (f'raw_query: "{self.__query}"\n'
                              f'query_by_step: "{model.invoke(self.prompt).content}"')
        summary_prompt = json.dumps({
            "task": "Summarize <user_query> into a short sentence "
                    "which includes all the key information from <user_query>.",
            "user_query": user_query_by_step,
            "output_format": "string (summarization of <user_query>)",
            "output_example": "To find toys for you in the room."
        }, ensure_ascii=False)
        summary = model.invoke(summary_prompt).content
        return summary, user_query_by_step
