from Question import Question
from slack_sdk.web import WebClient


class WaitingQuestion(Question):

    def __init__(self, channel: str, username: str, text: str, user, ts: str, client: WebClient):
        super().__init__(channel, username, text, user, ts, client)

    def send_pre_answer(self) -> str:
        return self.client.chat_postMessage(channel=self.channel, text="I am thinking ...")

    def send_answer(self) -> None:
        self.client.chat_postMessage(channel=self.channel, text=self.answer_text)
