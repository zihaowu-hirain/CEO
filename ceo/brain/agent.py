import copy
import hashlib
import json
import logging
import random
import datetime
from typing import Callable
from typing_extensions import override
from collections import OrderedDict

from langchain_core.language_models import BaseChatModel

from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.brain.base_agent import BaseAgent
from ceo.brain.memory_augment import MemoryAugment
from ceo.enum.Personality import Personality
from ceo.prompt import (
    NextMovePrompt,
    ExecutorPrompt,
    IntrospectionPrompt
)

PRUDENT_P = 0.25
PRUDENT_BETA = 1.45
INQUISITIVE_P = 0.05
INQUISITIVE_BETA = 1.25
log = logging.getLogger('ceo')


class Agent(BaseAgent, MemoryAugment):
    def __init__(self, abilities: list[Callable],
                 brain: BaseChatModel, name: str,
                 personality: Personality = Personality.PRUDENT,
                 query: str = '', memory: OrderedDict | None = None):
        BaseAgent.__init__(self, abilities=abilities, brain=brain, name=name, query=query)
        MemoryAugment.__init__(self, memory=memory)
        self.__expected_step = 0
        if personality == Personality.PRUDENT:
            self._p = self.__base_p = PRUDENT_P
            self._beta = PRUDENT_BETA
        elif personality == Personality.INQUISITIVE:
            self._p = self.__base_p = INQUISITIVE_P
            self._beta = INQUISITIVE_BETA

    @property
    def p(self) -> float:
        return self._p

    @property
    def base_p(self) -> float:
        return self.__base_p

    @property
    def beta(self) -> float:
        return self._beta

    @override
    def bring_in_memory(self, memory: OrderedDict):
        self._memory.update(memory)
        log.debug(f'Agent: {self._name}; '
                  f'Memory brought in: {len(memory.keys())};')
        return self

    @override
    def reposition(self):
        BaseAgent.reposition(self)
        self._memory = OrderedDict()
        self.__expected_step = 0
        self._p = self.__base_p
        return self

    @override
    def assign(self, query: str):
        BaseAgent.assign(self, query)
        return self.reposition()

    @override
    def reassign(self, query: str):
        return self.assign(query)

    @override
    def relay(self, query: str, query_by_step: str):
        self._query = query
        self._query_by_step = query_by_step
        return self.reposition()

    @override
    def just_do_it(self) -> dict:
        self.estimate_step()
        stop = False
        while True:
            if self._act_count > self.__expected_step:
                stop = self.stop()
                self.penalize()
            next_move = False
            if not stop:
                combined_query = {
                    'raw_query': self._query,
                    'query_by_step': self._query_by_step
                }
                next_move = NextMovePrompt(
                    query=combined_query,
                    abilities=self._abilities,
                    history=self.memory
                ).invoke(self._model)
                if not isinstance(next_move, bool):
                    action, params = next_move
                    if action.name.startswith(AGENTIC_ABILITY_PREFIX):
                        params = {
                            'query': self._query,
                            'query_by_step': self._query_by_step,
                            'memory': self.memory
                        }
                    self.memorize(ExecutorPrompt(params=params, action=action).invoke(model=self._model))
                    self._act_count += 1
                    continue
            response = IntrospectionPrompt(
                query=self._query,
                history=self.memory
            ).invoke(self._model)
            self.reposition()
            # log.debug(f'Agent: {self._name}; Conclusion: {response};')
            return {
                "success": next_move,
                "response": response
            }

    def assign_with_memory(self, query: str, memory: OrderedDict):
        return self.assign(query).bring_in_memory(memory)

    def estimate_step(self):
        if self._query_by_step == '':
            self.__expected_step = 0
            return
        self.__expected_step = len(self.plan(_log=False))
        log.debug(f'Agent: {self._name}; '
                  f'Expected steps: {self.__expected_step}; '
                  f'Query: "{self._query}";')

    def memorize(self, action_performed: dict):
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        _action_performed = copy.deepcopy(action_performed)
        _tmp_summarization = _action_performed['summarization']
        del _action_performed['summarization']
        _tmp_action_performed = _action_performed
        if _tmp_action_performed['ability'].startswith(AGENTIC_ABILITY_PREFIX):
            if 'choice' in _tmp_action_performed.keys():
                _tmp_action_performed['choice'] = 'Ask for a favor.'
        new_memory = {
            "timestamp": now,
            "agent_name": self._name,
            f"message_from_{self._name}": _tmp_summarization,
            f'action_performed_by_{self._name}': _tmp_action_performed
        }
        mem_hash = hashlib.md5(json.dumps(new_memory, ensure_ascii=False).encode()).hexdigest()
        self._memory[f"agent:[{self._name}] at:[{now}] hash:[{mem_hash}]"] = new_memory
        log.debug(f'Agent: {self._name}; Memory size: {len(self._memory.keys())}; Memory update: {_tmp_summarization};')

    def stop(self) -> bool:
        resample = 3
        log.debug(f'Agent: {self._name}; Termination Probability(p): {self._p}; Penalty Rate(beta): {self._beta};')
        rand_sum = 0.0
        for i in range(resample):
            rand_sum += random.uniform(0, 1)
        rand_avg = rand_sum / resample
        if rand_avg > self._p:
            return False
        return True

    def penalize(self):
        self._p = (self._beta * self._p) % 1.0

    def set_penalty(self, p: float, beta: float):
        self._p = self.__base_p = p
        self._beta = beta
        return self

    def change_personality(self, personality: Personality):
        if personality == Personality.PRUDENT:
            return self.set_penalty(p=PRUDENT_P, beta=PRUDENT_BETA)
        elif personality == Personality.INQUISITIVE:
            return self.set_penalty(p=INQUISITIVE_P, beta=INQUISITIVE_BETA)
