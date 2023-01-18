import time
from typing import List
from slack_sdk import WebClient
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import json
import argparse
from chatgpt_wrapper import ChatGPT
from Logger import *
import threading

parser = argparse.ArgumentParser()
parser.add_argument("--auth_path", help="Specifies the path to a file containing first the Slack Bot token, then the Slack signing secret", required=False)
parser.add_argument("--token", "-t", help="Manually specify the Slack token", required=False)
parser.add_argument("--secret", "-s", help="Manually specify the Slack signing secret", required=False)
parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging", required=False)
parser.add_argument("--headless", action="store_true", help="Run chatgpt wrapper in headless mode", required=False)
parser.add_argument("--browser", choices=["firefox", "chromium"], default="firefox", help="Specify the browser used by chatgpt wrapper (playwright install <browser>)", required=False)
parser.add_argument("--prefix", default="!", help="Specify the prefix to trigger the bot", required=False)

args = parser.parse_args()

if args.auth_path:
    token, secret = open(args.auth_path, "r").read().splitlines() 
else:
    token, secret = args.token, args.secret

lg = Logger("SlackGPT", level=Logger.Level.DEBUG if args.debug else Logger.Level.INFO, formatter=Logger.minecraft_formatter)
app = Flask("SlackGPT") 
adapter = SlackEventAdapter(secret, "/slack/events", app)

client = WebClient(token)


@adapter.on("message")
def message(payload: dict):
    global handler
    event = payload["event"]
    if "bot_id" in event.keys() or payload["event_id"] in handler.messages:
        return

    handler.messages.append(payload["event_id"])

    user = client.users_info(user=event["user"]) # lookup the user id to get the username and profile picture
    username = user["user"]["profile"]["display_name"]
    if username == "":
        username = user["user"]["real_name"]

    lg.debug(json.dumps(payload, indent=2))
    lg.info(f"[{event['channel']}] {username}: {event['text']}")

    message = event["text"]

    if message.lower().startswith(args.prefix.lower()):
        return handler.process_message(event, username)

    return Response("OK", status=200)

@adapter.on("")
def dm(payload: dict):
    ...


class Question:
    def __init__(self, channel: str, username: str, text: str):
        """Represents a question asked by a user

        Args:
            channel (str): The channel id
            username (str): The username of the user
            text (str): The prompt for ChatGPT
        """
        self.channel = channel
        self.username = username
        self.text = text
        self.answer = None # The field for the future answer by ChatGPT
        self.is_answered = False # Whether or not the question has been answered
        self.user = handler.get_user(username) # Get the user object from the handler
        self.user.add(self) # Add the question to the user's pending questions

    def __str__(self):
        return f"Item({self.channel}, {self.user.username}, {self.text}) -> {self.answer}"

    def __getitem__(self, index):
        return self


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
        self.pending.append(question)

    def answer(self, question: Question):
        """Marks a question as answered

        Args:
            question (Question): The question to mark as answered
        """        """"""
        question.is_answered = True
        self.answered.append(question)
        self.pending.remove(question)

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


class Queue:
    def __init__(self):
        """Represents a queue of questions to be answered by ChatGPT
        """
        self.__queue = []

    def push(self, question: Question):
        """Adds a question to the queue

        Args:
            question (Question): The question to add to the queue

        Raises:
            TypeError: If the question is not of type Question
        """
        if not isinstance(question, Question):
            raise TypeError("Question must be of type Question")
        self.__queue.append(question)

    def pop(self) -> Question:
        """Removes the first question from the queue and returns it

        Returns:
            Question: The first question in the queue
        """
        return self.__queue.pop(0)

    def __len__(self) -> Question:
        return len(self.__queue)

    def __getitem__(self, index) -> Question:
        return self.__queue[index]


class Handler:
    def __init__(self) -> None:
        """Represents a handler for the questions, users and queue
        """
        self.messages: List[str] = []
        self.users: List[User] = []
        self.queue: Queue = Queue()

    def get_user(self, username: str) -> User:
        """Returns either an existing user or a new user object

        Args:
            username (str): The username for the user object

        Returns:
            User: The user object
        """
        return [user for user in self.users if user.username == username][0] if username in [user.username for user in self.users] else User(username)

    def process_message(self, event: dict, username) -> Response:
        user = self.get_user(username)
        if user.in_pending(message) or user.in_answered(message):
            client.chat_postMessage(channel=event["channel"], text="You already asked that question. Please wait for an answer." if user.in_pending(message) else [question.answer for question in user.answered if question.text == message][0])
            return Response("OK", status=200)
        try:
            start = time.time()#
            question = Question(event["channel"], username, message)
            self.queue.push(question)
            lg.info(f"Added {username} to queue")            
            while not question.is_answered:
                time.sleep(1)
                lg.warning(f"Waiting for {username} to be answered")
            lg.info(f"Done! Took {time.time() - start} seconds")
            lg.info(f"Response: {question.answer}")
        
            client.chat_postMessage(channel=event["channel"], text=question.answer)
            return Response("OK", status=200)
        except Exception as e:
            lg.error(e)
            client.chat_postMessage(channel=event["channel"], text=f"An error occurred. Please try again later. \n{e}")
            return Response("An error occurred. Please try again later.", status=500)


class GPTThread(threading.Thread):
    def __init__(self, queue: Queue, handler: Handler, lg: Logger, browser: str, headless: bool = True):
        """Inherits from threading.Thread and is used to run ChatGPT in a separate thread

        Args:
            handler (Handler): The handler to use in the main thread
            browser (str): The browser playwright should use
            headless (bool, optional): Whether to run ChatGPT in headless mode. Defaults to True.
        """
        super().__init__()
        self.queue = handler.queue
        self.handler = handler
        self.lg = Logger("ChatGPT")
        self.browser = browser
        self.headless = headless

    def run(self):
        """The method that is run when the thread is started
        """
        self.lg.info("Running GPT Thread")
        lg.info(f"Initializing ChatGPT {self.ident}")
        self.bot = ChatGPT(browser=self.browser, headless=self.headless)
        lg.info(f"Initialized ChatGPT {self.ident}")
        while True:
            if len(self.queue) > 0:
                self.lg.debug(f"Queue Length = {len(self.queue)}")
                question: Question = self.queue.pop()
                try:
                    self.lg.info(f"Asking ChatGPT with prompt {question.text[3:]}")
                    if not question.user.conversation_id is None:
                        self.bot.conversation_id = question.user.conversation_id
                    question.answer = self.bot.ask(question.text[len(args.prefix):])
                    question.user.conversation_id = self.bot.conversation_id
                    self.lg.debug(f"Conversation ID = {self.bot.conversation_id}")

                    question.user.answer(question)
                except Exception as e:
                    self.lg.error(e)
                    question.answer = f"An error occurred. Please try again later. \n{e.with_traceback}"
                    question.user.answer(question)
            else:
                time.sleep(1)


if __name__ == "__main__":
    handler = Handler()
    lg.info("Starting GPT Thread from main.py")
    gpt_thread = GPTThread(handler.queue, handler, lg, args.browser, args.headless)
    lg.info("Started GPT Thread from main.py")
    gpt_thread.start()
    app.run(debug=args.debug)
