import hashlib
import inspect
import json
import logging
import random
import time
import warnings
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo.ability.ability import Ability
from ceo.prompt import (
    SchedulerPrompt,
    AnalyserPrompt,
    ExecutorPrompt,
    IntrospectionPrompt,
    RequestResolverPrompt,
    SelfIntroducePrompt
)

log = logging.getLogger('ceo')


class BaseAgent:
    def __init__(self, abilities: list[Callable], brain: BaseChatModel, name: str = '', request: str = ''):
        self._abilities = list()
        self._act_count = 0
        self._name = name
        self._model = brain
        self._request = self._request_by_step = str()
        if request is not None and request != '':
            self._request, self._request_by_step = RequestResolverPrompt(request).invoke(self._model)
        if self._name is None or len(self._name) < 1:
            self._name = self._generate_name()
        self.__prev_results = list()
        self.__schedule = list()
        self._introduction = str()
        self.grant_abilities(abilities)

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

    def _generate_name(self) -> str:
        __abilities_ls = [ability.to_dict() for ability in self.abilities]
        __tmp_bytes = f'{__abilities_ls}{time.time()}{random.uniform(0, 10 ** 3)}'.encode('utf-8')
        __tmp_str = hashlib.md5(__tmp_bytes).hexdigest()
        __sample_str = ''.join(random.sample(__tmp_str, 6))
        return f'智能體{__sample_str}型號'

    def to_dict(self) -> dict:
        __model_dict = self._model.dict()
        model_name = __model_dict.get('model_name', __model_dict.get('_type', 'unknown'))
        return {
            "name": self.name,
            "brain": model_name,
            "abilities": [ability.to_dict() for ability in self.abilities]
        }

    def introduce(self, update: bool = False) -> str:
        if self._introduction == '' or update:
            self._introduction = SelfIntroducePrompt(agent=self).invoke(self._model)
        return self._introduction

    def grant_ability(self, ability: Callable, update_introduction: bool = True):
        for _ability in self.abilities:
            if inspect.getsource(ability) == inspect.getsource(_ability.function):
                return
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
        scheduling = SchedulerPrompt(request=self._request_by_step, abilities=self._abilities)
        self.__schedule = scheduling.invoke(self._model)
        if _log:
            log.debug(f'Agent: {self._name}; Schedule: {[_.name for _ in self.__schedule]}; Request: "{self._request}";')
        return self.__schedule

    def reposition(self):
        self.__prev_results = list()
        self.__schedule = list()
        self._act_count = 0
        return self

    def assign(self, request: str):
        self._request, self._request_by_step = (
            RequestResolverPrompt(request=request).invoke(self._model))
        return self.reposition()

    def reassign(self, request: str):
        return self.assign(request)

    def relay(self, request: str, request_by_step: str):
        self._request = request
        self._request_by_step = request_by_step
        return self.reposition()

    def __step_quiet(self) -> str:
        if self._act_count < len(self.__schedule):
            combined_request = {
                'raw_request': self._request,
                'request_by_step': self._request_by_step
            }
            analysing = AnalyserPrompt(
                request=combined_request,
                prev_results=self.__prev_results,
                action=self.__schedule[self._act_count]
            )
            action, args = analysing.invoke(self._model)
            executing = ExecutorPrompt(args=args, action=action)
            action_str = (f'Agent: {self._name}; Action {self._act_count + 1}/{len(self.__schedule)}: '
                          f'{json.dumps(executing.invoke(model=self._model), ensure_ascii=False)};')
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
        brief_conclusion, response = IntrospectionPrompt(
            request=self._request,
            history=self.__prev_results
        ).invoke(self._model)
        log.debug(f'Agent: {self._name}; Conclusion: {brief_conclusion};')
        self.reposition()
        return f'{self._name}: {response}'
