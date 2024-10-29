import logging
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo.action.action import Action
from ceo.prompt import SchedulerPrompt, AnalyserPrompt, ExecutorPrompt, IntrospectionPrompt

log = logging.getLogger('ceo')


class Agent:
    def __init__(self, functions: list[Callable], model: BaseChatModel):
        self.actions = list()
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0
        self.model = model
        for function in functions:
            self.actions.append(Action(function))

    def plan(self, query: str) -> list:
        scheduling = SchedulerPrompt(query=query, actions=self.actions)
        self.schedule = scheduling.invoke(self.model)
        log.debug(f'Schedule: {[_.name for _ in self.schedule]}. Query: "{query}".')
        return self.schedule

    def renew(self):
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0

    def step_quiet(self, query: str) -> list:
        if self.act_count < len(self.schedule):
            analysing = AnalyserPrompt(
                query=query,
                prev_results=self.prev_results,
                action=self.schedule[self.act_count]
            )
            action, params = analysing.invoke(self.model)
            executing = ExecutorPrompt(params=params, action=action)
            self.prev_results.append(executing.invoke(model=self.model))
            self.act_count += 1
            log.debug(f'Action {self.act_count}/{len(self.schedule)}: {self.prev_results[-1]}')
            return self.prev_results
        self.renew()
        return self.prev_results

    def just_do_it(self, query: str) -> str | None:
        if not self.plan(query=query):
            return None
        for act_count in range(len(self.schedule)):
            self.step_quiet(query=query)
        response = IntrospectionPrompt(query=query, prev_results=self.prev_results).invoke(self.model)
        log.debug(f'Conclusion: {response}')
        self.renew()
        return response
