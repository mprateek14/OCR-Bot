import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler, Filters
import os
import pytesseract
import requests

TOKEN_ID = ''

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Prateek\\Downloads\\mykey.json"

bot = telegram.Bot(token = TOKEN_ID)
updater = Updater(token = TOKEN_ID)
dispatcher = updater.dispatcher

def start(bot,update):
    firstname = update.message.from_user.first_name
    bot.send_message(chat_id=update.message.chat_id, text=("Hey " + firstname + "! " + "Send me a picture having text and I will send back the text to you!"))
    


def textHandle(bot,update):
    msg = update.message.text
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text="I only accept images!")
    print("Message Received")


def get_picture(bot, update):
    message = update.message
    print("Message Received")
    file_id = message.photo[-1].file_id
    chat_id = update.message.chat_id
    do_ocr(bot, update, file_id, chat_id)


def do_ocr(bot, update, file_id, chat_id):
    filepath = os.path.expanduser('~') + '/' + file_id
    bot.send_message(chat_id=chat_id, text="Let me convert this to text!")
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    file = bot.get_file(file_id).download(filepath)
    pytes(filepath, chat_id)


def do_ocr_api(bot, update, file_id, chat_id):
    url = "https://api.telegram.org/bot" + TOKEN_ID + "/getFile?file_id=" + file_id
    response = requests.get(url)
    parse = response.json()
    filepath = parse["result"]["file_path"]
    newurl = "https://api.telegram.org/file/bot"+ TOKEN_ID + "/" +filepath
    print(newurl)
    bot.send_message(chat_id=chat_id, text="I am getting the text for you.")
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    #file = bot.get_file(file_id).download(newurl)
    ocr_space_url(newurl,chat_id,overlay=False, api_key='2da9ea967f88957', language='eng')


def pytes(filepath, chat_id):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    result = pytesseract.image_to_string(filepath, config='--psm 11')
    bot.send_message(chat_id=chat_id, text= str(result))
    os.remove(filepath)

def ocr_space_url(url,chat_id, overlay=False, api_key='2da9ea967f88957', language='eng'):


    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': '2da9ea967f88957',
               'language': 'eng',
               }
    r = requests.post('https://api.ocr.space/parse/image',
                      data=payload,
                      )
    result = r.content.decode()
    print(result)
    bot.send_message(chat_id=chat_id, text= str(result))



def googleVapi(filepath, chat_id):
    from google.cloud import vision
    image_uri = filepath

    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = image_uri

    response = client.text_detection(image=image)

    for text in response.text_annotations:
        print(text.description)
        bot.send_message(chat_id=chat_id, text= str(text.description))
        vertices = ['(%s,%s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
        print('bounds:', ",".join(vertices))



start_handler = CommandHandler('start', start)
text_handler = MessageHandler(Filters.text, textHandle)
image_handler = MessageHandler(Filters.photo, get_picture)


dispatcher.add_handler(start_handler)
dispatcher.add_handler(text_handler)
dispatcher.add_handler(image_handler)

updater.start_polling()

    
    
    
