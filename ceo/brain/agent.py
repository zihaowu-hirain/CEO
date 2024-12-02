import json
import logging
import random
import datetime
from typing import Callable, override

from langchain_core.language_models import BaseChatModel

from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.brain.base_agent import BaseAgent
from ceo.brain.memory_augment import MemoryAugment
from ceo.prompt import (
    NextMovePrompt,
    ExecutorPrompt,
    IntrospectionPrompt
)

log = logging.getLogger('ceo')


class Agent(BaseAgent, MemoryAugment):
    def __init__(self, abilities: list[Callable],
                 brain: BaseChatModel, name: str,
                 p: float, beta: float,
                 query: str = '', memory: dict | None = None):
        BaseAgent.__init__(self, abilities=abilities, brain=brain, name=name, query=query)
        MemoryAugment.__init__(self, memory=memory)
        self.__expected_step = 0
        self._p = p  # (0, 1)
        self._beta = beta  # (0, MAX)
        self.__base_p = p

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
    def bring_in_memory(self, memory: dict):
        self._memory.update(memory)
        return self

    @override
    def reposition(self):
        BaseAgent.reposition(self)
        self._memory = dict()
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
    def just_do_it(self) -> dict:
        self.estimate_step()
        stop = False
        while True:
            if self._act_count > self.__expected_step:
                stop = self.stop()
                self.punish()
            _history = json.dumps(self._memory, ensure_ascii=False)
            next_move = False
            if not stop:
                next_move = NextMovePrompt(
                    query=self._query_by_step,
                    abilities=self._abilities,
                    history=_history
                ).invoke(self._model)
                if not isinstance(next_move, bool):
                    action, params = next_move
                    if action.name.startswith(AGENTIC_ABILITY_PREFIX):
                        params['memory'] = self._memory
                    self.memorize(ExecutorPrompt(params=params, action=action).invoke(model=self._model))
                    self._act_count += 1
                    continue
            response = IntrospectionPrompt(
                query=self._query_high_level,
                prev_results=_history,
            ).invoke(self._model)
            self.reposition()
            log.debug(f'Agent: {self._name}, Conclusion: {response}')
            return {
                "success": next_move,
                "response": response
            }

    def assign_with_memory(self, query: str, memory: dict):
        return self.assign(query).bring_in_memory(memory)

    def estimate_step(self):
        if self._query_by_step == '':
            self.__expected_step = 0
            return
        self.__expected_step = len(self.plan(_log=False))
        log.debug(f'Agent: {self._name}; Expected steps: {self.__expected_step}; Query: "{self._query_high_level}".')

    def memorize(self, action_performed: str):
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        new_memory = {
            "date_time": now,
            "agent_name": self._name,
            f"message_from_{self._name}": action_performed
        }
        self._memory[f"{self._name} at {now}"] = new_memory
        log.debug(f'Agent: {self._name}, Memory update: {new_memory}')

    def stop(self) -> bool:
        log.debug(f'Agent: {self._name}, Termination Probability(p): {self._p}')
        if random.uniform(0, 1) > self._p:
            return False
        return True

    def punish(self):
        self._p = (self._beta * self._p) % 1.0
