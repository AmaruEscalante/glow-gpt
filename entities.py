class Message:
    def __init__(self, phone_number, content, is_from_assistant):
        self.phone_number = phone_number
        self.content = content
        self.is_from_assistant = is_from_assistant