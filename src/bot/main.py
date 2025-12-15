"""
FootyBot Main Module
Entry point for the Telegram bot.
"""

import asyncio
from telebot.async_telebot import AsyncTeleBot
from config.settings import TelegramBotConfig
from src.utils.logger import logger, log_startup_info
from src.bot.handlers.commands import register_command_handlers
from src.bot.handlers.callbacks import register_callback_handlers


# Initialize bot
bot = AsyncTeleBot(TelegramBotConfig.BOT_TOKEN, parse_mode='HTML')


async def start_bot():
    """
    Initialize and start the Telegram bot.
    """
    # Log startup information
    log_startup_info({
        'bot_name': 'FootyBot',
        'name': 'FootyBot',
        'version': '1.0.0',
        'environment': 'production'
    })
    
    try:
        # Register handlers
        logger.info("Registering bot handlers...")
        register_command_handlers(bot)
        register_callback_handlers(bot)
        logger.info("All handlers registered successfully")
        
        # Start polling
        logger.info("Starting bot polling...")
        await bot.polling(non_stop=True, interval=0, timeout=60)
        
    except Exception as e:
        logger.error(f"Fatal error in bot: {str(e)}")
        raise


def main():
    """
    Main entry point for the bot.
    """
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
