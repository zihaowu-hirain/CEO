import logging

from ceo.brain.base_agent import BaseAgent
from ceo.ability.agentic_ability import AgenticAbility

log = logging.getLogger('ceo.ability')


def agentic(agent: BaseAgent):
    def decorator(func):
        return AgenticAbility(agent)
    return decorator
