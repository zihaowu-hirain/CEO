from ceo import Agent


def agentic(agent: Agent):
    def decorator(func):
        def wrapper(query: str, *args, **kwargs) -> str:
            return agent.assign(query).just_do_it()
        wrapper.__name__ = f'talk_to_{agent.name}'
        wrapper.__doc__ = (f'Initiates a conversation with "{agent.name}" to use its abilities.\n'
                        f'You must tell detailed and exactly what you need "{agent.name}" to do.\n'
                        f'\nSelf introduction from {agent.name}: "{agent.introduction}".\n'
                        f'\nBelow is detailed information about {agent.name}:\n'
                        f'{"-"*6}\n{agent}\n{"-"*6}\n'
                        f'\nArgs:\n'
                        f'query (str): The input query to be processed by {agent.name}.\n'
                        f'\nReturns:\n'
                        f'str: {agent.name}\'s response to the query.\n')
        return wrapper
    return decorator
