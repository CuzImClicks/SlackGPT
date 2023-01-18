from typing import List
from slack_sdk import WebClient
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import json
import argparse
from Logger import *
from Handler import Handler
from GPTThread import GPTThread

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

lg = Logger("SlackGPT", level=Level.DEBUG if args.debug else Level.INFO, formatter=Logger.minecraft_formatter, handlers=[FileHandler.latest_file_handler(Logger.minecraft_formatter), main_file_handler])
clg = Logger("CHAT", level=Level.WARNING, formatter=Logger.minecraft_formatter, handlers=[FileHandler(Level.LOG, Logger.minecraft_formatter, directory="./logs", generator=lambda *_: "chat.log"), main_file_handler])
app = Flask("SlackGPT") 
adapter = SlackEventAdapter(secret, "/slack/events", app)

client = WebClient(token)
handler = Handler(client)

@adapter.on("message")
def message(payload: dict):

    event = payload["event"]
    message = event["text"]

    if "bot_id" in event.keys():
        if not handler.is_unique_message(payload):
            return
        if message == "I am thinking ...":
            handler.waiting_messages.append(event["ts"])
        return Response("OK", status=200)

    handler.messages.append(payload["event_id"])

    user = client.users_info(user=event["user"]) # lookup the user id to get the username and profile picture
    username = user["user"]["profile"]["display_name"]
    if username == "":
        username = user["user"]["real_name"]

    lg.debug(json.dumps(payload, indent=2))
    clg.log(f"[{event['channel']}] {username}: {event['text']}")

    if message.lower().startswith(args.prefix.lower()) or event["channel_type"] == "im":
        return handler.process_message(payload, username)

    return Response("OK", status=200)


if __name__ == "__main__":
    lg.info("Starting GPT Thread from main.py")
    gpt_thread = GPTThread(handler, args.browser, args.prefix, args.headless)
    lg.info("Started GPT Thread from main.py")
    gpt_thread.start()
    app.run(debug=args.debug)
