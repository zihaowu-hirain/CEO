class NullRequestException(Exception):
    def __init__(self):
        super().__init__("Query cannot be empty")
