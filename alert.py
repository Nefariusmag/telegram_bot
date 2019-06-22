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
    try:
        version_product = secure_filename(request.headers['version_product'])
        component = secure_filename(request.headers['component'])
        version_component = secure_filename(request.headers['version_component'])
        url_test = secure_filename(request.headers['url_test'])
        text = f'{component} version {version_component} on {version_product} is failed. {url_test}'
    except KeyError:
        text = "Didn't get all header that we need (version_product, component, version_component, url_test)"
    # logging.info(lamp)
    send_message(chat_id, text)
    # logging.info(res)
    return "OK"


def send_message(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params, proxies=dict(http=PROXY, https=PROXY))
    return response


app.run(host='0.0.0.0')
