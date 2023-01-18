from typing import List
from flask import Response
from User import User
from Queue import Queue
from Question import Question
from Logger import *
from slack_sdk import WebClient

class Handler:
    def __init__(self, client: WebClient) -> None:
        """Represents a handler for the questions, users and queue
        """
        self.messages: List[str] = []
        self.users: List[User] = []
        self.queue: Queue = Queue()
        self.client = client
        self.lg = Logger("Handler", level=Level.INFO, formatter=Logger.minecraft_formatter, handlers=[FileHandler.latest_file_handler(Logger.minecraft_formatter), main_file_handler])
        self.waiting_messages = []

    def get_user(self, username: str) -> User:
        """Returns either an existing user or a new user object

        Args:
            username (str): The username for the user object

        Returns:
            User: The user object
        """
        return [user for user in self.users if user.username == username][0] if username in [user.username for user in self.users] else User(username)

    def process_message(self, payload: dict, username) -> Response:
        """Handles the question from the user and replies to it

        Args:
            event (dict): The event extracted from the payload
            username (str): The username of the user

        Returns:
            Response: The response for the Slack API
        """	
        event = payload["event"]
        message = event["text"]
        user = self.get_user(username)
        if user.in_pending(message) or user.in_answered(message):
            self.client.chat_postMessage(channel=event["channel"], text="You already asked that question. Please wait for an answer. \n" if user.in_pending(message) else [question.answer_text for question in user.answered if question.text == message][0])
            return Response("OK", status=200)
        try:
            question = Question(event["channel"], username, message, user, event["ts"], self.client, direct_message=event["channel"] == "im")
            question.send_pre_answer()
            self.queue.push(question)
            self.lg.info(f"Added {username} to queue")
            return Response("OK", status=200)
        except Exception as e:
            self.lg.error(e)
            self.client.chat_postMessage(channel=event["channel"], text=f"An error occurred while processing your message. Please try again later. \n{e}")
            return Response("An error occurred. Please try again later.", status=500)

    def is_unique_message(self, payload: dict) -> bool:
        """Checks whether the message event has already been registered

        Args:
            payload (dict): The payload of the event

        Returns:
            bool: Whether the message event has already been registered
        """
        return not payload["event_id"] in self.messages

