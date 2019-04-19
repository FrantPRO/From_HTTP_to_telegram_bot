import logging
from queue import Queue
import cherrypy
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
from settings import NAME, PORT, TOKEN


class SimpleWebsite:
    @cherrypy.expose
    def index(self):
        return """<H1>Welcome!</H1>"""


class BotInstruction:
    @cherrypy.expose
    def index(self, chat_id, message):
        bot = BotComm(TOKEN, NAME)
        bot.send_message(chat_id, message)
        return "<pre>bot working...</pre>"


class BotComm:
    exposed = True

    def __init__(self, TOKEN, NAME):
        super(BotComm, self).__init__()
        self.TOKEN = TOKEN
        self.NAME = NAME
        self.bot = telegram.Bot(self.TOKEN)
        try:
            self.bot.setWebhook("https://{}.herokuapp.com/{}".format(self.NAME, self.TOKEN))
        except:
            raise RuntimeError("Failed to set the webhook")

        self.update_queue = Queue()
        self.dp = Dispatcher(self.bot, self.update_queue)

        self.dp.add_handler(CommandHandler("start", self._start))
        self.dp.add_handler(MessageHandler(Filters.text, self._echo_all))
        self.dp.add_error_handler(self._error)

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _error(self, error):
        cherrypy.log("Error occurred - {}".format(error))

    def _start(self, bot, update):
        update.effective_message.reply_text("Hello " + update.effective_message.from_user.first_name + "!")

    def send_message(self, chat_id, message_text):
        self.bot.send_message(chat_id=chat_id, text=message_text)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the cherrypy configuration
    cherrypy.config.update({"server.socket_host": "0.0.0.0", })
    cherrypy.config.update({"server.socket_port": int(PORT), })
    cherrypy.tree.mount(SimpleWebsite(), "/")
    cherrypy.tree.mount(BotInstruction(), "/bot")
    cherrypy.tree.mount(
        BotComm(TOKEN, NAME),
        "/{}".format(TOKEN),
        {"/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
