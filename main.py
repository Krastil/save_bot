import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
import psycopg2

from aiogram.types import ContentType
from config import *

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

command = ["Поиск", "Удаление"]
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard.add(*command)

base = psycopg2.connect(DB_URI, sslmode="require")
cur = base.cursor()

user_dict = {}


class UserIdFromTg(object):
    user_id = ""
    user_id_str = ""
    com = ""
    category_name = ""
    tag_name = ""
    message = ""

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_id_str = "user" + str(user_id)

    def get_user_id_str(self):
        return self.user_id_str

    def set_message(self, comm):
        self.message = comm

    def get_message(self):
        return self.message

    def set_com(self, comm):
        self.com = comm

    def get_com(self):
        return self.com

    def set_category_name(self, comm):
        self.category_name = comm

    def get_category_name(self):
        return self.category_name

    def set_tag_name(self, comm):
        self.tag_name = comm

    def get_tag_name(self):
        return self.tag_name


def clean(user_id):
    global user_dict
    for key in user_dict:
        if key == user_id:
            x = user_dict[key]
            x.set_com("")
            x.set_category_name("")
            x.set_tag_name("")
            x.set_message("")


@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message):
    global keyboard, user_dict
    user_id = message.from_user.id
    user_dict[user_id] = UserIdFromTg(user_id)
    base.execute('CREATE TABLE IF NOT EXISTS ' + user_dict[user_id].get_user_id_str() + ' (category, tag, description)')
    base.commit()
    await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                         reply_markup=keyboard)


@dp.message_handler(Text(equals="."))
async def exit_on_menu(message: types.Message):
    global keyboard, user_dict
    user_id = message.from_user.id
    user_dict[user_id] = UserIdFromTg(user_id)
    for key in user_dict:
        if key == message.from_user.id:
            clean(key)
            await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                 reply_markup=keyboard)


async def add_to_db(category, tag, description, user_id_str):
    cur.execute('INSERT INTO ' + user_id_str + ' VALUES(?, ?, ?)', (category, tag, description))
    base.commit()


def category_array(user_id_str):
    new_array = []
    array = cur.execute("SELECT category FROM " + user_id_str + "")
    for i in array:
        new_array.append(i[0])
    return new_array


def tag_array(user_id_str):
    new_array = []
    array = cur.execute("SELECT tag FROM " + user_id_str + "")
    for i in array:
        new_array.append(i[0])
    return new_array


def description_array(user_id_str):
    new_array = []
    array = cur.execute("SELECT description FROM " + user_id_str + "")
    for i in array:
        new_array.append(i[0])
    return new_array


def category_with_description(description, user_id_str):
    new_array = []
    array = cur.execute(
        "SELECT category FROM " + user_id_str + " WHERE description = '" + description + "'")
    for i in array:
        new_array.append(i[0])
    return new_array


def tag_array_with_description(tag, user_id_str):
    new_array = []
    array = cur.execute(
        "SELECT description FROM " + user_id_str + " WHERE tag = '" + tag + "'")
    for i in array:
        new_array.append(i[0])
    return new_array


def delete_tag(tag, user_id_str):
    cur.execute("DELETE FROM " + user_id_str + " WHERE tag = '" + tag + "'")
    base.commit()


def delete_description(tag, description, user_id_str):
    cur.execute("DELETE FROM " + user_id_str + " WHERE tag = '" + tag + "' AND description = '" + description + "'")
    base.commit()


@dp.message_handler(content_types=ContentType.PHOTO)
async def add_photo(message: types.Message):
    global keyboard, user_dict
    for key in user_dict:
        if key == message.from_user.id:
            x = user_dict[key]
            x.set_com("add_tag")
            x.set_category_name("photo")
            x.set_message(message.photo[-1].file_id)
            array = list(set(tag_array(x.get_user_id_str())))
            keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard_for_file.add(*array, "Пропустить")
            await message.answer("Введите tag или нажмите пропустить", reply_markup=keyboard_for_file)


@dp.message_handler(content_types=ContentType.VIDEO)
async def add_video(message: types.Message):
    global keyboard, user_dict
    for key in user_dict:
        if key == message.from_user.id:
            x = user_dict[key]
            x.set_com("add_tag")
            x.set_category_name("video")
            x.set_message(message.video.file_id)
            array = list(set(tag_array(x.get_user_id_str())))
            keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard_for_file.add(*array, "Пропустить")
            await message.answer("Введите tag или нажмите пропустить", reply_markup=keyboard_for_file)


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def add_doc(message: types.Message):
    global keyboard, user_dict
    for key in user_dict:
        if key == message.from_user.id:
            x = user_dict[key]
            x.set_com("add_tag")
            x.set_category_name("document")
            x.set_message(message.document.file_id)
            array = list(set(tag_array(x.get_user_id_str())))
            keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard_for_file.add(*array, "Пропустить")
            await message.answer("Введите tag или нажмите пропустить", reply_markup=keyboard_for_file)


@dp.message_handler(content_types=ContentType.VOICE)
async def add_voice(message: types.Message):
    global keyboard, user_dict
    for key in user_dict:
        if key == message.from_user.id:
            x = user_dict[key]
            x.set_com("add_tag")
            x.set_category_name("voice")
            x.set_message(message.voice.file_id)
            array = list(set(tag_array(x.get_user_id_str())))
            keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard_for_file.add(*array, "Пропустить")
            await message.answer("Введите tag или нажмите пропустить", reply_markup=keyboard_for_file)


@dp.message_handler(content_types=ContentType.AUDIO)
async def add_audio(message: types.Message):
    global keyboard, user_dict
    for key in user_dict:
        if key == message.from_user.id:
            x = user_dict[key]
            x.set_com("add_tag")
            x.set_category_name("audio")
            x.set_message(message.audio.file_id)
            array = list(set(tag_array(x.get_user_id_str())))
            keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard_for_file.add(*array, "Пропустить")
            await message.answer("Введите tag или нажмите пропустить", reply_markup=keyboard_for_file)


@dp.message_handler()
async def add_all_to_db(message: types.Message):
    global keyboard, user_dict
    for key in user_dict:
        if key == message.from_user.id:
            x = user_dict[key]
            access = True

            if x.get_com() == "add_tag" and message.text == "Пропустить":
                x.set_tag_name("")
                await add_to_db(x.get_category_name(), x.get_tag_name(), x.get_message(), x.get_user_id_str())
                await message.answer("Сообщение добавлено")
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)
                clean(key)
                access = False

            if x.get_com() == "add_tag":
                x.set_tag_name(message.text)
                await add_to_db(x.get_category_name(), x.get_tag_name(), x.get_message(), x.get_user_id_str())
                await message.answer("Сообщение добавлено")
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)
                clean(key)
                access = False

            if x.get_com() == "choose_tag":
                x.set_tag_name(message.text)
                array = tag_array_with_description(x.get_tag_name(), x.get_user_id_str())
                for i in array:
                    if category_with_description(i, x.get_user_id_str())[0] == "photo":
                        await message.answer_photo(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "video":
                        await message.answer_video(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "audio":
                        await message.answer_audio(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "voice":
                        await message.answer_voice(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "text":
                        await message.answer(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "document":
                        await message.answer_document(i)
                clean(key)
                access = False
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)

            if x.get_com() == "search" and message.text == "По tag":
                array = list(set(tag_array(x.get_user_id_str())))
                x.set_com("choose_tag")
                keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard_for_file.add(*array)
                await message.answer("Выберите tag", reply_markup=keyboard_for_file)

            if x.get_com() == "search" and message.text == "Без tag":
                x.set_tag_name("")
                array = tag_array_with_description(x.get_tag_name(), x.get_user_id_str())
                for i in array:
                    if category_with_description(i, x.get_user_id_str())[0] == "photo":
                        await message.answer_photo(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "video":
                        await message.answer_video(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "audio":
                        await message.answer_audio(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "voice":
                        await message.answer_voice(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "text":
                        await message.answer(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "document":
                        await message.answer_document(i)
                clean(key)
                access = False
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)

            if x.get_com() == "search" and message.text == "Показать все сообщения":
                array = description_array(x.get_user_id_str())
                for i in array:
                    if category_with_description(i, x.get_user_id_str())[0] == "photo":
                        await message.answer_photo(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "video":
                        await message.answer_video(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "audio":
                        await message.answer_audio(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "voice":
                        await message.answer_voice(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "text":
                        await message.answer(i)
                    if category_with_description(i, x.get_user_id_str())[0] == "document":
                        await message.answer_document(i)
                clean(key)
                access = False
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)

            if x.get_com() == "" and message.text == "Поиск":
                x.set_com("search")
                keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard_for_file.add("По tag", "Без tag", "Показать все сообщения")
                await message.answer("Выберите тип поиска", reply_markup=keyboard_for_file)

            if x.get_com() == "delete_tag":
                x.set_tag_name(message.text)
                delete_tag(x.get_tag_name(), x.get_user_id_str())
                await message.answer("Tag был удален")
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)
                clean(key)
                access = False

            if x.get_com() == "delete_message_without":
                array = tag_array_with_description(x.get_tag_name(), x.get_user_id_str())
                var = 1
                for i in array:
                    if str(var) == message.text:
                        delete_description(x.get_tag_name(), i, x.get_user_id_str())
                    var = var + 1
                await message.answer("Сообщение удалено")
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)
                clean(key)
                access = False

            if x.get_com() == "delete_message_with":
                array = tag_array_with_description(x.get_tag_name(), x.get_user_id_str())
                var = 1
                for i in array:
                    if str(var) == message.text:
                        delete_description(x.get_tag_name(), i, x.get_user_id_str())
                    var = var + 1
                await message.answer("Сообщение удалено")
                await message.answer("Отправьте сообщение или файл, который хотите сохранить.\r\n. - Команда сброса.",
                                     reply_markup=keyboard)
                clean(key)
                access = False

            if x.get_com() == "delete_message" and message.text == "Сообщения без tag":
                x.set_tag_name("")
                array = tag_array_with_description(x.get_tag_name(), x.get_user_id_str())
                var = 1
                for i in array:
                    if category_with_description(i, x.get_user_id_str())[0] == "photo":
                        await message.answer_photo(i, str(var) + ")")
                    if category_with_description(i, x.get_user_id_str())[0] == "video":
                        await message.answer_video(i, caption=str(var) + ')')
                    if category_with_description(i, x.get_user_id_str())[0] == "audio":
                        await message.answer_audio(i, str(var) + ")")
                    if category_with_description(i, x.get_user_id_str())[0] == "voice":
                        await message.answer_voice(i, str(var) + ")")
                    if category_with_description(i, x.get_user_id_str())[0] == "text":
                        await message.answer(str(var) + ") " + i)
                    if category_with_description(i, x.get_user_id_str())[0] == "document":
                        await message.answer_document(i, caption=str(var) + ')')
                    var = var + 1
                x.set_com("delete_message_without")
                await message.answer("Введите цифру сообщения, которое хотите удалить")

            if x.get_com() == "delete_message":
                x.set_tag_name(message.text)
                array = tag_array_with_description(x.get_tag_name(), x.get_user_id_str())
                var = 1
                for i in array:
                    if category_with_description(i, x.get_user_id_str())[0] == "photo":
                        await message.answer_photo(i, str(var) + ")")
                    if category_with_description(i, x.get_user_id_str())[0] == "video":
                        await message.answer_video(i, caption=str(var) + ')')
                    if category_with_description(i, x.get_user_id_str())[0] == "audio":
                        await message.answer_audio(i, str(var) + ")")
                    if category_with_description(i, x.get_user_id_str())[0] == "voice":
                        await message.answer_voice(i, str(var) + ")")
                    if category_with_description(i, x.get_user_id_str())[0] == "text":
                        await message.answer(str(var) + ") " + i)
                    if category_with_description(i, x.get_user_id_str())[0] == "document":
                        await message.answer_document(i, caption=str(var) + ')')
                    var = var + 1
                x.set_com("delete_message_with")
                await message.answer("Введите цифру сообщения, которое хотите удалить")

            if x.get_com() == "delete" and message.text == "Сообщение":
                array = list(set(tag_array(x.get_user_id_str())))
                x.set_com("delete_message")
                keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard_for_file.add(*array, "Сообщения без tag")
                await message.answer("Выберите tag", reply_markup=keyboard_for_file)

            if x.get_com() == "delete" and message.text == "Tag":
                array = list(set(tag_array(x.get_user_id_str())))
                x.set_com("delete_tag")
                keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard_for_file.add(*array)
                await message.answer("Выберите tag", reply_markup=keyboard_for_file)

            if x.get_com() == "" and message.text == "Удаление":
                x.set_com("delete")
                keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard_for_file.add("Tag", "Сообщение")
                await message.answer("Выберите что хотите удалить", reply_markup=keyboard_for_file)

            if x.get_com() == "" and access:
                x.set_com("add_tag")
                x.set_category_name("text")
                x.set_message(message.text)
                array = list(set(tag_array(x.get_user_id_str())))
                keyboard_for_file = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard_for_file.add(*array, "Пропустить")
                await message.answer("Введите tag или нажмите пропустить", reply_markup=keyboard_for_file)


if __name__ == '__main__':
    executor.start_polling(dp)


