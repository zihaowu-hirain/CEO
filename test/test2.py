from ceo.action.action import Action
from ceo.prompt.scheduler_prompt import SchedulerPrompt
from ceo.brain.lm import get_openai_model


def open_email(app_name: str) -> str:
    """
    Opens an email by its name
    :param app_name:
    :return:
    """
    pass


def edit_email(content: str) -> str:
    """
    Edits an email
    :param content:
    :return:
    """
    pass


def send_email(confirm: bool) -> str:
    """
    Sends an email
    :param confirm:
    :return:
    """
    pass


action = Action(open_email)
action2 = Action(edit_email)
action3 = Action(send_email)

model = get_openai_model(
    key='sk-BOa1mtOTJwJ6oS2JpxTyHleWGxtoLWHAJEmJHVXUvdT3BlbkFJz8vYJ3KpqnKEQH1h-qXg3yEj8bkGQwJj5jA_L8FgoA',
    name='gpt-3.5-turbo-1106',
    temp=1,
    top_p=0.5
)

prompt = SchedulerPrompt(actions=[action, action2, action3], query='send a email(use gmail) to mike tell him i am ill today')
print(prompt.prompt)
actions = prompt.invoke(model)
for action in actions:
    print(action.function)
