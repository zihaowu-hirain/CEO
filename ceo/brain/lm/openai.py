import langchain_openai


def get_lm(key: str, name: str, temp: int, top_p: int, stream: bool = True):
    return langchain_openai.ChatOpenAI(
        api_key=key,
        model=name,
        top_p=top_p,
        temperature=temp,
        streaming=stream
    )
