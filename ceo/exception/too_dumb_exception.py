from langchain_core.language_models import BaseChatModel


class TooDumbException(Exception):
    def __init__(self, model: BaseChatModel):
        model_name = model.dict()['model_name']
        super().__init__(f'The model "{model_name}" is too dumb to be my brain, '
                         f'swap it or change its temperature.')
