import json
import logging
import random
import datetime
from typing import Callable, override

from langchain_core.language_models import BaseChatModel

from ceo.brain.agent import Agent
from ceo.prompt import (
    NextMovePrompt,
    ExecutorPrompt,
    IntrospectionPrompt
)

log = logging.getLogger('ceo')


class AdaptiveAgent(Agent):
    def __init__(self, abilities: list[Callable],
                 brain: BaseChatModel, name: str,
                 p: float, beta: float, query: str = ''):
        super().__init__(abilities=abilities, brain=brain, name=name, query=query)
        self._memory = dict()  # json
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
    def reposition(self):
        super().reposition()
        self._memory = dict()
        self.__expected_step = 0
        self._p = self.__base_p
        return self

    @override
    def assign(self, query: str):
        super().assign(query)
        self.reposition()

    @override
    def reassign(self, query: str):
        return self.assign(query)

    @override
    def just_do_it(self) -> dict:
        while True:
            _history = json.dumps(self._memory, ensure_ascii=False)
            next_move = NextMovePrompt(
                query=self._query_by_step,
                abilities=self._abilities,
                history=_history
            ).invoke(self._model)
            if not isinstance(next_move, bool):
                action, params = next_move
                executing = ExecutorPrompt(params=params, action=action)
                self.memorize(executing.invoke(model=self._model))
                continue
            response = IntrospectionPrompt(
                query=self._query_high_level,
                prev_results=_history,
            ).invoke(self._model)
            log.debug(f'Agent: {self._name}, Conclusion: {response}')
            return {
                "success": next_move,
                "response": response
            }

    def estimate_step(self):
        if self._query_by_step == '':
            self.__expected_step = 0
            return
        self.__expected_step = len(self.plan(_log=False))

    def memorize(self, action_performed: str):
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        agent_name = f'Agent {self._name}'
        new_memory = {
            "date_time": now,
            "action_executor": agent_name,
            f"message_from_{self._name}": action_performed
        }
        self._memory[agent_name] = new_memory
        log.debug(f'Agent: {self._name}, Memory update: {new_memory}')

    def stop(self) -> bool:
        if random.uniform(0, 1) > self._p:
            return False
        return True

    def punish(self):
        self._p = (self._beta * self._p) % 1.0
