import json
import logging
from typing import override

from ceo.brain.base_agent import BaseAgent
from ceo.ability import Ability
from ceo.brain.memory_augment import MemoryAugment

log = logging.getLogger('ceo.ability')


class AgenticAbility(Ability):
    def __init__(self, agent: BaseAgent):
        self._agent: BaseAgent = agent
        self.__name__ = f'talk_to_{agent.name}'
        self.__doc__ = json.dumps({
            "description": {
                "brief_description": f'Initiates a conversation with "{agent.name}" to use its abilities.',
                "detailed_description": f"First, carefully consider and explore {agent.name}'s potential abilities in solving your tasks, "
                                        f"then, if you need {agent.name}'s help, you must tell comprehensively, precisely "
                                        f"and exactly what you need {agent.name} to do.",
                f"self_introduction_from_{agent.name}": agent.introduction,
                "hint": f"By reading [self_introduction_from_{agent.name}], you can learn what {agent.name} can do, "
                        f"and then decide whether to initiates a conversation with {agent.name} according to its abilities.",
                "args": [{
                    "query": {
                        "name": "query",
                        "type": "str",
                        "description": f"A comprehensively, precisely and exactly instruction to be processed by {agent.name}."
                    }
                  }
                ],
                "returns": {
                  "type": "str",
                  "description": f"{agent.name}'s response to your instruction."
                }
            }
        }, ensure_ascii=False)
        super().__init__(self)
        log.debug(f'Agent dispatcher generated. {self.__name__}: {self.__doc__}')

    @override
    def __call__(self, query: str, memory: dict | None = None, *args, **kwargs) -> str:
        if memory is not None and isinstance(self._agent, MemoryAugment):
            self._agent.bring_in_memory(memory)
        result = self._agent.assign(query).just_do_it()
        if isinstance(result, dict):
            return json.dumps(result, ensure_ascii=False)
        return result
