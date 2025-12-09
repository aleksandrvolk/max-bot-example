"""
Простейший пример бота на MaxBot без Telegram и без вебхуков.
Используется интерактивный ввод из консоли.
"""

from maxbot import MaxBot

# Инициализируем MaxBot с простым диалогом
bot = MaxBot.inline(
    """
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
    """
)


def main() -> None:
    """Запуск простого интерактивного бота."""
    print("🚀 MaxBot запущен. Введите '/exit' для выхода.")
    while True:
        try:
            user_text = input("🧑: ").strip()
            if user_text.lower() in {"/exit", "/quit"}:
                print("👋 Выход.")
                break
            if not user_text:
                continue

            message = {"text": user_text}
            commands = bot.process_message(message)

            if not commands:
                print("🤖: (нет ответа)")
                continue

            for command in commands:
                reply = command.get("text")
                if reply:
                    print(f"🤖: {reply}")
                else:
                    print(f"🤖: (команда без текста) {command}")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Выход.")
            break
        except Exception as exc:
            print(f"⚠️ Ошибка: {exc}")


if __name__ == "__main__":
    main()
