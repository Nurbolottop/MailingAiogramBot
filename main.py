from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import config
import sqlite3

connect = sqlite3.connect('users.db')
cur  = connect.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    username VARCHAR(255),
    id INTEGER,
    chat_id INTEGER
    );
    """)
connect.commit()

connect_admin = sqlite3.connect('admin.db')
curr  = connect_admin.cursor()
curr.execute("""CREATE TABLE IF NOT EXISTS admin(
    id INTEGER
    );
    """)
connect_admin.commit()

bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())



@dp.message_handler(commands=["start"])
async def start(message : types.Message):
    cur  = connect.cursor()
    cur.execute(f"SELECT id FROM users WHERE  id  == {message.from_user.id};")
    result = cur.fetchall()
    if result ==[]:
        cur.execute(f"INSERT INTO users VALUES ('{message.from_user.username}', {message.from_user.id}, {message.chat.id});")
    connect.commit()
    await message.answer(f"Здравстуйте,{message.from_user.full_name} .Меня зовут Tolobrun.\nЕсли хотите узнать обо мне больше нажмите: /help ")

@dp.message_handler(commands=["help"])
async def help(message : types.Message):
    await message.answer("Привет Я черный! \nВот мои команды:\n/start - Запустить бота\n/help - Помощь\n/users - Посмотреть список пользователей\n(только для админам)\n/add_admin - Добавить админа(только для админам)\n/mailing - Сделать рассылку(только для админам).")


@dp.message_handler(commands=["users"])
async def start(message : types.Message):
    cur  = connect.cursor()
    cur.execute("SELECT * FROM users;")
    res = cur.fetchall()

    cur1  = connect_admin.cursor()
    cur1.execute("SELECT * FROM admin;")

    result = cur1.fetchall()
    for user in result:
        if message.from_user.id in user:
            if res !=[]:
                await message.answer(res)
            else:
                await message.answer("Список пуст")

class MailingState(StatesGroup):
    mailing = State()

@dp.message_handler(commands=["mailing"])
async def mailing(message : types.Message):
    cur1  = connect_admin.cursor()
    cur1.execute("SELECT * FROM admin;")
    result = cur1.fetchall()
    for user in result:
        
        if message.from_user.id in user:
            
            await message.answer('Введите сообщение рассылки: ')
            await MailingState.mailing.set()
    else:
        await message.answer("У вас нет прав")
class MailingState(StatesGroup):
    mailing = State()

@dp.message_handler(commands=["mailing"])
async def mailing(message : types.Message):
    cur1  = connect_admin.cursor()
    cur1.execute("SELECT * FROM admin;")
    result = cur1.fetchall()
    for user in result:
        
        if message.from_user.id in user:
            
            await message.answer('Введите сообщение рассылки: ')
            await MailingState.mailing.set()
    else:
        await message.answer("У вас нет прав")

@dp.message_handler(state=MailingState.mailing)
async def mailing(message : types.Message, state : FSMContext):
    cur1  = connect_admin.cursor()
    cur1.execute("SELECT * FROM admin;")
    result = cur1.fetchall()
    try:
        await message.answer("Началась рассылка")
        for user in result:
            if message.from_user.id in user:
                cur = connect.cursor()
                cur.execute("SELECT chat_id FROM users;")
                result = cur.fetchall()
                for i in result:

                    await bot.send_message(chat_id=int(i[0]), text = message.text)
                await state.finish()
        await state.finish()
    except:
        await message.answer("Произошла ошибка, повторите попытку позже")
        await state.finish()

class AdminState(StatesGroup):
    admin = State()


        
@dp.message_handler(state=AdminState.admin)
async def admin_add(message : types.Message,state : FSMContext):
    cur_admin  = connect_admin.cursor()
    cur_admin.execute("SELECT * FROM admin;")
    result = cur_admin.fetchall()
    try:
        for user in result:
            if message.from_user.id in user:
                print(user)
                res = message.text.split()
                
                cur_admin = cur_admin.execute(f"INSERT INTO admin (id) VALUES ('{res[0]}');")
                connect_admin.commit()
        await state.finish()
        
    except:
        await message.answer("Произошла ошибка, повторите попытку позже")


executor.start_polling(dp)