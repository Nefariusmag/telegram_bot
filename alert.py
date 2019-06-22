import os
# import logging
from flask import Flask, request
from werkzeug.utils import secure_filename
import requests


TOKEN = os.getenv('TOKEN', '')
PROXY = os.getenv('PROXY', '')
url = f"https://api.telegram.org/bot{TOKEN}/"
chat_id = '121860960'


# logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO,
#                     filename='alert.log')


app = Flask(__name__)
app.denig = True


@app.route("/", methods=["GET"])
def index():
    return "Hello World"


@app.route("/alert", methods=["POST"])
def get_alert_message():
    lamp = secure_filename(request.headers['lamp'])
    # logging.info(lamp)
    send_message(chat_id, f'{lamp} is failed')
    # logging.info(res)
    return "OK"


def send_message(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params, proxies=dict(http=PROXY, https=PROXY))
    return response


app.run(host='0.0.0.0')
