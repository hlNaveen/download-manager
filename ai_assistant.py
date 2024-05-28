import re
import random

class AIAssistant:
    def __init__(self):
        self.responses = {
            "hello": ["Hello! How can I help you?", "Hi there! How can I assist you?"],
            "how are you": ["I'm just a program, but thanks for asking! How can I assist you?"],
            "help": ["You can ask me about anything related to downloading files."],
            "thank you": ["You're welcome!", "No problem!"],
            "download status": ["Checking the status of your downloads...", "Let me see how your downloads are going..."]
        }

        self.patterns = [
            (re.compile(r'my name is (.*)', re.IGNORECASE), self.respond_to_name),
            (re.compile(r'(hi|hello|hey|hola)', re.IGNORECASE), self.respond_to_greeting),
            (re.compile(r'what is your name?', re.IGNORECASE), self.respond_to_name_query),
            (re.compile(r'who (created|made) you?', re.IGNORECASE), self.respond_to_creator_query),
            (re.compile(r'can you help me with (.*)', re.IGNORECASE), self.respond_to_help_request),
            (re.compile(r'what is the status of my downloads?', re.IGNORECASE), self.respond_to_download_status)
        ]

        self.default_responses = [
            "I'm not sure how to respond to that.",
            "Can you please clarify?",
            "I'm still learning. Could you please rephrase?"
        ]

    def respond_to_name(self, match):
        name = match.group(1)
        return f"Hello {name}, how can I assist you today?"

    def respond_to_greeting(self, match):
        return random.choice(self.responses["hello"])

    def respond_to_name_query(self, match):
        return "I'm just a chatbot, but you can call me ChatGPT!"

    def respond_to_creator_query(self, match):
        return "I was created by a team of developers at OpenAI."

    def respond_to_help_request(self, match):
        topic = match.group(1)
        return f"Sure, I can help you with {topic}. What specifically would you like to know?"

    def respond_to_download_status(self, match):
        return random.choice(self.responses["download status"])

    def get_response(self, user_input):
        for pattern, response_function in self.patterns:
            match = pattern.match(user_input)
            if match:
                return response_function(match)

        # Learning capability: if no pattern matches, store the new pattern and response
        new_pattern = re.compile(re.escape(user_input), re.IGNORECASE)
        new_response = input("I don't know how to respond to that. What should I say? ")
        self.patterns.append((new_pattern, lambda _: new_response))
        return new_response

    def chat(self, user_input):
        user_input = user_input.lower()
        for question, responses in self.responses.items():
            if question in user_input:
                return random.choice(responses)
        return self.get_response(user_input)
