import logging
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo.action.action import Action
from ceo.prompt import (
    SchedulerPrompt,
    AnalyserPrompt,
    ExecutorPrompt,
    IntrospectionPrompt,
    QueryResolverPrompt
)

log = logging.getLogger('ceo')


class Agent:
    def __init__(self, functions: list[Callable], model: BaseChatModel, query: str, ext_context: str = ''):
        self.actions = list()
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0
        self.model = model
        self.ext_context = ext_context
        self.query_high_level, self.query_by_step = (
            QueryResolverPrompt(query=query, ext_context=ext_context).invoke(self.model))
        for function in functions:
            self.actions.append(Action(function))

    def plan(self) -> list:
        scheduling = SchedulerPrompt(query=self.query_by_step, actions=self.actions, ext_context=self.ext_context)
        self.schedule = scheduling.invoke(self.model)
        log.debug(f'Schedule: {[_.name for _ in self.schedule]}. Query: "{self.query_high_level}".')
        return self.schedule

    def reposition(self):
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0
        return self

    def assign(self, query: str):
        self.query_high_level, self.query_by_step = (
            QueryResolverPrompt(query=query, ext_context=self.ext_context).invoke(self.model))
        return self.reposition()

    def reassign(self, query: str):
        return self.assign(query=query)

    def step_quiet(self) -> str:
        if self.act_count < len(self.schedule):
            analysing = AnalyserPrompt(
                query=self.query_by_step,
                prev_results=self.prev_results,
                action=self.schedule[self.act_count],
                ext_context=self.ext_context
            )
            action, params = analysing.invoke(self.model)
            executing = ExecutorPrompt(params=params, action=action, ext_context=self.ext_context)
            action_str = f'Action {self.act_count + 1}/{len(self.schedule)}: {executing.invoke(model=self.model)}'
            self.prev_results.append(action_str)
            self.act_count += 1
            log.debug(action_str)
            return action_str
        self.reposition()
        return ''

    def just_do_it(self) -> str | None:
        if not self.plan():
            return None
        for act_count in range(len(self.schedule)):
            self.step_quiet()
        response = (IntrospectionPrompt(
            query=self.query_high_level,
            prev_results=self.prev_results,
            ext_context=self.ext_context).invoke(self.model))
        log.debug(f'Conclusion: {response}')
        self.reposition()
        return response
