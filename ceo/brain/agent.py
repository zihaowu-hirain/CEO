from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from ceo.action.action import Action
from ceo.prompt import generate_decision_prompt, generate_response_prompt


class Agent:
    def __init__(self, query: str, action: Action, model: BaseChatModel):
        self.query: str = query
        self.action: Action = action
        self.model: BaseChatModel = model
        self.chain_to_decide = self.model | JsonOutputParser()
        self.chain_to_respond = self.model | StrOutputParser()

    def decide(self):
        prompt = generate_decision_prompt(self.query, self.action)
        param = self.chain_to_decide.invoke(prompt)
        if param != {}:
            return True, self.action.invoke_formatted(**param)
        else:
            return False, None

    def respond(self):
        prompt = generate_response_prompt(self.query, self.decide()[1])
        return self.chain_to_respond.invoke(prompt)
