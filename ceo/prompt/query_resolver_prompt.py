import json
import logging

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class QueryResolverPrompt(Prompt):
    def __init__(self, query: str, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": f'There is a user query: "{query}"',
            "task": "What you need to do is to tell user's intention based on [user query].",
            "task_redeclare": "To tell user's intention based on [user query]. Not your (you are the assistant) intention.",
            "additional": "For any details mentioned by the user, you should preserve them in full, "
                          "especially specific information with accuracy requirements such as numbers, dates, etc.",
            "firstly": "Deduce the user's query step by step.",
            "secondly": "Break user's intention down into several minimum steps.",
            "output_format": "Step[n]:[Action of the step]",
            "output_example": "Step1:Open the door;Step2:Go into the room;Step3:Find the toys in the room;"
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
            "task": "Summarize user's query into a short sentence "
                    "which includes all the key information from user's query "
                    "(User's query is provided below at [user's query]).",
            "user_query": f'"{user_query_by_step}".',
            "output_format": "string(summarization of [user's query])",
            "output_example": "To find toys for you in the room."
        }, ensure_ascii=False)
        summary = model.invoke(summary_prompt).content
        return (json.dumps({"User's intention": summary}),
                json.dumps({"User's query (Step by step)": user_query_by_step}))
