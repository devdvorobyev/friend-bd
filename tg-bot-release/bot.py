import telebot
import logging
import asyncio

bot = telebot.TeleBot('8022532267:AAH5HX8T8izACdlAtd7Yt6llPhzkCp8sIgw')

# ID Channel -1002494432055
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)  # logging
bot.polling(none_stop=True, interval=0)

releaseChatId = -1002494432055


async def send_status_message(event, msg_id='', mail_body=''):
    if (event == 'send'):
        msg = bot.send_message(chat_id=releaseChatId, text=mail_body)
        return msg
    else:
        msg = bot.edit_message_text(chat_id=releaseChatId, message_id=msg_id, text=mail_body)
        return msg


#asyncio.run(send_status_message())
