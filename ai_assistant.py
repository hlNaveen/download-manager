import re

class AIAssistant:
    def __init__(self):
        self.responses = {
            "hello": "Hello! How can I help you?",
            "how are you": "I'm just a program, but thanks for asking!",
            "help": "You can ask me about anything related to downloading files.",
            "thank you": "You're welcome!"
        }

        self.chatbot_pairs = [
            ['my name is (.*)', ['Hello %1, how can I assist you?']],
            ['(hi|hello|hey|hola)', ['Hello', 'Hey there', 'Hi']],
            ['(.*) your name?', ["I'm just a chatbot, you can call me ChatGPT!"]],
            ['(.*) (created|made) you', ['I was created by a team of developers at OpenAI.']],
            ['(.*) help (.*)', ['Sure, I can try to help. What do you need assistance with?']]
        ]

    def get_response(self, question):
        for pattern, responses in self.chatbot_pairs:
            match = re.match(pattern, question, re.IGNORECASE)
            if match:
                response = responses[0]
                for i, group in enumerate(match.groups()):
                    response = response.replace(f"%{i + 1}", group)
                return response
        return self.responses.get(question.lower(), "I'm not sure how to answer that.")
