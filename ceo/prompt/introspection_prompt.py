import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')

END = '--END--'
START_SENTENCE = 'To assess whether the <query> has been fully achieved, I will outline the recorded actions from <history> and compare them to the <query>:'

OUTPUT_EXAMPLE = START_SENTENCE + """
1. Grocery shopping: The plan was to purchase ingredients such as vegetables, meat, and spices. The history shows that Alex successfully bought carrots, chicken breasts, and garlic from the supermarket.
2. Cooking the meal: The dish required chopping the vegetables and sautéing them with the chicken. Alex followed this step and cooked the chicken with the carrots and garlic in a pan, ensuring everything was well-cooked.
3. Plating the dish: The next step involved arranging the cooked meal beautifully on a plate. Alex skillfully plated the chicken and vegetables, making it visually appealing.
4. Eating the meal: There is no record indicating that Alex sat down to eat the meal after plating it. 
Conclusion: Based on the above assessment, the <query> has not been fully achieved. While shopping, cooking, and plating were completed, the final step of eating the meal has not been recorded.
""" + END


class IntrospectionPrompt(Prompt):
    def __init__(self, query: str, history: dict | list, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": "Below in <history> are actions have been performed to achieve <query>. ",
            "query": query,
            "task": "Think step by step whether <query> has been fully achieved "
                    "according to <history> and <query>. "
                    "Then, provide the detailed results mentioned in <history> accurately. "
                    "Finally, if the <query> has not been fully achieved, explain why failed?",
            "history": history,
            "output_datatype": "text",
            "output_format": f'{START_SENTENCE}\n'
                             '{recorded_actions_from_<history>}\n'
                             '{conclusion}',
            "output_example": OUTPUT_EXAMPLE,
            "hint_1_for_output": 'You must strictly follow the format in <output_format>!! '
                                 'You should refer to example in <output_example>!!',
            "hint_2_for_output": "Provide thought process (briefly and concisely) before opinion and conclusion.",
            "hint_3_for_output": "Output should be concise, accurate, and short enough.",
            "hint_for_end_pattern": f'The "{END}" pattern marks the end of your whole response, '
                                    f'no more words are allowed after "{END}" pattern. '
                                    f'The "{END}" pattern is absolutely important, do not forget to place it '
                                    'in the end of your response.'
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'IntrospectionPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        resp = model.invoke(self.prompt).content
        log.debug(f'IntrospectionResponse: {resp}')
        return resp
