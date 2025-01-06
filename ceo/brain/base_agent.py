import json
import logging
import warnings
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


class BaseAgent:
    def __init__(self, abilities: list[Callable], brain: BaseChatModel, name: str, query: str = ''):
        self._abilities = list()
        self._act_count = 0
        self._name = name
        self._model = brain
        self._query_high_level = self._query_by_step = str()
        if query is not None and query != '':
            self._query_high_level, self._query_by_step = QueryResolverPrompt(query).invoke(self._model)
        for ability in abilities:
            self._abilities.append(Ability(ability))
        self._introduction = str()
        self.introduce()
        self.__prev_results = list()
        self.__schedule = list()

    @property
    def abilities(self) -> list[Ability]:
        return self._abilities

    @property
    def name(self) -> str:
        return self._name

    @property
    def introduction(self) -> str:
        return self._introduction

    @property
    def brain(self) -> BaseChatModel:
        return self._model

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self):
        return self.__repr__()

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "brain": self._model.dict().get('model_name', 'unknown'),
            "abilities": [ability.to_dict() for ability in self._abilities]
        }

    def introduce(self, update: bool = False) -> str:
        if self._introduction == '' or update:
            self._introduction = SelfIntroducePrompt(agent=self).invoke(self._model)
        return self._introduction

    def grant_ability(self, ability: Callable, update_introduction: bool = True):
        self._abilities.append(Ability(ability))
        self.introduce(update_introduction)

    def grant_abilities(self, abilities: list[Callable]):
        for ability in abilities:
            self.grant_ability(ability, update_introduction=False)
        self.introduce(update=True)

    def deprive_ability(self, ability: Callable, update_introduction: bool = True):
        ability = Ability(ability)
        for _ability in self._abilities:
            if _ability.name == ability.name:
                self._abilities.remove(_ability)
        self.introduce(update_introduction)

    def deprive_abilities(self, abilities: list[Callable]):
        for ability in abilities:
            self.deprive_ability(ability, update_introduction=False)
        self.introduce(update=True)

    def plan(self, _log: bool = True) -> list:
        scheduling = SchedulerPrompt(query=self._query_by_step, abilities=self._abilities)
        self.__schedule = scheduling.invoke(self._model)
        if _log:
            log.debug(f'Agent: {self._name}; Schedule: {[_.name for _ in self.__schedule]}; Query: "{self._query_high_level}";')
        return self.__schedule

    def reposition(self):
        self.__prev_results = list()
        self.__schedule = list()
        self._act_count = 0
        return self

    def assign(self, query: str):
        self._query_high_level, self._query_by_step = (
            QueryResolverPrompt(query=query).invoke(self._model))
        return self.reposition()

    def reassign(self, query: str):
        return self.assign(query)

    def __step_quiet(self) -> str:
        if self._act_count < len(self.__schedule):
            analysing = AnalyserPrompt(
                query=self._query_by_step,
                prev_results=self.__prev_results,
                action=self.__schedule[self._act_count]
            )
            action, params = analysing.invoke(self._model)
            executing = ExecutorPrompt(params=params, action=action)
            action_str = f'Agent: {self._name}; Action {self._act_count + 1}/{len(self.__schedule)}: {executing.invoke(model=self._model)};'
            self.__prev_results.append(action_str)
            self._act_count += 1
            log.debug(action_str)
            return action_str
        self.reposition()
        return ''

    def just_do_it(self) -> str | None:
        warnings.warn(
            "This function is deprecated and will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2
        )
        if not self.plan():
            return None
        for act_count in range(len(self.__schedule)):
            self.__step_quiet()
        response = IntrospectionPrompt(
            query=self._query_high_level,
            history=self.__prev_results
        ).invoke(self._model)
        log.debug(f'Agent: {self._name}; Conclusion: {response};')
        self.reposition()
        return f'{self._name}: {response}'
