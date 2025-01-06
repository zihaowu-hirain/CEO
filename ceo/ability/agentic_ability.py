import json
import logging
from typing_extensions import override

from ceo.brain.base_agent import BaseAgent
from ceo.ability import Ability
from ceo.brain.memory_augment import MemoryAugment

log = logging.getLogger('ceo.ability')
PREFIX = '__AgenticAbility__'


class AgenticAbility(Ability):
    def __init__(self, agent: BaseAgent | MemoryAugment):
        try:
            _test_mem = agent.memory
        except AttributeError:
            raise TypeError("The 'agent' of AgenticAbility should be instance of 'ceo.Agent'.")
        self._agent = agent
        self.__name__ = f'{PREFIX}talk_to_{agent.name}'
        self.__doc__ = json.dumps({
            "description": {
                "brief_description": f'Initiates a conversation with "{agent.name}" to use its abilities.',
                "detailed_description": f"First, carefully consider and explore {agent.name}'s "
                                        "potential abilities in solving your tasks, "
                                        f"then, if you need {agent.name}'s help, "
                                        "you must tell comprehensively, precisely "
                                        f"and exactly what you need {agent.name} to do.",
                f"self_introduction_from_{agent.name}": agent.introduction,
                "hint": f"By reading <self_introduction_from_{agent.name}>, you can learn what {agent.name} can do, "
                        f"and then decide whether to initiates a conversation with {agent.name} "
                        "according to its abilities.",
                "parameters": [{
                    "query": {
                        "name": "query",
                        "type": "str",
                        "description": "A comprehensively, precisely and exactly instruction "
                                       f"to be processed by {agent.name}."
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
    def __call__(self, query_by_step: str, query_high_level: str, memory: dict, *args, **kwargs) -> str:
        self._agent.relay(query_by_step=query_by_step, query_high_level=query_high_level)
        self._agent.bring_in_memory(memory)
        result = self._agent.just_do_it()
        if isinstance(result, dict):
            return json.dumps(result, ensure_ascii=False)
        return result
