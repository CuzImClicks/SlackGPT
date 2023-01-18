# SlackGPT
A Slack bot that uses the OpenAI's [ChatGPT](https://chat.openai.com) to respond to users' questions, posed in a slack channel.

## Usage
1. Clone the repository and install the dependencies:
```
git clone https://github.com/CuzImClicks/SlackGPT.git
pip install -r requirements.txt
```

2. Follow a tutorial on how to create a slack bot in the slack webinterface and obtain

`SLACK_APP_TOKEN and SLACK_BOT_TOKEN.`

3. Use ngrok to obtain an IP for the Slack Event System to use and register it with Slack

3. Follow the documentation at [ChatGPT-Wrapper](https://github.com/mmabrouk/chatgpt-wrapper) and login to your OpenAI account.

4. Run the bot

`python app.py --token <SLACK_APP_TOKEN> --secret <SLACK_BOT_TOKEN>`

## Command Line Arguments
```
usage: main.py [-h] [--auth_path AUTH_PATH] [--token TOKEN] [--secret SECRET] [--debug] [--headless]
               [--browser {firefox,chromium}] [--prefix PREFIX]

options:
  -h, --help                show this help message and exit
  --auth_path AUTH_PATH
                            Specifies the path to a file containing first the Slack Bot token, then the Slack signing
                            secret
  --token TOKEN, -t TOKEN
                            Manually specify the Slack token
  --secret SECRET, -s SECRET
                            Manually specify the Slack signing secret
  --debug, -d               Enable debug logging
  --headless                Run chatgpt wrapper in headless mode
  --browser {firefox,chromium}
                            Specify the browser used by chatgpt wrapper (playwright install <browser>)
  --prefix PREFIX           Specify the prefix to trigger the bot
```

## Example
```
python app.py --token xoxp-1234567890-1234567890-1234567890-abcdef --secret xoxb-1234567890-abcdefghijklmnopqrstuvwxyz
```

### Note
This bot uses the ChatGPT Wrapper which requires an OpenAI account.

## Built With
```
Slack API - The API used to interact with Slack
SlackEventAdapter - A Python adapter for the Slack Events API
ChatGPT Wrapper - A Python wrapper for the OpenAI's ChatGPT
Flask - A micro web framework for Python
argparse - A standard library for parsing command-line options and arguments
```