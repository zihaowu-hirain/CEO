from ceo.action.action import Action


class ActionContainer(object):
    def __init__(self):
        actions: dict[str, dict[str, Action]] = dict()

