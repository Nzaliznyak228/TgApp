#!/usr/bin/env python3
"""
Year Review Telegram Bot + Mini App
Всё в одном файле - просто запустите и всё работает!

Использование:
    python bot.py
    
Откройте Telegram и напишите вашему боту /start
"""

import os
import sys
import asyncio
import json
import hmac
import hashlib
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, BotCommand
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8534379117:AAHQ6iHykbjedmOXrHs6gJWSpghoznlRqkY")
BOT_USERNAME = os.getenv("BOT_USERNAME", "YearReviewBot")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "True") == "True"

print(f"""
╔════════════════════════════════════════════════╗
║   Year Review Bot + Mini App (ALL IN ONE)      ║
╚════════════════════════════════════════════════╝

📱 Bot Token: {BOT_TOKEN[:20]}...
🌐 Web Server: http://localhost:{PORT}
🎯 Mini App: http://localhost:{PORT}/app
📊 API: http://localhost:{PORT}/api

Запуск...
""")

# ============================================================================
# FLASK APP (Web Server + API)
# ============================================================================

app = Flask(__name__)
CORS(app)

# Кэш статистики пользователей
USER_STATS_CACHE = {}


def generate_user_stats(user_id: int) -> dict:
    """Генерирует статистику для пользователя"""
    if user_id in USER_STATS_CACHE:
        return USER_STATS_CACHE[user_id]
    
    stats = {
        "user_id": user_id,
        "username": f"User_{user_id}",
        "messages_sent": 4287,
        "chats_used": 156,
        "calls_made": 89,
        "voice_messages": 234,
        "stickers_sent": 1200,
        "photos_shared": 456,
        "videos_shared": 123,
        "files_shared": 78,
        "active_hours": "21:00-23:00",
        "most_active_day": "Friday",
        "favorite_emoji": "😂",
        "forwarded_messages": 890,
        "replied_messages": 456,
        "edited_messages": 234,
        "deleted_messages": 156,
        "generated_at": datetime.now().isoformat()
    }
    
    USER_STATS_CACHE[user_id] = stats
    return stats


def verify_telegram_data(init_data: str) -> bool:
    """Проверить подпись данных от Telegram Mini App"""
    try:
        data = {}
        for item in init_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                data[key] = value
        
        hash_value = data.pop('hash', '')
        
        check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
        
        secret_key = hmac.new(
            b'WebAppData',
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        computed_hash = hmac.new(
            secret_key,
            check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return computed_hash == hash_value
    except Exception as e:
        print(f"❌ Ошибка проверки подписи: {e}")
        return False


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка статуса API"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Year Review Mini App"
    })


@app.route('/api/init', methods=['POST'])
def api_init():
    """Инициализация Mini App"""
    try:
        init_data = request.json.get('initData', '')
        
        if not verify_telegram_data(init_data):
            return jsonify({"error": "Invalid signature"}), 401
        
        # Парсим данные пользователя
        user_data = {}
        for item in init_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                user_data[key] = value
        
        return jsonify({
            "status": "ok",
            "user_data": user_data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/stats/<int:user_id>', methods=['GET'])
def get_user_stats(user_id: int):
    """Получить статистику пользователя"""
    try:
        stats = generate_user_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============================================================================
# WEB APP ROUTES (Frontend)
# ============================================================================

@app.route('/app')
@app.route('/app/')
@app.route('/')
def serve_index():
    """Главная страница Mini App"""
    return send_from_directory('web', 'index.html')


@app.route('/styles.css')
def serve_css():
    """CSS стили"""
    return send_from_directory('web', 'styles.css')


@app.route('/app.js')
def serve_js():
    """JavaScript приложения"""
    return send_from_directory('web', 'app.js')


# ============================================================================
# TELEGRAM BOT
# ============================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

WEBAPP_URL = f"http://localhost:{PORT}/app"


async def set_default_commands():
    """Установить команды бота"""
    commands = [
        BotCommand(command="start", description="📊 Start Year Review"),
        BotCommand(command="help", description="ℹ️ Help"),
    ]
    await bot.set_my_commands(commands)


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка /start"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 View Your Year Review",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    
    welcome_text = (
        "👋 Welcome to Year Review Bot!\n\n"
        "This bot shows you your amazing Telegram year statistics!\n\n"
        "📊 **13 Interactive Slides:**\n"
        "1. 🚀 Rising Star\n"
        "2. 📱 Chat Master\n"
        "3. 🎤 Voice Legend\n"
        "4. 📸 Photo Enthusiast\n"
        "5. 🎬 Movie Lover\n"
        "6. 📎 File Organizer\n"
        "7. ⏰ Night Owl\n"
        "8. 🎯 Productivity Guru\n"
        "9. 😊 Emoji Queen\n"
        "10. ↩️ Reply Master\n"
        "11. ✏️ Editor Pro\n"
        "12. 🗑️ Cleaner\n"
        "13. 🎉 Year Summary\n\n"
        "Click the button below to see your results!"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка"""
    help_text = (
        "📊 **Year Review Bot Help**\n\n"
        "This bot shows your Telegram statistics for the year.\n\n"
        "**Commands:**\n"
        "/start - Open Year Review\n"
        "/help - Show this message\n\n"
        "**Features:**\n"
        "• 13 beautiful statistics slides\n"
        "• Animated emojis\n"
        "• Touch navigation (swipe)\n"
        "• Keyboard navigation (arrow keys)\n"
        "• Responsive design\n\n"
        "Click the button to open the interactive Year Review!"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Open Year Review",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    
    await message.answer(help_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message()
async def echo_handler(message: Message):
    """Обработка других сообщений"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 View Your Year Review",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    
    await message.answer(
        "Click the button below to view your Year Review!",
        reply_markup=keyboard
    )


async def run_bot():
    """Запуск Telegram Bot"""
    await set_default_commands()
    print("✅ Bot started and listening for messages...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n❌ Bot stopped")
    finally:
        await bot.session.close()


def start_bot_thread():
    """Запуск бота в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    try:
        # Запускаем Flask в основном потоке
        # и бота в отдельном потоке
        
        print(f"""
╔════════════════════════════════════════════════╗
║             🚀 STARTING ALL SYSTEMS            ║
╚════════════════════════════════════════════════╝

1️⃣  Flask Web Server (http://localhost:{PORT})
2️⃣  Telegram Bot (@{BOT_USERNAME})
3️⃣  Mini App Frontend (http://localhost:{PORT}/app)

To open Mini App:
- Write /start to the bot in Telegram
- Click button "View Your Year Review"
- Or visit http://localhost:{PORT}/app in browser

Press CTRL+C to stop all services
""")
        
        # Запускаем бота в отдельном потоке
        bot_thread = Thread(target=start_bot_thread, daemon=True)
        bot_thread.start()
        
        # Запускаем Flask в основном потоке
        app.run(
            host='0.0.0.0',
            port=PORT,
            debug=DEBUG,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n\n❌ All services stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
