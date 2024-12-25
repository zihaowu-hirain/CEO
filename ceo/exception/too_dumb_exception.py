from langchain_core.language_models import BaseChatModel


class TooDumbException(Exception):
    def __init__(self, model: BaseChatModel):
        super().__init__(f'The model "{model.dict()['model_name']}" is too dumb to be my brain, '
                         f'swap it or change its temperature.')
