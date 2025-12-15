"""
Command Handlers Module
Handles bot commands like /start and /info.
"""

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from src.database.supabase_client import get_supabase_client
from src.bot.keyboards.inline import main_menu_keyboard
from src.bot.messages.translations import get_text
from src.utils.logger import logger, log_user_action
from datetime import datetime
import hashlib


def register_command_handlers(bot: AsyncTeleBot):
    """
    Register all command handlers with the bot.
    
    Args:
        bot: AsyncTeleBot instance
    """
    
    @bot.message_handler(commands=['start'])
    async def start_command(message: Message):
        """
        Handle /start command with optional referral code.
        
        Args:
            message: Telegram message object
        """
        user = message.from_user
        user_id = user.id
        username = user.username or f"user_{user_id}"
        first_name = user.first_name or "User"
        last_name = user.last_name or ""
        language_code = user.language_code or "en"
        
        # Extract referral code from command args
        command_args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        referral_code = command_args[0] if command_args else None
        
        log_user_action(user_id, username, "start_command", {"referral_code": referral_code})
        
        try:
            db = get_supabase_client()
            
            # Check if user exists
            existing_user = db.get_user_by_telegram_id(user_id)
            
            if existing_user:
                # Existing user - welcome back
                logger.info(f"Existing user {user_id} started bot")
                
                # Update last active
                db.update_user(user_id, {'last_active_at': datetime.utcnow().isoformat()})
                
                await bot.send_message(
                    message.chat.id,
                    get_text('welcome_back', language_code),
                    reply_markup=main_menu_keyboard(language_code),
                    parse_mode='HTML'
                )
            else:
                # New user - create account
                logger.info(f"New user {user_id} started bot")
                
                # Generate unique referral code for new user
                referral_code_new = generate_referral_code(user_id)
                
                user_data = {
                    'telegram_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'language_code': language_code,
                    'referral_code': referral_code_new,
                    'free_requests': 3,
                    'premium_points': 0,
                    'is_active': True,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_active_at': datetime.utcnow().isoformat()
                }
                
                created_user = db.create_user(user_data)
                
                if not created_user:
                    await bot.send_message(
                        message.chat.id,
                        get_text('error', language_code),
                        parse_mode='HTML'
                    )
                    return
                
                # Process referral if provided
                referral_success = False
                if referral_code:
                    result = db.process_referral(user_id, referral_code)
                    referral_success = result.get('success', False)
                    
                    if referral_success:
                        logger.info(f"Referral processed: {user_id} referred by code {referral_code}")
                
                # Send welcome message
                if referral_success:
                    welcome_message = get_text('welcome_with_referral', language_code)
                else:
                    welcome_message = get_text('welcome', language_code)
                
                await bot.send_message(
                    message.chat.id,
                    welcome_message,
                    reply_markup=main_menu_keyboard(language_code),
                    parse_mode='HTML'
                )
                
                # Create default user preferences
                db.update_user_preferences(user_id, {
                    'preferred_language': language_code,
                    'notifications_enabled': True
                })
                
        except Exception as e:
            logger.error(f"Error in start command for user {user_id}: {str(e)}")
            await bot.send_message(
                message.chat.id,
                get_text('error', language_code),
                parse_mode='HTML'
            )
    
    @bot.message_handler(commands=['info'])
    async def info_command(message: Message):
        """
        Handle /info command - show bot info and user statistics.
        
        Args:
            message: Telegram message object
        """
        user = message.from_user
        user_id = user.id
        username = user.username or f"user_{user_id}"
        language_code = user.language_code or "en"
        
        log_user_action(user_id, username, "info_command", {})
        
        try:
            db = get_supabase_client()
            
            # Get user data
            user_data = db.get_user_by_telegram_id(user_id)
            
            if not user_data:
                await bot.send_message(
                    message.chat.id,
                    get_text('error', language_code),
                    parse_mode='HTML'
                )
                return
            
            # Get referral count
            referrals = db.get_user_referrals(user_id)
            referral_count = len(referrals)
            
            # Format info message
            info_message = get_text(
                'bot_info', 
                language_code,
                free=user_data.get('free_requests', 0),
                premium=user_data.get('premium_points', 0),
                referrals=referral_count
            )
            
            await bot.send_message(
                message.chat.id,
                info_message,
                reply_markup=main_menu_keyboard(language_code),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in info command for user {user_id}: {str(e)}")
            await bot.send_message(
                message.chat.id,
                get_text('error', language_code),
                parse_mode='HTML'
            )
    
    @bot.message_handler(commands=['help'])
    async def help_command(message: Message):
        """
        Handle /help command - show available commands.
        
        Args:
            message: Telegram message object
        """
        user = message.from_user
        language_code = user.language_code or "en"
        
        help_message = get_text('help', language_code)
        
        await bot.send_message(
            message.chat.id,
            help_message,
            parse_mode='HTML'
        )
    
    logger.info("Command handlers registered")


def generate_referral_code(user_id: int) -> str:
    """
    Generate a unique referral code for a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        8-character referral code
    """
    # Create hash from user ID and timestamp
    timestamp = str(datetime.utcnow().timestamp())
    hash_input = f"{user_id}_{timestamp}"
    hash_obj = hashlib.md5(hash_input.encode())
    code = hash_obj.hexdigest()[:8].upper()
    return code
