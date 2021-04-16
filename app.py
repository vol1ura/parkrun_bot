# Bot is deployed on Heroku, so it might sleep
# after 30 mins of being inactive but could wake up (big delay around 30 secs)
from flask import Flask, request, render_template

from parkrunnerbot import *


app = Flask(__name__)


@app.route('/' + TOKEN_BOT, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route(f"/{os.environ.get('WEBHOOK')}")
def webhook():
    bot.remove_webhook()
    webhook_url = os.environ.get('HOST_BOT') + TOKEN_BOT
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to [{webhook_url[:40]}... ]", 200


@app.route("/")
def index():
    return render_template("index.html"), 200


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    app.run()
