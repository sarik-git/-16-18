import telebot
from  telebot import types
import sqlite3
import knop as bt

connection = sqlite3.connect('delivery.db', check_same_thread=False)
sql = connection.cursor()
sql.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, language TEXT, selected_option TEXT)')
sql.execute('CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY, name TEXT, number TEXT); ')
sql.execute('CREATE TABLE IF NOT EXISTS products (pr_id INTEGER PRIMARY KEY AUTOINCREMENT, pr_name TEXT, pr_des TEXT, pr_price REAL, pr_count INTEGER, pr_photo TEXT, pr_category TEXT);')
sql.execute('CREATE TABLE IF NOT EXISTS cart (user_id INTEGER, user_product INTEGER, product_amount INTEGER);')
connection.commit()

bot = telebot.TeleBot('7947958597:AAFsTIRJxuIJbj4W59kdBnVZCcZu88ppUe0')
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_user(user_id):
        user_language = get_user_language(user_id)
        if user_language == 'uz':
            bot.send_message(user_id, 'Assalomu alaykum! Siz allaqachon ro\'yxatdan o\'tganingiz.')
        else:
            bot.send_message(user_id, 'Привет! Вы уже зарегистрированы.')
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Русский', 'O\'zbekcha')
        bot.send_message(user_id, 'Выберите язык / Tilni tanlang:', reply_markup=markup)
        bot.register_next_step_handler(message, set_language)


def set_language(message):
    user_id = message.from_user.id
    if message.text == 'Русский':
        language = 'ru'
    elif message.text == 'O\'zbekcha':
        language = 'uz'
    else:
        bot.send_message(user_id, 'Пожалуйста, выберите правильный язык / Iltimos, to\'g\'ri tilni tanlang.')
        return

    sql.execute('INSERT INTO users (tg_id, language) VALUES (?, ?)', (user_id, language))
    connection.commit()
    if language == 'uz':
        bot.send_message(user_id, 'Ismingizni kiriting:')
    else:
        bot.send_message(user_id, 'Введите ваше имя')
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    user_name = message.text
    user_id = message.from_user.id
    sql.execute('UPDATE users SET name=? WHERE tg_id=?', (user_name, user_id))
    connection.commit()

    language = get_user_language(user_id)
    if language == 'uz':
        bot.send_message(user_id, 'Endi telefon raqamingizni yuboring.', reply_markup=bt.number_button())
    else:
        bot.send_message(user_id, 'Отлично! Теперь отправьте свой номер телефона.', reply_markup=bt.number_button())
    bot.register_next_step_handler(message, get_number, user_name)


def get_number(message, user_name):
    user_id = message.from_user.id
    if message.contact:
        user_number = message.contact.phone_number
        register(user_id, user_name, user_number)
        bot.send_message(user_id, 'Вы успешно зарегистрированы!', reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        language = get_user_language(user_id)
        if language == 'uz':
            bot.send_message(user_id, 'Iltimos, telefon raqamingizni quyidagi tugma orqali yuboring.')
        else:
            bot.send_message(user_id, 'Пожалуйста, отправьте номер телефона через кнопку ниже.')
        bot.register_next_step_handler(message, get_number, user_name)


def register(tg_id, name, number):
    sql.execute('UPDATE users SET number=? WHERE tg_id=?', (number, tg_id))
    connection.commit()


def check_user(tg_id):
    return sql.execute('SELECT * FROM users WHERE tg_id=?;', (tg_id,)).fetchone() is not None


def get_user_language(tg_id):
    return sql.execute('SELECT language FROM users WHERE tg_id=?;', (tg_id,)).fetchone()[0]


bot.polling()


def get_name(message):
    user_name = message.text
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отлично! Теперь отправьте свой номер телефона.', reply_markup=bt.number_button())
    bot.register_next_step_handler(message, get_number, user_name)

def get_number(message, user_name):
    user_id = message.from_user.id
    if message.contact:
        user_number = message.contact.phone_number
        register(user_id, user_name, user_number)
        bot.send_message(user_id, 'Вы успешно зарегистрированы!', reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, 'Пожалуйста отправьте номер телефона через кнопку ниже.')
        bot.register_next_step_handler(message, get_number, user_name)

def register(tg_id, name, number):
    sql.execute('INSERT INTO users (tg_id, name, number) VALUES (?,?,?);', (tg_id, name, number))
    connection.commit()


def check_user(tg_id):
    return sql.execute('SELECT * FROM users WHERE tg_id=?;', (tg_id,)).fetchone() is not None

@bot.message_handler(commands=['edit_profile'])
def edit_profile(message):
    user_id = message.from_user.id
    if check_user(user_id):
        bot.send_message(user_id, 'Что вы хотите изменить?\n1. Имя\n2. Номер телефона\nВведите номер опции.')
        bot.register_next_step_handler(message, choose_edit_option)
    else:
        bot.send_message(user_id, 'Вы не зарегистрированы!')

def choose_edit_option(message):
    option = message.text
    user_id = message.from_user.id
    if option == '1':
        bot.send_message(user_id, 'Введите ваше новое имя:')
        bot.register_next_step_handler(message, update_name)
    elif option == '2':
        bot.send_message(user_id, 'Отправьте новый номер телефона через кнопку ниже.', reply_markup=bt.number_button())
        bot.register_next_step_handler(message, update_number)
    else:
        bot.send_message(user_id, 'Неверный выбор. Попробуйте снова.')

def update_name(message):
    new_name = message.text
    user_id = message.from_user.id
    sql.execute('UPDATE users SET name=? WHERE tg_id=?;',(new_name, user_id))
    connection.commit()
    bot.send_message(user_id, 'Ваше имя успешно обновлено!')

def update_number(message):
    user_id = message.from_user.id
    if message.contact:
        new_number = message.contact.phone_number
        sql.execute('UPDATE users SET number=? WHERE tg_id=?;', (new_number, user_id))
        connection.commit()
        bot.send_message(user_id, 'Ваш номер телефона успешно обновлен!', reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, 'Пожалуйста отправьте номер через кнопку.')
        bot.register_next_step_nadler(message, update_number)

@bot.message_handler(commands=['my_profile'])
def my_profile(message):
    user_id = message.from_user.id
    user_data = sql.execute('SELECT name, number FROM users WHERE tg_id=?;',(user_id,)).fetchone()
    if user_data:
        name, number = user_data
        bot.send_message(user_id, f'Ваш профиль:\nИмя: {name}\nНомер телефона: {number}')
    else:
        bot.send_message(user_id, 'Вы не зарегистрированы.')


@bot.message_handler(commands=['delete_profile'])
def delete_profile(message):
    user_id = message.from_user.id
    if check_user(user_id):
        sql.execute('DELETE FROM users WHERE tg_id=?;', (user_id,))
        connection.commit()
        bot.send_message(user_id, 'Ваш профиль успешно удален.')
    else:
        bot.send_message(user_id, 'Вы не зарегистрированы')

@bot.message_handler(commands=['categories'])
def show_categories(message):
    categories = ['Рабы', 'ВидеоКарты', 'Овощи', 'Все для дома']
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        kb.add(types.KeyboardButton(text=category))

    bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=kb)
    bot.register_next_step_handler(message, show_products_in_category)

def show_products_in_category(message):
    category = message.text
    products = sql.execute('SELECT pr_name FROM products WHERE pr_category=?;', (category,)).fetchall()
    if products:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product in products:
            kb.add(types.KeyboardButton(text=product[0]))
        bot.send_message(message.chat.id, f'Продукты в категории "{category}":', reply_markup=kb)
    else:
        bot.send_message(message.chat.id, f'Нет продуктов в категории "{category}".')

@bot.message_handler(commands=['add_to_cart'])
def add_to_cart(message):
    bot.send_message(message.chat.id, "Введите ID продукта, который хотите добавить в корзину:")
    bot.register_next_step_handler(message, process_add_to_cart)


def process_add_to_cart(message):
    user_id = message.from_user.id
    product_id = int(message.text)
    sql.execute('INSERT INTO cart (user_id, user_product, product_amount) VALUES (?, ?, ?)', (user_id, product_id, 1))
    connection.commit()
    bot.send_message(message.chat.id, "Продукт добавлен в корзину!")

@bot.message_handler(commands=['view_cart'])
def view_cart(message):
    user_id = message.from_user.id
    cart_items = sql.execute('SELECT user_product, product_amount FROM cart WHERE user_id=?;', (user_id,)).fetchall()
    if cart_items:
        response = "Ваша корзина:\n"
        for item in cart_items:
            product_name = sql.execute('SELECT pr_name FROM products WHERE pr_id=?;', (item[0],)).fetchone()[0]
            response += f'{product_name} - {item[1]} шт.\n'
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")


@bot.message_handler(commands=['remove_from_cart'])
def remove_from_cart(message):
    bot.send_message(message.chat.id, "Введите ID продукта, который хотите удалить из корзины:")
    bot.register_next_step_handler(message, process_remove_from_cart)

def process_remove_from_cart(message):
    user_id = message.from_user.id
    product_id = int(message.text)
    sql.execute('DELETE FROM cart WHERE user_id=? AND user_product=?;', (user_id, product_id))
    connection.commit()
    bot.send_message(message.chat.id, "Продукт удален из корзины!")



bot.polling()
