import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class IntrospectionPrompt(Prompt):
    def __init__(self, query: str, history: dict | list, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": "Below in <history> are actions have been performed to achieve <query>. ",
            "query": query,
            "task": "Think step by step whether <query> has been fully achieved "
                    "according to <history> and <query>. "
                    "Then, provide the detailed results mentioned in <history> accurately. "
                    "Finally, if the <query> has not been fully achieved, explain why failed?",
            "output_datatype": "text",
            "output_example": "Your intention is to do calculation, and I was trying to open calculator. "
                              "But I failed because I did not have that ability to open calculator. "
                              "I have not achieved your intention.",
            "hint_1_for_output": "Provide thought process (briefly and concisely) before opinion and conclusion.",
            "hint_2_for_output": "Output should be concise, accurate, and short enough.",
            "history": history
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'IntrospectionPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
