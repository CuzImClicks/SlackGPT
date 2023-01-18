from typing import List
from Question import Question

class User:
    def __init__(self, username: str):
        """Represents a user in the handler

        Args:
            username (str): The username of the user
        """
        self.username = username
        self.conversation_id = None # The conversation id from ChatGPT
        self.pending: List[Question] = [] # The list of pending questions
        self.answered: List[Question] = [] # The list of answered questions

    def __str__(self):
        return f"User({self.username}) -> {self.conversation_id}"

    def add(self, question: Question):
        question.user = self
        self.pending.append(question)

    def in_pending(self, question: str) -> bool:
        """Utility method to check if a question is in the pending list

        Args:
            question (str): The prompt of the question to check

        Returns:
            bool: Whether or not the question is in the pending list
        """
        return question in [item.text for item in self.pending]

    def in_answered(self, question: str) -> bool:
        """Utility method to check if a question is in the answered list

        Args:
            question (str): The prompt of the question to check

        Returns:
            bool: Whether or not the question is in the answered list
        """        """"""
        return question in [item.text for item in self.answered]