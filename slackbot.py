import requests
import slack
import os
import json


def slack_send_message(msg, chnl):
    client = slack.WebClient(os.environ['SLACK_TOKEN'])
    response = client.chat_postMessage(channel=chnl,text=msg)

def slack_post_message(msg, chnl, **kwargs):

    url = 'https://slack.com/api/chat.postMessage'
    data = {
        'token': os.environ['SLACK_BOT_TOKEN'],
        'channel': chnl,
        'text': msg
        }

    data.update(**kwargs)

    response = requests.post(url, data=data)



