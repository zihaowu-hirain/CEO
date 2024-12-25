import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class IntrospectionPrompt(Prompt):
    def __init__(self, query: str, prev_results: list | str, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": "Below are actions you (you are the bot/assistant) have performed "
                            "to achieve the <user_query>. "
                            "You are talking to the user (I (who now talking to you here) am the user), "
                            "use 'you' instead of the 'user' when you organize your response (output).",
            "user_query": query,
            "task": "Tell user's intention first, "
                    "then think seriously whether you have achieved the user's query "
                    "according to actions you have performed. "
                    "Finally, provide the results wanted by the user based on <user_query>. "
                    "If you did not achieve the user's query, explain why?",
            "output_format": "text",
            "output_example": "Your intention is to calculate math, and I was trying to open calculator. "
                              "But I failed because I did not have that ability to open calculator. "
                              "I have not achieved your intention.",
            "hint_for_output": "Your output should be concise and comprehensive",
            "actions_performed": prev_results if isinstance(prev_results, str) else str(prev_results)
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'IntrospectionPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
