# Custom Error for handling failed API Calls

class APICallError(Exception):
    def __init__(self, message = "API Call Error"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message