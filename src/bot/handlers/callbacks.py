"""
Callback Handlers Module
Handles all callback queries from inline keyboards.
"""

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from src.database.supabase_client import get_supabase_client
from src.bot.keyboards.inline import (
    main_menu_keyboard,
    leagues_keyboard,
    teams_keyboard,
    team_list_keyboard,
    team_details_keyboard,
    standings_keyboard,
    back_button_keyboard
)
from src.bot.messages.translations import get_text
from src.bot.messages.formatter import MessageFormatter
from src.bot.services.static_data_service import StaticDataService
from src.bot.middleware.points_checker import requires_points
from src.api.football_api import FootballAPIClient
from src.utils.logger import logger, log_user_action
from datetime import datetime, timedelta
from config.settings import EnvironmentConfig


def register_callback_handlers(bot: AsyncTeleBot):
    """
    Register all callback query handlers with the bot.
    
    Args:
        bot: AsyncTeleBot instance
    """
    
    # Initialize Football API client
    football_api = FootballAPIClient(api_key=EnvironmentConfig.API_FOOTBALL_KEY)
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
    async def back_to_main(call: CallbackQuery):
        """Handle back to main menu."""
        language_code = call.from_user.language_code or "en"
        
        await bot.edit_message_text(
            get_text('main_menu', language_code),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu_keyboard(language_code),
            parse_mode='HTML'
        )
        await call.answer()
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_info")
    async def menu_info(call: CallbackQuery):
        """Handle info menu - show bot information."""
        user_id = call.from_user.id
        username = call.from_user.username or f"user_{user_id}"
        language_code = call.from_user.language_code or "en"
        
        log_user_action(user_id, username, "menu_info", {})
        
        try:
            db = get_supabase_client()
            user_data = db.get_user_by_telegram_id(user_id)
            
            if not user_data:
                await call.answer(get_text('error', language_code), show_alert=True)
                return
            
            referrals = db.get_user_referrals(user_id)
            
            info_message = get_text(
                'bot_info',
                language_code,
                free=user_data.get('free_requests', 0),
                premium=user_data.get('premium_points', 0),
                referrals=len(referrals)
            )
            
            await bot.edit_message_text(
                info_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("back_to_main", language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in menu_info: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_points")
    async def menu_points(call: CallbackQuery):
        """Handle points menu - show user points."""
        user_id = call.from_user.id
        username = call.from_user.username or f"user_{user_id}"
        language_code = call.from_user.language_code or "en"
        
        log_user_action(user_id, username, "menu_points", {})
        
        try:
            db = get_supabase_client()
            user_data = db.get_user_by_telegram_id(user_id)
            
            if not user_data:
                await call.answer(get_text('error', language_code), show_alert=True)
                return
            
            points_message = get_text(
                'points_info',
                language_code,
                free=user_data.get('free_requests', 0),
                premium=user_data.get('premium_points', 0)
            )
            
            await bot.edit_message_text(
                points_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("back_to_main", language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in menu_points: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_referral")
    async def menu_referral(call: CallbackQuery):
        """Handle referral menu - show referral info."""
        user_id = call.from_user.id
        username = call.from_user.username or f"user_{user_id}"
        language_code = call.from_user.language_code or "en"
        
        log_user_action(user_id, username, "menu_referral", {})
        
        try:
            db = get_supabase_client()
            user_data = db.get_user_by_telegram_id(user_id)
            
            if not user_data:
                await call.answer(get_text('error', language_code), show_alert=True)
                return
            
            referral_code = user_data.get('referral_code', 'N/A')
            referrals = db.get_user_referrals(user_id)
            referral_count = len(referrals)
            referral_points = referral_count * 3
            
            # Create bot link with referral code
            bot_username = (await bot.get_me()).username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            referral_message = get_text(
                'referral_info',
                language_code,
                code=referral_code,
                count=referral_count,
                points=referral_points
            )
            
            referral_message += f"\n\n{get_text('referral_link', language_code, link=referral_link, code=referral_code)}"
            
            await bot.edit_message_text(
                referral_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("back_to_main", language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in menu_referral: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_settings")
    async def menu_settings(call: CallbackQuery):
        """Handle settings menu."""
        language_code = call.from_user.language_code or "en"
        
        settings_message = get_text('settings', language_code)
        
        await bot.edit_message_text(
            settings_message,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button_keyboard("back_to_main", language_code),
            parse_mode='HTML'
        )
        await call.answer()
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_teams")
    async def menu_teams(call: CallbackQuery):
        """Handle teams menu - show league selection."""
        language_code = call.from_user.language_code or "en"
        
        await bot.edit_message_text(
            get_text('teams_list', language_code),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=teams_keyboard(0, language_code),
            parse_mode='HTML'
        )
        await call.answer()
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("teams_league_"))
    async def teams_by_league(call: CallbackQuery):
        """Handle showing teams for a selected league."""
        language_code = call.from_user.language_code or "en"
        
        try:
            league_id = int(call.data.split("_")[-1])
            teams = StaticDataService.get_teams_by_league(league_id)
            
            if not teams:
                await call.answer(get_text('team_not_found', language_code), show_alert=True)
                return
            
            await bot.edit_message_text(
                get_text('select_team', language_code),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=team_list_keyboard(teams, language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in teams_by_league: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("team_static_"))
    async def team_static_info(call: CallbackQuery):
        """Handle showing static team information (no API call needed)."""
        language_code = call.from_user.language_code or "en"
        
        try:
            team_id = int(call.data.split("_")[-1])
            team = StaticDataService.get_team_by_id(team_id)
            
            if not team:
                await call.answer(get_text('team_not_found', language_code), show_alert=True)
                return
            
            team_message = MessageFormatter.format_team_info(team, language_code)
            
            await bot.edit_message_text(
                team_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=team_details_keyboard(team_id, language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in team_static_info: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_leagues")
    async def menu_leagues(call: CallbackQuery):
        """Handle leagues menu - show available leagues."""
        language_code = call.from_user.language_code or "en"
        
        try:
            leagues = StaticDataService.get_all_leagues()
            
            await bot.edit_message_text(
                get_text('leagues_list', language_code),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=leagues_keyboard(leagues, language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in menu_leagues: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("league_info_"))
    async def league_info(call: CallbackQuery):
        """Handle showing league information (static data)."""
        language_code = call.from_user.language_code or "en"
        
        try:
            league_id = int(call.data.split("_")[-1])
            league = StaticDataService.get_league_info(league_id)
            
            if not league:
                await call.answer(get_text('league_not_found', language_code), show_alert=True)
                return
            
            league_message = MessageFormatter.format_league_info(league, language_code)
            
            await bot.edit_message_text(
                league_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("menu_leagues", language_code),
                parse_mode='HTML'
            )
            await call.answer()
            
        except Exception as e:
            logger.error(f"Error in league_info: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_standings")
    async def menu_standings(call: CallbackQuery):
        """Handle standings menu - show league selection."""
        language_code = call.from_user.language_code or "en"
        
        await bot.edit_message_text(
            get_text('leagues_list', language_code),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=standings_keyboard(language_code),
            parse_mode='HTML'
        )
        await call.answer()
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("standings_"))
    @requires_points
    async def show_standings(call: CallbackQuery):
        """Handle showing league standings (requires points)."""
        language_code = call.from_user.language_code or "en"
        
        try:
            league_id = int(call.data.split("_")[-1])
            league = StaticDataService.get_league_info(league_id)
            
            if not league:
                await call.answer(get_text('league_not_found', language_code), show_alert=True)
                return
            
            # Get standings from API
            standings = football_api.get_standings(league_id, 2024)
            
            if not standings or len(standings) == 0:
                await call.answer(get_text('error', language_code), show_alert=True)
                return
            
            league_name = league.get('name_ar' if language_code == 'ar' else 'name')
            standings_message = MessageFormatter.format_standings(standings[0], league_name, language_code)
            
            await bot.edit_message_text(
                standings_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("menu_standings", language_code),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in show_standings: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_live")
    @requires_points
    async def menu_live(call: CallbackQuery):
        """Handle live matches menu (requires points)."""
        language_code = call.from_user.language_code or "en"
        
        try:
            # Get live matches from API
            matches = football_api.get_live_fixtures()
            
            if not matches:
                await bot.edit_message_text(
                    get_text('no_live_matches', language_code),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=back_button_keyboard("back_to_main", language_code),
                    parse_mode='HTML'
                )
                return
            
            title = "⚽ " + (get_text('btn_live', language_code))
            matches_message = MessageFormatter.format_matches_list(matches, title, language_code)
            
            await bot.edit_message_text(
                matches_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("back_to_main", language_code),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in menu_live: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_today")
    @requires_points
    async def menu_today(call: CallbackQuery):
        """Handle today's matches menu (requires points)."""
        language_code = call.from_user.language_code or "en"
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            matches = football_api.get_fixtures_by_date(today)
            
            if not matches:
                await bot.edit_message_text(
                    get_text('no_matches_today', language_code),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=back_button_keyboard("back_to_main", language_code),
                    parse_mode='HTML'
                )
                return
            
            title = "📅 " + (get_text('btn_today', language_code))
            matches_message = MessageFormatter.format_matches_list(matches, title, language_code)
            
            await bot.edit_message_text(
                matches_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("back_to_main", language_code),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in menu_today: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == "menu_tomorrow")
    @requires_points
    async def menu_tomorrow(call: CallbackQuery):
        """Handle tomorrow's matches menu (requires points)."""
        language_code = call.from_user.language_code or "en"
        
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            matches = football_api.get_fixtures_by_date(tomorrow)
            
            if not matches:
                await bot.edit_message_text(
                    get_text('no_matches_tomorrow', language_code),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=back_button_keyboard("back_to_main", language_code),
                    parse_mode='HTML'
                )
                return
            
            title = "📆 " + (get_text('btn_tomorrow', language_code))
            matches_message = MessageFormatter.format_matches_list(matches, title, language_code)
            
            await bot.edit_message_text(
                matches_message,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button_keyboard("back_to_main", language_code),
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in menu_tomorrow: {str(e)}")
            await call.answer(get_text('error', language_code), show_alert=True)
    
    logger.info("Callback handlers registered")
