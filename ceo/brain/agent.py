import json
import logging
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo.ability.ability import Ability
from ceo.prompt import (
    SchedulerPrompt,
    AnalyserPrompt,
    ExecutorPrompt,
    IntrospectionPrompt,
    QueryResolverPrompt,
    SelfIntroducePrompt
)

log = logging.getLogger('ceo')


class Agent:
    def __init__(self, abilities: list[Callable], brain: BaseChatModel, name: str, query: str = ''):
        self.abilities = list()
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0
        self.name = name
        self.model = brain
        self.query_high_level = self.query_by_step = str()
        if query is not None and query != '':
            self.query_high_level, self.query_by_step = QueryResolverPrompt(query).invoke(self.model)
        for ability in abilities:
            self.abilities.append(Ability(ability))
        self.introduction = str()
        self.introduce()

    def __repr__(self):
        ability_str = '['
        for ability in self.abilities:
            ability_str += f'{ability}, '
        ability_str = ability_str[:-2] + ']'
        if ability_str == ']':
            ability_str = '[]'
        schedule_str = '['
        for ability in self.schedule:
            schedule_str += f'{ability.name}, '
        schedule_str = schedule_str[:-2] + ']'
        if schedule_str == ']':
            schedule_str = '[]'
        return json.dumps({
            self.name: {
                "name": self.name,
                "brain": self.model.dict()['model_name'],
                "abilities": ability_str,
                "schedule": schedule_str
            }
        }, ensure_ascii=False)

    def __str__(self):
        return self.__repr__()

    def introduce(self, update: bool = False) -> str:
        if self.introduction == '' or update:
            self.introduction = SelfIntroducePrompt(agent=self).invoke(self.model)
        return self.introduction

    def grant_ability(self, ability: Callable, update_introduction: bool = True):
        self.abilities.append(Ability(ability))
        self.introduce(update_introduction)

    def grant_abilities(self, abilities: list[Callable]):
        for ability in abilities:
            self.grant_ability(ability, update_introduction=False)
        self.introduce(update=True)

    def deprive_ability(self, ability: Callable, update_introduction: bool = True):
        ability = Ability(ability)
        for _ability in self.abilities:
            if _ability.name == ability.name:
                self.abilities.remove(_ability)
        self.introduce(update_introduction)

    def deprive_abilities(self, abilities: list[Callable]):
        for ability in abilities:
            self.deprive_ability(ability, update_introduction=False)
        self.introduce(update=True)

    def plan(self, _log: bool = True) -> list:
        scheduling = SchedulerPrompt(query=self.query_by_step, abilities=self.abilities)
        self.schedule = scheduling.invoke(self.model)
        if _log:
            log.debug(f'Agent: {self.name}, Schedule: {[_.name for _ in self.schedule]}. Query: "{self.query_high_level}".')
        return self.schedule

    def reposition(self):
        self.prev_results = list()
        self.schedule = list()
        self.act_count = 0
        return self

    def assign(self, query: str):
        self.query_high_level, self.query_by_step = (
            QueryResolverPrompt(query=query).invoke(self.model))
        return self.reposition()

    def reassign(self, query: str):
        return self.assign(query)

    def step_quiet(self) -> str:
        if self.act_count < len(self.schedule):
            analysing = AnalyserPrompt(
                query=self.query_by_step,
                prev_results=self.prev_results,
                action=self.schedule[self.act_count]
            )
            action, params = analysing.invoke(self.model)
            executing = ExecutorPrompt(params=params, action=action)
            action_str = f'Agent: {self.name}, Action {self.act_count + 1}/{len(self.schedule)}: {executing.invoke(model=self.model)}'
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
        response = IntrospectionPrompt(
            query=self.query_high_level,
            prev_results=self.prev_results,
        ).invoke(self.model)
        log.debug(f'Agent: {self.name}, Conclusion: {response}')
        self.reposition()
        return f'{self.name}: {response}'
