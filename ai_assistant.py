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
            ['(.*) help (.*)', ['Sure, I can try to help. What do you need assistance with?']],
        ]

    def get_response(self, question):
        question = question.lower()
        for pattern, responses in self.chatbot_pairs:
            match = re.match(pattern, question)
            if match:
                response = random.choice(responses)
                return response % match.groups()
        return self.responses.get(question, "I'm sorry, I don't understand that question.")
