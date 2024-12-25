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
            "task_redeclare": "To tell user's intention based on <user_query>. "
                              "Not your intention (you are the user's assistant).",
            "additional": "For any details mentioned in <user_query>, you should preserve them in full, "
                          "especially specific information with accuracy requirements such as numbers, dates, etc.",
            "hint_for_thinking": "Deduce and analyse the <user_query> step by step. "
                                 "Keep track of the steps' interdependence and orderliness.",
            "output_format (json)": {
                "step_{n}": "{action_of_step_{n}}"
            },
            "hint_for_output": "Break user's intention(s) down into multiple minimum steps as granular as possible. "
                               "Keep track of the steps' interdependence and orderliness again.",
            "output_example": {
                "step_1": "Open the door",
                "step_2": "(Door opened) Go into the room",
                "step_3": "(Walked in the room) Find the toys in the room",
                "step_...": "(Found toys)..."
            }
        }, ensure_ascii=False)
        self.__query = query
        super().__init__(prompt, ext_context)
        log.debug(f'QueryResolverPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> tuple[str, str]:
        if self.__query == '':
            return (json.dumps({"User's intention": "Don't do anything."}),
                    json.dumps({"User's query (Step by step)": "Don't do anything."}))
        user_query_by_step = model.invoke(self.prompt).content
        summary_prompt = json.dumps({
            "task": "Summarize <user_query> into a short sentence "
                    "which includes all the key information from <user_query>.",
            "user_query": user_query_by_step,
            "output_format": "string (summarization of <user_query>)",
            "output_example": "To find toys for you in the room."
        }, ensure_ascii=False)
        summary = model.invoke(summary_prompt).content
        return (json.dumps({"User's intention": summary}),
                json.dumps({"User's query (Step by step)": user_query_by_step}))
