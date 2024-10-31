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
DEFAULT_NAME = 'CEO (Default)'


class Agent:
    def __init__(self, abilities: list[Callable], brain: BaseChatModel, name: str = DEFAULT_NAME, query: str = '', ext_context: str = ''):
        self.actions = list()
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0
        self.name = name
        self.model = brain
        self.ext_context = ext_context
        self.query_high_level, self.query_by_step = (
            QueryResolverPrompt(query=query, ext_context=ext_context).invoke(self.model)
        )
        for ability in abilities:
            self.actions.append(Action(ability))

    def __repr__(self):
        actions_str = '['
        for action in self.actions:
            actions_str += f'{action.name}, '
        actions_str = actions_str[:-2] + ']'
        if actions_str == ']':
            actions_str = '[]'
        schedule_str = '['
        for action in self.schedule:
            schedule_str += f'{action.name}, '
        schedule_str = schedule_str[:-2] + ']'
        if schedule_str == ']':
            schedule_str = '[]'
        ext_context = self.ext_context
        if ext_context == '':
            ext_context = 'None'
        return (f'Agent: \n'
                f'- Name: {self.name}\n'
                f'- Brain: {self.model.dict()['model_name']}\n'
                f'- Abilities: {actions_str}\n'
                f'- Schedule: {schedule_str}\n'
                f'- ExternalContext: {ext_context}')

    def __str__(self):
        return self.__repr__()

    def grant_ability(self, ability: Callable):
        self.actions.append(Action(ability))

    def grant_abilities(self, abilities: list[Callable]):
        for ability in abilities:
            self.grant_ability(ability)

    def deprive_ability(self, ability: Callable):
        action = Action(ability)
        for _action in self.actions:
            if _action.name == action.name:
                self.actions.remove(_action)

    def deprive_abilities(self, abilities: list[Callable]):
        for ability in abilities:
            self.deprive_ability(ability)

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
        return f'{self.name}: response'
