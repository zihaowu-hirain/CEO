import logging

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class QueryResolverPrompt(Prompt):
    def __init__(self, query: str, ext_context: str = ''):
        prompt = (f'Precondition: There is a user query: "{query}"\n'
                  "Task: What you need to do is to tell user's intention based on user query. "
                  "(Break user's intention down into several minimum steps)\n"
                  'Output format: Step[n]:[Action of the step]\n'
                  'Example output: Step1:Open the door;Step2:Go into the room;Step3:Find the toys in the room;\n')
        self.__query = query
        super().__init__(prompt, ext_context)
        log.debug(f'QueryResolverPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> tuple[str, str]:
        if self.__query == '':
            return f"User's intention: Don't do anything.", f"User's query(Step by step): Don't do anything."
        user_query_by_step = model.invoke(self.prompt).content
        summary_prompt = ("Task: Summarize user's query into a sentence (Which includes all the key information)\n"
                          f"User's query by step: \"{user_query_by_step}\"\n"
                          "Output format: string\n"
                          "Output example: To find toys for you in the room.\n")
        summary = model.invoke(summary_prompt).content
        return f"User's intention: {summary}", f"User's query(Step by step): {user_query_by_step}"
