# Bot is deployed on Heroku, so it might sleep
# after 30 mins of being inactive but could wake up (big delay around 30 secs)
from flask import Flask, request

from parkrunnerbot import *


app = Flask(__name__)


@app.route('/' + TOKEN_BOT, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route(f"/{os.environ.get('WEBHOOK')}")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://parkruner.herokuapp.com/' + TOKEN_BOT)
    return "!", 200


@app.route("/bot")
def bot_page():
    return "<h1>Привет, вы на странице для администрирования бота</h1>", 200


@app.route("/")
def index():
    return "<h1>Привет</h1>", 200


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    app.run()
