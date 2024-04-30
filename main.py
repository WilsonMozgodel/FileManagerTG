import telebot
from telebot import TeleBot, types
import sqlite3
import os
  
  
bot = TeleBot('YOUR_TOKEN')


def create_table():
    conn = sqlite3.connect('file_storage.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                      )''')
    conn.commit()
    conn.close()

def add_file(file_name):
    conn = sqlite3.connect('file_storage.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (name) VALUES (?)", (file_name,))
    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(commands=['start'])
def main(message: types.Message):
    user_id = message.from_user.id
    res = bot.get_chat_member(chat_id='@pomoikabomja', user_id=user_id)
    
    if res.status == "member" or res.status == 'creator':
    
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Открыть хранилище")
        markup.row(button)

        bot.send_message(user_id, "Хранилище файлов", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Открыть хранилище")
def base(message):
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
    callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
    callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
    callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
    keyboard.add(callback_button2, callback_button4)
    keyboard.add(callback_button1, callback_button3)
    bot.send_message(message.chat.id, "Хранилище открыто", reply_markup=keyboard)
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    conn = sqlite3.connect('file_storage.db')
    cursor = conn.cursor()

    if call.data == "in":
        bot.send_message(call.message.chat.id, "Отправь файл для добавления")

    elif call.data == "del":
        keyboard = types.InlineKeyboardMarkup()
        callback_button1 = types.InlineKeyboardButton(text="Назад", callback_data="back")
        keyboard.add(callback_button1)
        def delete_handler(call):
            try:
                conn = sqlite3.connect('file_storage.db')
                cursor = conn.cursor()
    
                cursor.execute("SELECT name FROM files")
                files = cursor.fetchall()
    
                if files:
                    files_list = ""
                    for idx, (file_name,) in enumerate(files, start=1):
                        files_list += f"{idx}. {file_name}\n"
    
                    bot.send_message(call.message.chat.id, f"Введите номер файла, который хотите удалить:\n`{files_list}`", parse_mode='MarkdownV2')
                    bot.register_next_step_handler(call.message, lambda message, files=files, cursor=cursor, conn=conn: delete_file(message.text, call, files, cursor, conn))  # Передаем текст сообщения
                else:
                    bot.send_message(call.message.chat.id, "Хранилище файлов пусто")
                    keyboard = types.InlineKeyboardMarkup()
                    callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
                    callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
                    callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
                    callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
                    keyboard.add(callback_button2, callback_button4)
                    keyboard.add(callback_button1, callback_button3)
                    bot.send_message(call.message.chat.id, "Открыто хранилище", reply_markup=keyboard)
                    cursor.close()
                    conn.close()
            except Exception as e:
                bot.send_message(call.message.chat.id, f"Ошибка: {e}")
    
        delete_handler(call)

        def delete_file(file_index, call, files, cursor, conn):
            try:
                selected_idx = int(file_index.split('.')[0])
                if selected_idx in range(1, len(files) + 1):
                    file_name = files[selected_idx - 1][0]
                    cursor.execute("DELETE FROM files WHERE name=?", (file_name,))
                    conn.commit()
                    bot.send_message(call.message.chat.id, f"Файл {file_name} успешно удален")
                    keyboard = types.InlineKeyboardMarkup()
                    callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
                    callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
                    callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
                    callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
                    keyboard.add(callback_button2, callback_button4)
                    keyboard.add(callback_button1, callback_button3)
                    bot.send_message(call.message.chat.id, "Открыто хранилище", reply_markup=keyboard)
                else:
                    bot.send_message(call.message.chat.id, "Неверный номер файла")
            except Exception as e:
                bot.send_message(call.message.chat.id, f"Ошибка при удалении файла: {e}")
        

    elif call.data == "out":
        cursor.execute("SELECT name FROM files")
        files = cursor.fetchall()

        if files:
            files_list = ""
            for idx, (file_name,) in enumerate(files, start=1):
                files_list += f"{idx}. {file_name}\n"

            bot.send_message(call.message.chat.id, f"Выберите номер файла, который хотите получить:\n`{files_list}`", parse_mode='MarkdownV2')
            bot.register_next_step_handler(call.message, lambda message, files=files, call=call: send_selected_file(message.text, files, call))


        else:
            bot.send_message(call.message.chat.id, "Хранилище файлов пусто")
            keyboard = types.InlineKeyboardMarkup()
            callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
            callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
            callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
            callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
            keyboard.add(callback_button2, callback_button4)
            keyboard.add(callback_button1, callback_button3)
            bot.send_message(call.message.chat.id, "Открыто хранилище", reply_markup=keyboard)
            cursor.close()
            conn.close()

    elif call.data == 'list':
        cursor.execute("SELECT name FROM files")
        files = cursor.fetchall()

        if files:
            files_list = ""
            for idx, (file_name,) in enumerate(files, start=1):
                files_list += f"{idx}. {file_name}\n"

            bot.send_message(call.message.chat.id, f"Список ваших файлов:\n`{files_list}`", parse_mode='MarkdownV2')
            keyboard = types.InlineKeyboardMarkup()
            callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
            callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
            callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
            callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
            keyboard.add(callback_button2, callback_button4)
            keyboard.add(callback_button1, callback_button3)
            bot.send_message(call.message.chat.id, "Открыто хранилище", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, "Хранилище файлов пусто")
            keyboard = types.InlineKeyboardMarkup()
            callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
            callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
            callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
            callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
            keyboard.add(callback_button2, callback_button4)
            keyboard.add(callback_button1, callback_button3)
            bot.send_message(call.message.chat.id, "Открыто хранилище", reply_markup=keyboard)
            cursor.close()
            conn.close()
        
            
@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name

    # Check if the file already exists
    if os.path.exists(file_name):
        # If the file exists, generate a new filename with (1), (2), etc.
        base_name, extension = os.path.splitext(file_name)
        counter = 1
        while os.path.exists(f"{base_name} ({counter}){extension}"):
            counter += 1
        file_name = f"{base_name} ({counter}){extension}"

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    add_file(file_name)

    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
    callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
    callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
    callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
    keyboard.add(callback_button2, callback_button4)
    keyboard.add(callback_button1, callback_button3)
    bot.send_message(message.chat.id, "Файл сохранен", reply_markup=keyboard)

def send_selected_file(selected_idx, files, call):
    try:
        conn = sqlite3.connect('file_storage.db')
        cursor = conn.cursor()

        selected_idx = int(selected_idx.split('.')[0])
        if selected_idx in range(1, len(files) + 1):
            file_name = files[selected_idx - 1][0]
            with open(file_name, 'rb') as file:
                bot.send_document(call.message.chat.id, file)
        else:
            bot.send_message(call.message.chat.id, "Неверный номер файла")
        
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Внести файл", callback_data="in")
    callback_button2 = types.InlineKeyboardButton(text="Показать список", callback_data="list")
    callback_button3 = types.InlineKeyboardButton(text="Удалить файл", callback_data="del")
    callback_button4 = types.InlineKeyboardButton(text="Получить файл ", callback_data="out")
    keyboard.add(callback_button2, callback_button4)
    keyboard.add(callback_button1, callback_button3)
    bot.send_message(call.message.chat.id, "Открыто хранилище", reply_markup=keyboard)

create_table()
bot.polling(none_stop=True)
