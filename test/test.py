import subprocess

from ceo.action.action import Action
from ceo.brain.lm import get_openai_model
from ceo.brain.agent import Agent

def open_calculator(do: bool) -> str:
    if do:
        subprocess.run(['calc'], capture_output=False, text=False)
        return 'opens the calculator'

model = get_openai_model(
    key='sk-aQISEZpOPkf-4F0WlzxX7oqogziwTePmBIZ9J-p5gjT3BlbkFJwUHkTjEirza8z6NdT1hY78mMAlCSkLrfNnWrrFR28A',
    name='gpt-3.5-turbo-1106',
    temp=0.3,
    top_p=0.5
)

action = Action('open the calculator', function=open_calculator)

response = Agent(
    query='i am suffering doing math!',
    action=action,
    model=model
).respond()

print(response)
