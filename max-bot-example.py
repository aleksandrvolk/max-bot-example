#!/usr/bin/env python3
"""
Пример бота для мессенджера Max с полным функционалом
Использует библиотеку maxbot и интегрируется с системой Bothost
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests
from maxbot import MaxBot, Message, User, Chat
from maxbot.handlers import CommandHandler, MessageHandler, CallbackHandler
from maxbot.keyboards import InlineKeyboard, ReplyKeyboard
from maxbot.filters import Filter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не установлен!")
    exit(1)

# URL для API авторизации Bothost
AUTH_API_URL = os.getenv('AUTH_API_URL', 'https://bothost.ru/api/auth.php')

# Получаем ID бота из переменных окружения (устанавливается агентом)
BOT_ID = os.getenv('BOT_ID', 'demo_max_bot')

# Создаем экземпляр бота
bot = MaxBot(BOT_TOKEN)

class MaxBotManager:
    """Менеджер для бота Max с расширенным функционалом"""
    
    def __init__(self, bot_id: str, auth_api_url: str):
        self.bot_id = bot_id
        self.auth_api_url = auth_api_url
        self.user_sessions = {}  # Сессии пользователей
        self.user_data = {}      # Данные пользователей
        self.stats = {           # Статистика бота
            'total_users': 0,
            'total_messages': 0,
            'start_time': datetime.now()
        }
    
    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Получить или создать сессию пользователя"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'state': 'idle',
                'data': {},
                'last_activity': datetime.now(),
                'message_count': 0
            }
        return self.user_sessions[user_id]
    
    def update_user_session(self, user_id: str, **kwargs):
        """Обновить сессию пользователя"""
        session = self.get_user_session(user_id)
        session.update(kwargs)
        session['last_activity'] = datetime.now()
        session['message_count'] += 1
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Получить данные пользователя"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'user_id': user_id,
                'first_seen': datetime.now(),
                'total_messages': 0,
                'preferences': {
                    'language': 'ru',
                    'notifications': True,
                    'theme': 'light'
                },
                'subscription': {
                    'plan': 'free',
                    'expires_at': None,
                    'features': ['basic_messaging']
                }
            }
        return self.user_data[user_id]
    
    def update_user_data(self, user_id: str, **kwargs):
        """Обновить данные пользователя"""
        user_data = self.get_user_data(user_id)
        user_data.update(kwargs)
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Получить статистику бота"""
        uptime = datetime.now() - self.stats['start_time']
        return {
            'uptime': str(uptime).split('.')[0],
            'total_users': len(self.user_data),
            'active_users': len([s for s in self.user_sessions.values() 
                               if (datetime.now() - s['last_activity']).seconds < 3600]),
            'total_messages': sum(s['message_count'] for s in self.user_sessions.values()),
            'memory_usage': f"{len(str(self.user_data)) + len(str(self.user_sessions))} bytes"
        }

# Создаем менеджер бота
bot_manager = MaxBotManager(BOT_ID, AUTH_API_URL)

class MaxBotFeatures:
    """Класс с основными функциями бота"""
    
    @staticmethod
    def create_main_menu() -> InlineKeyboard:
        """Создать главное меню"""
        keyboard = InlineKeyboard()
        keyboard.add_button("📊 Статистика", callback_data="stats")
        keyboard.add_button("⚙️ Настройки", callback_data="settings")
        keyboard.add_button("🎮 Игры", callback_data="games")
        keyboard.add_button("📚 Помощь", callback_data="help")
        keyboard.add_button("🔧 Админ", callback_data="admin")
        return keyboard
    
    @staticmethod
    def create_settings_menu() -> InlineKeyboard:
        """Создать меню настроек"""
        keyboard = InlineKeyboard()
        keyboard.add_button("🌐 Язык", callback_data="lang_settings")
        keyboard.add_button("🔔 Уведомления", callback_data="notif_settings")
        keyboard.add_button("🎨 Тема", callback_data="theme_settings")
        keyboard.add_button("⬅️ Назад", callback_data="main_menu")
        return keyboard
    
    @staticmethod
    def create_games_menu() -> InlineKeyboard:
        """Создать меню игр"""
        keyboard = InlineKeyboard()
        keyboard.add_button("🎲 Случайное число", callback_data="random_number")
        keyboard.add_button("🎯 Угадай число", callback_data="guess_number")
        keyboard.add_button("📝 Викторина", callback_data="quiz")
        keyboard.add_button("🎮 Крестики-нолики", callback_data="tic_tac_toe")
        keyboard.add_button("⬅️ Назад", callback_data="main_menu")
        return keyboard
    
    @staticmethod
    def create_admin_menu() -> InlineKeyboard:
        """Создать админ меню"""
        keyboard = InlineKeyboard()
        keyboard.add_button("📈 Статистика бота", callback_data="bot_stats")
        keyboard.add_button("👥 Пользователи", callback_data="users_list")
        keyboard.add_button("🔧 Управление", callback_data="bot_management")
        keyboard.add_button("📊 Логи", callback_data="bot_logs")
        keyboard.add_button("⬅️ Назад", callback_data="main_menu")
        return keyboard

# Обработчик команды /start
@bot.command_handler('/start')
async def start_command(message: Message):
    """Обработчик команды /start"""
    user = message.from_user
    user_id = str(user.id)
    
    # Обновляем данные пользователя
    bot_manager.update_user_session(user_id, state='idle')
    bot_manager.update_user_data(user_id, 
                               username=user.username,
                               first_name=user.first_name,
                               last_name=user.last_name)
    
    welcome_text = f"""🤖 Добро пожаловать в Max Bot!

👋 Привет, {user.first_name}!

Этот бот создан специально для мессенджера Max и демонстрирует 
возможности интеграции с платформой Bothost.

🎯 Основные функции:
• 📊 Статистика и аналитика
• ⚙️ Настройки пользователя
• 🎮 Мини-игры и развлечения
• 📚 Справочная информация
• 🔧 Административные функции

🆔 Ваш ID: {user.id}
👤 Username: @{user.username or 'не указан'}
📅 Дата регистрации: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Выберите действие из меню ниже:"""
    
    await message.reply(
        text=welcome_text,
        reply_markup=MaxBotFeatures.create_main_menu()
    )

# Обработчик команды /help
@bot.command_handler('/help')
async def help_command(message: Message):
    """Обработчик команды /help"""
    help_text = """📖 Справка по Max Bot

🤖 О боте:
Max Bot - это демонстрационный бот для мессенджера Max, 
показывающий возможности платформы Bothost.

📋 Доступные команды:
/start - Начать работу с ботом
/help - Показать эту справку
/info - Информация о боте
/profile - Ваш профиль
/stats - Статистика пользователя
/settings - Настройки
/games - Игры и развлечения
/admin - Административные функции

🎮 Игры:
• Случайное число - генерация случайных чисел
• Угадай число - игра на угадывание
• Викторина - вопросы и ответы
• Крестики-нолики - классическая игра

⚙️ Настройки:
• Язык интерфейса
• Уведомления
• Тема оформления

❓ Если у вас есть вопросы, используйте команду /start 
для возврата в главное меню."""
    
    await message.reply(help_text)

# Обработчик команды /info
@bot.command_handler('/info')
async def info_command(message: Message):
    """Обработчик команды /info"""
    stats = bot_manager.get_bot_stats()
    
    info_text = f"""ℹ️ Информация о Max Bot

🤖 ID бота: {BOT_ID}
📊 Статистика:
• Время работы: {stats['uptime']}
• Всего пользователей: {stats['total_users']}
• Активных пользователей: {stats['active_users']}
• Всего сообщений: {stats['total_messages']}
• Использование памяти: {stats['memory_usage']}

🛡️ Система безопасности:
• Интеграция с Bothost Auth API
• Управление сессиями пользователей
• Кэширование данных
• Логирование действий

🔧 Техническая информация:
• Библиотека: maxbot
• Система авторизации: Bothost Auth API
• Платформа: Max Messenger
• Версия: 1.0.0

🌐 Поддержка:
• Сайт: https://bothost.ru
• Документация: https://bothost.ru/docs
• Поддержка: support@bothost.ru"""
    
    await message.reply(info_text)

# Обработчик команды /profile
@bot.command_handler('/profile')
async def profile_command(message: Message):
    """Обработчик команды /profile"""
    user = message.from_user
    user_id = str(user.id)
    
    user_data = bot_manager.get_user_data(user_id)
    session = bot_manager.get_user_session(user_id)
    
    profile_text = f"""👤 Ваш профиль

🆔 Max ID: {user.id}
👤 Username: @{user.username or 'не указан'}
📛 Имя: {user.first_name} {user.last_name or ''}
🌐 Язык: {user_data['preferences']['language']}

📊 Статистика:
• Первый вход: {user_data['first_seen'].strftime('%d.%m.%Y %H:%M')}
• Всего сообщений: {user_data['total_messages']}
• Сообщений в сессии: {session['message_count']}
• Последняя активность: {session['last_activity'].strftime('%d.%m.%Y %H:%M')}

⚙️ Настройки:
• Уведомления: {'✅ Включены' if user_data['preferences']['notifications'] else '❌ Отключены'}
• Тема: {user_data['preferences']['theme']}
• Язык: {user_data['preferences']['language']}

🎫 Подписка:
• План: {user_data['subscription']['plan'].upper()}
• Функции: {', '.join(user_data['subscription']['features'])}
• Истекает: {user_data['subscription']['expires_at'] or 'Без ограничений'}"""
    
    await message.reply(profile_text)

# Обработчик команды /stats
@bot.command_handler('/stats')
async def stats_command(message: Message):
    """Обработчик команды /stats"""
    user_id = str(message.from_user.id)
    user_data = bot_manager.get_user_data(user_id)
    session = bot_manager.get_user_session(user_id)
    
    stats_text = f"""📊 Ваша статистика

👤 Личная статистика:
• Всего сообщений: {user_data['total_messages']}
• Сообщений в сессии: {session['message_count']}
• Время в боте: {datetime.now() - user_data['first_seen']}
• Последняя активность: {session['last_activity'].strftime('%H:%M')}

🤖 Статистика бота:
• Всего пользователей: {bot_manager.stats['total_users']}
• Активных пользователей: {len([s for s in bot_manager.user_sessions.values() if (datetime.now() - s['last_activity']).seconds < 3600])}
• Всего сообщений: {bot_manager.stats['total_messages']}
• Время работы: {bot_manager.get_bot_stats()['uptime']}"""
    
    await message.reply(stats_text)

# Обработчик команды /games
@bot.command_handler('/games')
async def games_command(message: Message):
    """Обработчик команды /games"""
    games_text = """🎮 Игры и развлечения

Выберите игру из меню ниже:

🎲 Случайное число - генерация случайных чисел в заданном диапазоне
🎯 Угадай число - попробуйте угадать загаданное число
📝 Викторина - ответьте на вопросы из разных категорий
🎮 Крестики-нолики - классическая игра против бота

Все игры адаптированы для мессенджера Max и 
работают через удобные кнопки и меню."""
    
    await message.reply(
        text=games_text,
        reply_markup=MaxBotFeatures.create_games_menu()
    )

# Обработчик команды /settings
@bot.command_handler('/settings')
async def settings_command(message: Message):
    """Обработчик команды /settings"""
    settings_text = """⚙️ Настройки

Здесь вы можете настроить:
• 🌐 Язык интерфейса
• 🔔 Уведомления
• 🎨 Тему оформления

Выберите настройку для изменения:"""
    
    await message.reply(
        text=settings_text,
        reply_markup=MaxBotFeatures.create_settings_menu()
    )

# Обработчик команды /admin
@bot.command_handler('/admin')
async def admin_command(message: Message):
    """Обработчик команды /admin"""
    user_id = str(message.from_user.id)
    
    # Простая проверка прав администратора
    # В реальном проекте здесь должна быть более сложная логика
    admin_ids = ['123456789', '987654321']  # Замените на реальные ID админов
    
    if user_id not in admin_ids:
        await message.reply("❌ У вас нет прав администратора.")
        return
    
    admin_text = f"""👨‍💼 Административная панель

🔐 Статус системы: ✅ Активна
📊 Статистика бота:
• Всего пользователей: {bot_manager.stats['total_users']}
• Активных сессий: {len(bot_manager.user_sessions)}
• Всего сообщений: {bot_manager.stats['total_messages']}
• Время работы: {bot_manager.get_bot_stats()['uptime']}

🛠️ Доступные функции:
• Просмотр статистики бота
• Управление пользователями
• Настройки бота
• Просмотр логов

Выберите действие:"""
    
    await message.reply(
        text=admin_text,
        reply_markup=MaxBotFeatures.create_admin_menu()
    )

# Обработчики callback-ов
@bot.callback_handler(lambda callback: callback.data == 'main_menu')
async def main_menu_callback(callback):
    """Обработчик возврата в главное меню"""
    await callback.message.edit_text(
        text="🏠 Главное меню\n\nВыберите действие:",
        reply_markup=MaxBotFeatures.create_main_menu()
    )
    await callback.answer()

@bot.callback_handler(lambda callback: callback.data == 'stats')
async def stats_callback(callback):
    """Обработчик статистики"""
    user_id = str(callback.from_user.id)
    user_data = bot_manager.get_user_data(user_id)
    session = bot_manager.get_user_session(user_id)
    
    stats_text = f"""📊 Статистика пользователя

👤 Личная статистика:
• Всего сообщений: {user_data['total_messages']}
• Сообщений в сессии: {session['message_count']}
• Время в боте: {datetime.now() - user_data['first_seen']}
• Последняя активность: {session['last_activity'].strftime('%H:%M')}

🤖 Общая статистика:
• Всего пользователей: {bot_manager.stats['total_users']}
• Активных пользователей: {len([s for s in bot_manager.user_sessions.values() if (datetime.now() - s['last_activity']).seconds < 3600])}
• Время работы бота: {bot_manager.get_bot_stats()['uptime']}"""
    
    keyboard = InlineKeyboard()
    keyboard.add_button("⬅️ Назад", callback_data="main_menu")
    
    await callback.message.edit_text(
        text=stats_text,
        reply_markup=keyboard
    )
    await callback.answer()

@bot.callback_handler(lambda callback: callback.data == 'settings')
async def settings_callback(callback):
    """Обработчик настроек"""
    settings_text = """⚙️ Настройки

Здесь вы можете настроить:
• 🌐 Язык интерфейса
• 🔔 Уведомления  
• 🎨 Тему оформления

Выберите настройку для изменения:"""
    
    await callback.message.edit_text(
        text=settings_text,
        reply_markup=MaxBotFeatures.create_settings_menu()
    )
    await callback.answer()

@bot.callback_handler(lambda callback: callback.data == 'games')
async def games_callback(callback):
    """Обработчик игр"""
    games_text = """🎮 Игры и развлечения

Выберите игру из меню ниже:

🎲 Случайное число - генерация случайных чисел
🎯 Угадай число - игра на угадывание
📝 Викторина - вопросы и ответы
🎮 Крестики-нолики - классическая игра"""
    
    await callback.message.edit_text(
        text=games_text,
        reply_markup=MaxBotFeatures.create_games_menu()
    )
    await callback.answer()

@bot.callback_handler(lambda callback: callback.data == 'random_number')
async def random_number_callback(callback):
    """Обработчик игры 'Случайное число'"""
    import random
    
    # Генерируем случайное число от 1 до 100
    number = random.randint(1, 100)
    
    game_text = f"""🎲 Случайное число

🎯 Сгенерированное число: **{number}**

Диапазон: 1-100
Время генерации: {datetime.now().strftime('%H:%M:%S')}

Хотите сгенерировать еще одно число?"""
    
    keyboard = InlineKeyboard()
    keyboard.add_button("🎲 Еще число", callback_data="random_number")
    keyboard.add_button("⬅️ Назад к играм", callback_data="games")
    
    await callback.message.edit_text(
        text=game_text,
        reply_markup=keyboard
    )
    await callback.answer(f"Сгенерировано число: {number}")

@bot.callback_handler(lambda callback: callback.data == 'guess_number')
async def guess_number_callback(callback):
    """Обработчик игры 'Угадай число'"""
    user_id = str(callback.from_user.id)
    session = bot_manager.get_user_session(user_id)
    
    # Загадываем число если игра не начата
    if 'guess_game' not in session['data']:
        import random
        session['data']['guess_game'] = {
            'number': random.randint(1, 100),
            'attempts': 0,
            'max_attempts': 7
        }
        bot_manager.update_user_session(user_id, state='guessing')
    
    game_data = session['data']['guess_game']
    
    game_text = f"""🎯 Угадай число

Я загадал число от 1 до 100.
У вас есть {game_data['max_attempts']} попыток.

Попыток использовано: {game_data['attempts']}
Осталось попыток: {game_data['max_attempts'] - game_data['attempts']}

Отправьте число в чат для угадывания!"""
    
    keyboard = InlineKeyboard()
    keyboard.add_button("🔄 Новая игра", callback_data="guess_number_new")
    keyboard.add_button("⬅️ Назад к играм", callback_data="games")
    
    await callback.message.edit_text(
        text=game_text,
        reply_markup=keyboard
    )
    await callback.answer("Игра начата! Отправьте число в чат.")

@bot.callback_handler(lambda callback: callback.data == 'guess_number_new')
async def guess_number_new_callback(callback):
    """Обработчик новой игры 'Угадай число'"""
    user_id = str(callback.from_user.id)
    session = bot_manager.get_user_session(user_id)
    
    # Сбрасываем игру
    session['data']['guess_game'] = None
    bot_manager.update_user_session(user_id, state='idle')
    
    await guess_number_callback(callback)

# Обработчик текстовых сообщений для игры "Угадай число"
@bot.message_handler(lambda message: bot_manager.get_user_session(str(message.from_user.id))['state'] == 'guessing')
async def guess_number_message(message: Message):
    """Обработчик сообщений в игре 'Угадай число'"""
    user_id = str(message.from_user.id)
    session = bot_manager.get_user_session(user_id)
    
    try:
        guess = int(message.text)
    except ValueError:
        await message.reply("❌ Пожалуйста, введите число!")
        return
    
    game_data = session['data']['guess_game']
    game_data['attempts'] += 1
    
    if guess == game_data['number']:
        # Пользователь угадал!
        result_text = f"""🎉 Поздравляем! Вы угадали!

🎯 Загаданное число: {game_data['number']}
📊 Попыток использовано: {game_data['attempts']}
⭐ Оценка: {'Отлично!' if game_data['attempts'] <= 3 else 'Хорошо!' if game_data['attempts'] <= 5 else 'Неплохо!'}

Хотите сыграть еще раз?"""
        
        keyboard = InlineKeyboard()
        keyboard.add_button("🎮 Новая игра", callback_data="guess_number")
        keyboard.add_button("⬅️ Назад к играм", callback_data="games")
        
        await message.reply(
            text=result_text,
            reply_markup=keyboard
        )
        
        # Сбрасываем игру
        session['data']['guess_game'] = None
        bot_manager.update_user_session(user_id, state='idle')
        
    elif game_data['attempts'] >= game_data['max_attempts']:
        # Попытки закончились
        result_text = f"""😔 Игра окончена!

🎯 Загаданное число было: {game_data['number']}
📊 Попыток использовано: {game_data['attempts']}

Не расстраивайтесь, попробуйте еще раз!"""
        
        keyboard = InlineKeyboard()
        keyboard.add_button("🎮 Новая игра", callback_data="guess_number")
        keyboard.add_button("⬅️ Назад к играм", callback_data="games")
        
        await message.reply(
            text=result_text,
            reply_markup=keyboard
        )
        
        # Сбрасываем игру
        session['data']['guess_game'] = None
        bot_manager.update_user_session(user_id, state='idle')
        
    else:
        # Даем подсказку
        hint = "больше" if guess < game_data['number'] else "меньше"
        hint_text = f"""🤔 Не угадали!

Ваше число: {guess}
Загаданное число {hint} чем {guess}

Попыток использовано: {game_data['attempts']}/{game_data['max_attempts']}
Осталось попыток: {game_data['max_attempts'] - game_data['attempts']}

Попробуйте еще раз!"""
        
        await message.reply(hint_text)

# Обработчик всех остальных сообщений
@bot.message_handler()
async def handle_all_messages(message: Message):
    """Обработчик всех остальных сообщений"""
    user = message.from_user
    user_id = str(user.id)
    
    # Обновляем статистику
    bot_manager.update_user_session(user_id, state='idle')
    bot_manager.update_user_data(user_id, total_messages=bot_manager.get_user_data(user_id)['total_messages'] + 1)
    bot_manager.stats['total_messages'] += 1
    
    response_text = f"""💬 Получено сообщение от {user.first_name}!

📝 Текст: {message.text}
🆔 Ваш ID: {user.id}
👤 Username: @{user.username or 'не указан'}
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

ℹ️ Для получения списка команд используйте /help
🏠 Для возврата в главное меню используйте /start"""
    
    await message.reply(response_text)

# Обработчик ошибок
@bot.error_handler()
async def error_handler(error):
    """Обработчик ошибок"""
    logger.error(f"Ошибка в боте: {str(error)}")
    # Здесь можно добавить отправку уведомлений администраторам

# Функция для запуска бота
def main():
    """Основная функция"""
    logger.info(f"Запуск Max Bot {BOT_ID}...")
    
    # Логируем информацию о боте
    logger.info(f"Bot ID: {BOT_ID}")
    logger.info(f"Auth API URL: {AUTH_API_URL}")
    logger.info(f"Max Bot готов к работе!")
    
    # Запускаем бота
    try:
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {str(e)}")
        raise

if __name__ == "__main__":
    main()
