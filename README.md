# 🤖 Max Bot Example

**Полнофункциональный бот для мессенджера Max с интеграцией Bothost**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![Bothost](https://img.shields.io/badge/Bothost-Integrated-green.svg)](https://bothost.ru)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🚀 **Готовый к использованию пример бота** с играми, статистикой, админкой и полной инфраструктурой для развертывания на платформе Bothost.

## ✨ Особенности

- 🎮 **Игры и развлечения** - случайные числа, угадай число, викторина
- 📊 **Статистика и аналитика** - метрики пользователей и бота
- ⚙️ **Настройки пользователя** - язык, уведомления, тема
- 🔧 **Административные функции** - управление пользователями
- 🐳 **Docker готовность** - контейнеризация и Docker Compose
- 📈 **Мониторинг** - Prometheus + Grafana дашборды
- 🗄️ **База данных** - PostgreSQL + Redis кэширование
- 🔒 **Безопасность** - валидация, rate limiting, авторизация

## 🚀 Быстрый старт

```bash
# Клонирование
git clone https://github.com/aleksandrvolk/max-bot-example.git
cd max-bot-example

# Установка зависимостей
pip install -r requirements.txt

# Настройка
cp env.example .env
# Отредактируйте .env с вашими настройками

# Запуск
python max-bot-example.py
```

## 🐳 Docker

```bash
# Запуск полной инфраструктуры
docker-compose up -d
```

Включает: бот, PostgreSQL, Redis, Prometheus, Grafana, Nginx

## 🔗 Интеграция с Bothost

1. Загрузите код в GitHub
2. В панели Bothost создайте бота с Git URL
3. Добавьте переменные окружения
4. Развертывание автоматически!

## 📋 Команды бота

- `/start` - Начать работу
- `/help` - Справка
- `/games` - Игры
- `/stats` - Статистика
- `/settings` - Настройки
- `/admin` - Админка

## 🛠️ Технологии

- **Python 3.11+** - основной язык
- **maxbot** - библиотека для Max Messenger
- **Docker** - контейнеризация
- **PostgreSQL** - база данных
- **Redis** - кэширование
- **Prometheus** - метрики
- **Grafana** - визуализация

## 📚 Документация

- [Bothost Platform](https://bothost.ru)
- [Max Messenger API](https://max.messenger.com/api)
- [Docker Documentation](https://docs.docker.com)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE)

## 🆘 Поддержка

- 📧 Email: support@bothost.ru
- 💬 Telegram: @bothost_support
- 📚 Документация: https://bothost.ru/docs

---

**Создано с ❤️ командой Bothost**
