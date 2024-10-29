import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class IntrospectionPrompt(Prompt):
    def __init__(self, query: str, prev_results: list, ext_context: str = ''):
        prompt = ('Precondition: Below are actions you(the bot/assistant) have performed to achieve the user query. '
                  'You are talking to the user, use "you" instead of the "user", '
                  'and you are the assistant.\n'
                  f'User query: "{query}"\n'
                  "Task: tell user's intention first, "
                  "then think seriously whether you have achieve user's query based on actions you have performed. "
                  '(If you did not achieve, explain why?)\n'
                  'Output format: text.\n'
                  'Example output: Your intention is to calculate math, and I was trying to open calculator. '
                  'But i failed because i did not have that ability to open calculator. '
                  'I have not achieve your intention.\n'
                  f'Actions You Have Performed (from left to right): {prev_results}\n')
        super().__init__(prompt, ext_context)
        log.debug(f'IntrospectionPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
