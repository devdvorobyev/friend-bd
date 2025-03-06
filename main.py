import asyncio
#from termcolor import colored, cprint
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psycopg2  # Коннект к БД
import os  # Для считки деррикторий
import shutil  # Для перемещения файлов
import smtplib  # Рассылки E-mail
# import importlib.util
# import sys
import telebot

# TG Release Bot
bot = telebot.TeleBot('8022532267:AAH5HX8T8izACdlAtd7Yt6llPhzkCp8sIgw')
#bot.polling(none_stop=True, interval=0) #После вызова этой функции TeleBot начинает опрашивать серверы Telegram на предмет новых сообщений
releaseChatId = -1002494432055
#--------
sqlDirectory = input("Введите путь до папки где лежат SQL скрипты: ")


def send_status_message(event, msg_id='', mail_body=''):
    if (event == 'send'):
        msg = bot.send_message(chat_id=releaseChatId, text=mail_body)
        return msg.message_id
    else:
        bot.edit_message_text(chat_id=releaseChatId, message_id=msg_id, text=mail_body)


try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='OTUS', user='postgres', password='123', host='localhost')
    print('\nWe are here!\n')
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')

cursor = conn.cursor()


def SendMail(toEmail, error, fileName):
    ### SMTP интеграция, для рассылки успеха и нет
    smtp_server = "smtp.yandex.ru"
    port = 587  # используйте порт 465 для SSL
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()  # обновляем соединение с использованием TLS-шифрования
    email = "supermen2123@yandex.ru"

    try:
        server.login(email, password)
    except Exception as e:
        print(str(e))

    from_email = email
    to_email = toEmail
    subject = "Тестовое сообщение"
    message = f"Привет, это тестовое сообщение, отправленное с помощью Python и SMTP. Ошибка выполнения файла {fileName}, суть проблемы: {error}"

    server.sendmail(from_email, to_email, f"Subject: {subject}\n\n{message}")
    server.quit()


def FileWorker():
    # Указываем путь к директории
    rootDirectory = './'
    # Дирректория с логированием
    logDirectory = "/log.txt"
    # Успешные папки и ошибочные
    errorFolder = "SQL_ERROR/"
    successFolder = "SQL_SUCCESS/"
    # Получаем список файлов
    files = os.listdir(sqlDirectory)
    # Шаблон строки для ТГ бота
    msg_template = 'Коллеги, добрый день!\nПроизошло релизное выполнение SQL скриптов на среде STAGE.\nРезультат выполнения скриптов:\n'
    # Переменная для хранения и будущего вытаскивания Id сообщения в ТГ
    msg_id = -1
    if len(files):
        msg_id = send_status_message('send', '', msg_template)
        for fileName in files:
            file = open(sqlDirectory + fileName)
            fileInside = file.read()
            # asyncio.run()
            # print(fileInside)
            msg_template = msg_template + fileName
            #msg = send_status_message('change', msg.id, msg.text + '\n' + fileName)#

            try:
                cursor.execute('BEGIN; SAVEPOINT BEFORE_EXECUTE; ' + fileInside)
                cursor.execute('RELEASE SAVEPOINT BEFORE_EXECUTE;')
                conn.commit()
                # cursor.execute('SELECT * FROM users')
                # all_users = cursor.fetchall()
                # print(all_users)
                """ logFile.truncate(0)
                logFile.write( '\n' + fileName + ' Success!' ) """
                msg_template = msg_template + ' | Success! ✅\n'
                #msg = send_status_message('change', msg_id, msg.text + ' | Success! ✅')#

                file.close()
                if not os.path.exists(rootDirectory + successFolder + fileName):
                    os.makedirs(rootDirectory + successFolder + fileName)
                shutil.copy2(sqlDirectory + fileName, rootDirectory + successFolder + fileName)
                os.remove( sqlDirectory + fileName )
            except Exception as e:
                cursor.execute('ROLLBACK TO SAVEPOINT BEFORE_EXECUTE;')
                if not os.path.exists(rootDirectory + errorFolder + fileName):
                    os.makedirs(rootDirectory + errorFolder + fileName)
                logFile = open(rootDirectory + errorFolder + fileName + logDirectory, 'a+')
                logFile.write('\n' + fileName + ' Error: ' + str(e))
                msg_template = msg_template + ' | Error! ❌\n'
                #msg = send_status_message('change', msg.id, msg.text + ' | Error! ❌')#

                # SendMail('dvorobyevdev@yandex.ru', str(e), fileName)
                file.close()
                shutil.copy2(sqlDirectory + fileName, rootDirectory + errorFolder + fileName)
                os.remove(sqlDirectory + fileName)
                # закрываем все подключения, что бы не загружать память
                logFile.close()
        send_status_message('change', msg_id, msg_template)
        #cprint('Релиз успешно поставлен!', 'white', 'on_green')



# Описание класса по отслеживанию дерриктории, триггер на создание
class FileHandler(FileSystemEventHandler):

    def on_created(self, event):
        FileWorker()



event_handler = FileHandler()
observer = Observer()
observer.schedule(event_handler, path=sqlDirectory, recursive=True)
observer.start()

# Цикл для вечной работы исполняемого файла
while True:
    try:
        pass
    except KeyboardInterrupt:
        observer.stop()
        cursor.close()
        conn.close()
