import requests
import os
import time
import json
import flask
import slack
import dialogs
import trello_commands

from pprint import pprint as pp
from flask import Flask, make_response
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
executor = ThreadPoolExecutor(1)

def slack_send_webhook(text, channel, **kwargs):

    data = {
        "channel": channel,
        "text": text
    }

    data.update(kwargs)

    response = requests.post(
        url=os.environ['SLACK_WEB_HOOK'],
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )

    pp("response from 'send_webhook' [%d]: %s" % (
        response.status_code,
        response.text
    ))

@app.route('/angry/1', methods=['POST'])
def hulk():
    client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    client.files_upload(file=r'E:\hulk.jpg',channels='test_channel')

    return make_response('', 200)

@app.route('/add_table', methods=['POST'])
def on_add_board():


    data = {
        "token": os.environ['SLACK_BOT_TOKEN'],
        "trigger_id" : flask.request.values["trigger_id"],
        "dialog": json.dumps(dialogs.dialog_add_table)
    }

    response = requests.post(
        url="https://slack.com/api/dialog.open",
        data=data
    )

    pp(response)

    return make_response("Processing started...", 200)

@app.route('/interactive_action', methods=['POST'])
def on_interactive_action():

    response_text = ''
    interactive_action = json.loads(flask.request.values["payload"])


    try:

        if interactive_action["type"] == "interactive_message":
            pass

        elif interactive_action["type"] == "dialog_submission":

            #TODO: input validation
            executor.submit(
                add_table,
                interactive_action
            )

    except Exception as ex:
        response_text = ":x: Error: `%s`" % ex

    return make_response(response_text, 200)

def add_table(message):

    pp('Task started...')

    submission = message['submission']
    name = submission['name of board']

    try:
        trello_commands.create_new_board(os.environ['TRELLO_KEY'], os.environ['TRELLO_TOKEN'], name)
        response_text = ':v:'

    except Exception as ex:
        response_text = ':x: Что-то пошло не так: `%s`' % ex

    slack_send_webhook(text='Доска создана '+ response_text,
        channel=message['channel']['id'],
        icon=':chart_with_upwards_trend:')


def slack_incoming_msg_handler():

    app.run(host='0.0.0.0', port=8080, threaded=True)


def main():
    slack_incoming_msg_handler()


if __name__ == '__main__':
    main()