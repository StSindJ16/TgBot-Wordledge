"""ИМПОРТЫ"""
from datetime import datetime
import telebot
import random
import threading
import time
from pytz import timezone


# Токен
TOKEN = "7241678368:AAEpI95n_4Dvd9i6xHt0x1ecf17ZKZucYsk"
bot = telebot.TeleBot(TOKEN)


# Данные пользователей
user_data = {}
leaderboard = {}  # Лидерборд для всех игроков



"""ОБРАБОТКИ СЛОВ"""
def get_random_word(k):
    with open('words.txt', 'r', encoding="utf-8") as f:
        words = f.read().splitlines()
    words = [word for word in words if len(word) == k]
    return random.choice(words)

# Проверка слова в словаре
def input_check(k, guess):
    with open('words.txt', 'r', encoding="utf-8") as f:
        words = f.read().splitlines()
    return len(guess) == k and guess in words

# Логика проверки слова
def result(guess, word):
    feedback = []
    for i, letter in enumerate(guess):
        if letter == word[i]:
            feedback.append(f"{letter} - ✓")
        elif letter in word:
            feedback.append(f"{letter} - ?")
        else:
            feedback.append(f"{letter} - x")
    return "\n".join(feedback)
"""ОБРАБОТКИ СЛОВ (КОНЕЦ)"""



"""/restart и /start с /help"""
@bot.message_handler(commands=['start'])
def start_game(message):
    user_data[message.chat.id] = {'state': 'waiting_length'}
    bot.send_message(message.chat.id, "Добро пожаловать в игру 'Угадай слово'! Введите длину слова (от 2 до 24):")

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "Добро пожаловать в игру 'Угадай слово'!\n\n"
        "Цель игры: Угадать загаданное слово за ограниченное количество попыток.\n\n"
        "Доступные команды:\n"
        "/start - Начать новую игру.\n"
        "/restart - Перезапустить текущую игру.\n"
        "/rating - Играть в рейтинговом режиме (результаты учитываются в общем рейтинге).\n"
        "/globalleaderboard - показать топ-30 игроков по миру на данный момент.\n"
        "/leaderboard - Показать текущий рейтинг игроков (работает только в группах).\n"
        "/help - Показать это сообщение с объяснением правил и команд.\n"
        "/myscore - показать ваш текущий счёт \n\n"
        "Принцип игры:\n"
        "1. Вы вводите длину слова, которое хотите отгадать (от 2 до 25).\n"
        "2. Укажите количество попыток для угадывания слова.\n"
        "3. Бот загадает слово, и вы начинаете угадывать.\n"
        "   - Если буква на своём месте, она помечается как ✓.\n"
        "   - Если буква есть в слове, но на другом месте, она помечается как ?.\n"
        "   - Если буквы нет в слове, она помечается как x.\n"
        "4. В рейтинговом режиме вы получаете очки за угаданное слово.\n\n"
        "Удачи в игре!"
    )
    bot.send_message(message.chat.id, help_text)
@bot.message_handler(commands=['restart'])
def restart_game(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data.pop(chat_id)  # Удаляем данные пользователя, если они есть
    bot.send_message(chat_id, "Игра перезапущена. Введите \n /start, чтобы начать заново.")
#333 (напоминалка-тесты(позже удлаить))
"""/restart и /start с /help (КОНЕЦ)"""



#ЛИМИТ РЕЙТА НА ДЕНЬ
# Дополнительный словарь для отслеживания игр пользователей
rating_games_count = {}
def reset_daily_limits():
    """Функция для сброса счётчиков игр в конце дня."""
    global rating_games_count
    rating_games_count = {}

# /rating обработка
@bot.message_handler(commands=['rating'])
def start_rating_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Получение текущей даты
    current_date = datetime.now().date()

    # Init данных для пользователя
    if user_id not in rating_games_count:
        rating_games_count[user_id] = {'date': current_date, 'games': 0}

    # Другая дата=сброс счетчика
    if rating_games_count[user_id]['date'] < current_date:
        rating_games_count[user_id] = {'date': current_date, 'games': 0}

    # Проверка, колько игр сыграл юзер сегодня
    if rating_games_count[user_id]['games'] >= 3:
        bot.send_message(chat_id, "Вы уже сыграли 3 игры в рейтинговом режиме сегодня. Попробуйте снова завтра!")
        return

    # Увел кол-ва сыгр игр в рейт
    rating_games_count[user_id]['games'] += 1

    user_data[chat_id] = {'state': 'waiting_length_rating'}
    bot.send_message(chat_id, "Добро пожаловать в игру 'Угадай слово' в рейтинге! Введите длину слова (от 2 до 24):")


"""ЛИДЕРБОРДЫ"""
# Команда /globalleaderboard
@bot.message_handler(commands=['globalleaderboard'])
def show_leaderboard(message):
    if leaderboard:
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1]['points'], reverse=True)
        # Ограничиваем количество выводимых записей до 30
        top_30_leaders = sorted_leaderboard[:30]
        leaderboard_text = "Текущий рейтинг:\n"
        for rank, (player_id, data) in enumerate(top_30_leaders, 1):
            leaderboard_text += f"{rank}. {data['name']} - {data['points']} баллов\n"
        bot.send_message(message.chat.id, leaderboard_text)
    else:
        bot.send_message(message.chat.id, "Рейтинг пока пуст.")


# Команда /leaderboard
@bot.message_handler(commands=['leaderboard'])
def local_leaderboard(message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    if chat_type == 'private':
        bot.reply_to(message, "Эта функция доступна только в группах!")

# Получаем список участников чата
    else:
        chat_members = [
            member.user.id
            for member in bot.get_chat_administrators(chat_id)
        ]

    # Фильтруем глобальный лидерборд, оставляя только участников данного чата
        filtered_leaderboard = {
            user_id: data
            for user_id, data in leaderboard.items()
            if user_id in chat_members
        }

        if filtered_leaderboard:
            sorted_local_leaderboard = sorted(filtered_leaderboard.items(), key=lambda x: x[1]['points'], reverse=True)

            leaderboard_text = "Местный рейтинг:\n"
            for rank, (player_id, data) in enumerate(sorted_local_leaderboard, 1):
                leaderboard_text += f"{rank}. {data['name']} - {data['points']} баллов\n"

            bot.send_message(chat_id, leaderboard_text)
        else:
            bot.send_message(chat_id, "Нет данных для местного рейтинга.")

# Команда /myscore
@bot.message_handler(commands=['myscore'])
def my_score(message):
    user_id = message.from_user.id
    if user_id in leaderboard:
        score = leaderboard[user_id]['points']
        namen = message.from_user.first_name
        bot.send_message(message.chat.id, f"Ваши очки:  {namen} {score}")
    else:
        bot.send_message(message.chat.id, "У вас пока нет очков. \n Сыграйте в "
                                          "рейтинговую игру, чтобы заработать очки!")
"""КОНЕЦ ЛИДЕРБОРДОВ"""


"""Обработка сообщений от пользователей"""
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "Введите /start для начала игры.")
        return

    state = user_data[chat_id].get('state')

    if state == 'waiting_length':
        try:
            k = int(message.text)
            if 2 <= k < 25:
                user_data[chat_id]['length'] = k
                user_data[chat_id]['state'] = 'waiting_attempts'
                bot.send_message(chat_id, "Введите количество попыток:")
            else:
                bot.send_message(chat_id, "Введите число от 2 до 24!")
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите число от 2 до 24!")

    elif state == 'waiting_attempts':
        try:
            n = int(message.text)
            if n > 0:
                user_data[chat_id]['attempts'] = n
                user_data[chat_id]['word'] = get_random_word(user_data[chat_id]['length'])
                user_data[chat_id]['current_attempt'] = 0
                user_data[chat_id]['state'] = 'playing'
                bot.send_message(chat_id, "Игра началась! Введите ваше первое слово:")
            else:
                bot.send_message(chat_id, "Количество попыток должно быть больше нуля!")
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите положительное число!")
    elif state == 'playing':
        guess = message.text.lower()
        k = user_data[chat_id]['length']
        if not input_check(k, guess):
            bot.send_message(chat_id, f"Ваше слово должно быть длиной {k} символов и содержаться в словаре!")
            return

        user_data[chat_id]['current_attempt'] += 1
        word = user_data[chat_id]['word']
        if guess == word:
            bot.send_message(chat_id, f"Поздравляем! Вы угадали слово: {word}!")
            bot.send_message(chat_id, "Введите /restart для перезапуска.")
            user_data.pop(chat_id)
        else:
            feedback = result(guess, word)
            remaining_attempts = user_data[chat_id]["attempts"] - user_data[chat_id]["current_attempt"]
            bot.send_message(chat_id, f"Результат:\n{feedback}")
            if user_data[chat_id]['current_attempt'] >= user_data[chat_id]['attempts']:
                bot.send_message(chat_id, f"Вы проиграли! Загаданное слово было: {word}.")
                bot.send_message(chat_id, "Введите /restart для перезапуска.")
                user_data.pop(chat_id)
            else:
                bot.send_message(chat_id, f"Осталось попыток: {remaining_attempts}")
#33 (напонминалка)
    elif state == 'waiting_length_rating':
        try:
            k = int(message.text)
            if 2 <= k < 25:
                user_data[chat_id]['length'] = k
                user_data[chat_id]['attempts'] = 7  # Устанавливаем фиксированное количество попыток
                user_data[chat_id]['word'] = get_random_word(k)
                user_data[chat_id]['current_attempt'] = 0
                user_data[chat_id]['state'] = 'playing_rating'
                bot.send_message(chat_id, "Игра началась! У вас 7 попыток. Введите ваше первое слово:")
            else:
                bot.send_message(chat_id, "Введите число от 2 до 24!")
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите число от 2 до 24!")

    elif state == 'playing_rating':

        guess = message.text.lower()

        if 'length' not in user_data[chat_id] or 'word' not in user_data[chat_id]:
            bot.send_message(chat_id, "Произошла ошибка. Начните игру заново с команды /restart.")

            return

        k = user_data[chat_id]['length']

        word = user_data[chat_id]['word']

        if not input_check(k, guess):
            bot.send_message(chat_id, f"Ваше слово должно быть длиной {k} символов и содержаться в словаре!")

            return

        user_data[chat_id]['current_attempt'] += 1

        if guess == word:
# Подсчёт очков
            points = len(word) * 7
            points = points / user_data[chat_id]['current_attempt']
            points=round(points, 2)
# Добавление в лидерборд
            user_id = message.from_user.id
            user_name = message.from_user.first_name
            if user_id in leaderboard:
                leaderboard[user_id]['points'] += points
            else:
                leaderboard[user_id] = {'name': user_name, 'points': points}
            bot.send_message(chat_id, f"Поздравляем! Вы угадали слово: {word}. \n Баллы: {leaderboard[user_id]['points']}. "
                                      f"\n За ответ вы заработали:   {points} баллов")
# Обновление лидерборда
            bot.send_message(chat_id, "Введите /restart для перезапуска.")
            user_data.pop(chat_id)

        else:
            feedback = result(guess, word)
            remaining_attempts = user_data[chat_id]["attempts"] - user_data[chat_id]["current_attempt"]
            bot.send_message(chat_id, f"Результат:\n{feedback}")
            if user_data[chat_id]['current_attempt'] >= user_data[chat_id]['attempts']:
                bot.send_message(chat_id, f"Вы проиграли! Загаданное слово было: {word}.")
                bot.send_message(chat_id, "Введите /restart для перезапуска.")
                user_data.pop(chat_id)

            else:
                bot.send_message(chat_id, f"Осталось попыток: {remaining_attempts}")
"""КОНЕЦ ОБРАБОТКИ СООБЩЕНИЙ"""

# Обнул рейт
def reset_leaderboard():
    global leaderboard
    leaderboard.clear()
    reset_message = "Рейтинг обнулён! Начинаем новую неделю. Удачи всем игрокам!"
    for chat_id in user_data.keys():
        try:
            bot.send_message(chat_id, reset_message)
        except Exception as e:
            print(f"Не удалось отправить сообщение в чат {chat_id}: {e}")

# Отслеж времени и обнул рейта в вс 23:59 по мск
def schedule_reset():
    while True:
        now = datetime.now(timezone('Europe/Moscow'))
        # Проверяем, что сейчас воскресенье и время 23:59
        if now.weekday() == 6 and now.hour == 23 and now.minute == 59:
            reset_leaderboard()
            time.sleep(60)  # Чтоб повторно не сработало
        time.sleep(1)

# Запускаем функцию отслеживания времени в отдельном потоке
reset_thread = threading.Thread(target=schedule_reset)
reset_thread.daemon = True
reset_thread.start()

# Запуск бота
bot.polling(none_stop=True)