"""
Пример бота на MaxBot для Telegram
Исправленная версия без импорта Message, User, Chat
"""

import os
import asyncio
from fastapi import FastAPI, Request
from maxbot import MaxBot
import uvicorn

# Получаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
PORT = int(os.getenv("PORT", "3000"))

# Создаем FastAPI приложение
app = FastAPI()

# Инициализируем MaxBot с диалогом
bot = MaxBot.inline("""
    dialog:
      - condition: message.text.lower() in ['hello', 'hi', 'привет', 'здравствуй']
        response: |
          Привет! Я бот на MaxBot.
          Как дела?
      
      - condition: message.text.lower() in ['good bye', 'bye', 'пока', 'до свидания']
        response: |
          До свидания! Удачи!
      
      - condition: message.text == '/start'
        response: |
          Добро пожаловать! Я бот на MaxBot.
          Напишите "привет" или "hello" для начала.
      
      - condition: true
        response: |
          Извините, я не понял. Попробуйте написать "привет" или "/start".
""")

def telegram_to_maxbot(telegram_update: dict) -> dict:
    """
    Конвертирует обновление Telegram в формат MaxBot
    """
    message = telegram_update.get("message", {})
    if not message:
        return None
    
    return {
        "text": message.get("text", ""),
        "user_id": message.get("from", {}).get("id"),
        "chat_id": message.get("chat", {}).get("id"),
    }

def maxbot_to_telegram(commands: list, chat_id: int) -> list:
    """
    Конвертирует команды MaxBot в запросы к Telegram API
    """
    telegram_requests = []
    for command in commands:
        if "text" in command:
            telegram_requests.append({
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": command["text"]
            })
    return telegram_requests

@app.get("/health")
async def health() -> dict:
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    """
    Обработчик webhook от Telegram
    """
    try:
        update = await request.json()
        
        # Конвертируем обновление Telegram в формат MaxBot
        message = telegram_to_maxbot(update)
        if not message:
            return {"ok": True}
        
        # Обрабатываем сообщение через MaxBot
        commands = bot.process_message(message)
        
        # Конвертируем команды MaxBot в запросы к Telegram API
        chat_id = message.get("chat_id")
        if chat_id and commands:
            telegram_requests = maxbot_to_telegram(commands, chat_id)
            
            # Здесь можно отправить запросы к Telegram API
            # Для примера просто возвращаем их
            # В реальном боте нужно использовать библиотеку для работы с Telegram API
            # Например: python-telegram-bot или aiogram
            
            return {
                "ok": True,
                "commands": telegram_requests
            }
        
        return {"ok": True}
    
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    print(f"Starting MaxBot server on port {PORT}")
    print(f"Webhook path: {WEBHOOK_PATH}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

