import logging

from ceo.brain.agent import Agent
from ceo.ability.agentic_ability import AgenticAbility

log = logging.getLogger('ceo.ability')


def agentic(agent: Agent):
    return lambda func: AgenticAbility(agent)
