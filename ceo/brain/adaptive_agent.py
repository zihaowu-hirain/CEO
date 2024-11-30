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
        self.memory = dict()  # json
        self.expected_step = 0
        self.p = p  # (0, 1)
        self.beta = beta  # (0, MAX)
        self.__origin_p = p

    def estimate_step(self):
        if self.query_by_step == '':
            self.expected_step = 0
            return
        self.expected_step = len(self.plan(_log=False))

    def memorize(self, action_performed: str):
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        agent_name = f'Agent {self.name}'
        self.memory[agent_name] = {
            "action_executor": agent_name,
            f"message_from_{self.name}": action_performed,
            "date_time": now
        }

    def stop(self) -> bool:
        if random.uniform(0, 1) > self.p:
            return False
        return True

    def punish(self):
        self.p = (self.beta * self.p) % 1.0

    @override
    def reposition(self):
        super().reposition()
        self.memory = dict()
        self.expected_step = 0
        self.p = self.__origin_p
        return self

    @override
    def assign(self, query: str):
        super().assign(query)
        self.reposition()

    @override
    def reassign(self, query: str):
        return self.assign(query)

    @override
    def step_quiet(self) -> str | None:
        pass

    @override
    def just_do_it(self) -> dict:
        while True:
            _history = json.dumps(self.memory, ensure_ascii=False)
            next_move = NextMovePrompt(
                query=self.query_by_step,
                abilities=self.abilities,
                history=_history
            ).invoke(self.model)
            if not isinstance(next_move, bool):
                action, params = next_move
                executing = ExecutorPrompt(params=params, action=action)
                self.memorize(executing.invoke(model=self.model))
            return {
                "success": next_move,
                "response": IntrospectionPrompt(
                    query=self.query_high_level,
                    prev_results=_history,
                ).invoke(self.model)
            }
