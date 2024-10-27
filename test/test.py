import subprocess

from ceo.action.action import Action
from ceo.brain.lm import get_openai_model
from ceo.brain.agent import Agent


def open_calculator(do: bool) -> str:
    if do:
        subprocess.run(['calc'], capture_output=False, text=False)
        return 'the calculator is opened'


model = get_openai_model(
    key='sk-BOa1mtOTJwJ6oS2JpxTyHleWGxtoLWHAJEmJHVXUvdT3BlbkFJz8vYJ3KpqnKEQH1h-qXg3yEj8bkGQwJj5jA_L8FgoA',
    name='gpt-3.5-turbo-1106',
    temp=1,
    top_p=0.5
)

action = Action('open the calculator', function=open_calculator)

response = Agent(
    query='i am suffering doing math!',
    action=action,
    model=model
).respond()

print(response)
