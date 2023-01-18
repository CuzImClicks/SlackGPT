import threading
from Handler import Handler
from Logger import *
from Question import Question

class ChatBotThread(threading.Thread):

    def __init__(self, handler: Handler, browser: str, prefix: str = "!", headless: bool = True):
        """Inherits from threading.Thread and is used to run ChatGPT in a separate thread

        Args:
            handler (Handler): The handler to use in the main thread
            browser (str): The browser playwright should use
            headless (bool, optional): Whether to run ChatGPT in headless mode. Defaults to True.
        """
        super().__init__()
        self.queue = handler.queue
        self.handler = handler
        self.lg = Logger("ChatGPT", level=Level.INFO, formatter=Logger.minecraft_formatter, handlers=[FileHandler.latest_file_handler(Logger.minecraft_formatter), main_file_handler])
        self.browser = browser
        self.headless = headless
        self.prefix = prefix

    def create_bot(self):
        return None

    def run(self) -> None:
        return super().run()

    def ask(self, question: Question) -> str:
        return ""