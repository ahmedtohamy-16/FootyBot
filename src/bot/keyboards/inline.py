"""
Inline Keyboards Module
Provides inline keyboard layouts for the bot.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional
from src.bot.messages.translations import get_text


def main_menu_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create the main menu keyboard with 10 buttons.
    
    Args:
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with main menu buttons
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Row 1: Live matches and Today's matches
    keyboard.add(
        InlineKeyboardButton(get_text('btn_live', lang), callback_data="menu_live"),
        InlineKeyboardButton(get_text('btn_today', lang), callback_data="menu_today")
    )
    
    # Row 2: Tomorrow's matches and Standings
    keyboard.add(
        InlineKeyboardButton(get_text('btn_tomorrow', lang), callback_data="menu_tomorrow"),
        InlineKeyboardButton(get_text('btn_standings', lang), callback_data="menu_standings")
    )
    
    # Row 3: Teams and Leagues
    keyboard.add(
        InlineKeyboardButton(get_text('btn_teams', lang), callback_data="menu_teams"),
        InlineKeyboardButton(get_text('btn_leagues', lang), callback_data="menu_leagues")
    )
    
    # Row 4: Points and Referrals
    keyboard.add(
        InlineKeyboardButton(get_text('btn_points', lang), callback_data="menu_points"),
        InlineKeyboardButton(get_text('btn_referral', lang), callback_data="menu_referral")
    )
    
    # Row 5: Settings and Info
    keyboard.add(
        InlineKeyboardButton(get_text('btn_settings', lang), callback_data="menu_settings"),
        InlineKeyboardButton(get_text('btn_info', lang), callback_data="menu_info")
    )
    
    return keyboard


def leagues_keyboard(leagues: List[Dict[str, Any]], lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create keyboard with league buttons.
    
    Args:
        leagues: List of league dictionaries
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with league buttons
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for league in leagues:
        league_id = league.get('id')
        league_name = league.get('name_ar' if lang == 'ar' else 'name', league.get('name'))
        
        keyboard.add(
            InlineKeyboardButton(
                f"🏆 {league_name}",
                callback_data=f"league_info_{league_id}"
            )
        )
    
    # Back button
    keyboard.add(
        InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_to_main")
    )
    
    return keyboard


def teams_keyboard(league_id: int, lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create keyboard to select a league for viewing teams.
    
    Args:
        league_id: Optional pre-selected league ID
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with league selection buttons
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Supported leagues
    leagues = [
        (39, "الدوري الإنجليزي", "Premier League"),
        (140, "الدوري الإسباني", "La Liga"),
        (78, "الدوري الألماني", "Bundesliga"),
        (135, "الدوري الإيطالي", "Serie A"),
        (61, "الدوري الفرنسي", "Ligue 1"),
        (307, "دوري روشن", "Saudi League")
    ]
    
    for lid, name_ar, name_en in leagues:
        name = name_ar if lang == 'ar' else name_en
        keyboard.add(
            InlineKeyboardButton(
                f"👕 {name}",
                callback_data=f"teams_league_{lid}"
            )
        )
    
    # Back button
    keyboard.add(
        InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_to_main")
    )
    
    return keyboard


def team_list_keyboard(teams: List[Dict[str, Any]], lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create keyboard with team buttons.
    
    Args:
        teams: List of team dictionaries
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with team buttons
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for team in teams:
        team_id = team.get('id')
        team_name = team.get('name_ar' if lang == 'ar' else 'name', team.get('name'))
        
        keyboard.add(
            InlineKeyboardButton(
                f"👕 {team_name}",
                callback_data=f"team_static_{team_id}"
            )
        )
    
    # Back button
    keyboard.add(
        InlineKeyboardButton(get_text('btn_back', lang), callback_data="menu_teams")
    )
    
    return keyboard


def team_details_keyboard(team_id: int, lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create keyboard for team details with options.
    
    Args:
        team_id: Team ID
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with team action buttons
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if lang == 'ar':
        keyboard.add(
            InlineKeyboardButton("📊 الإحصائيات", callback_data=f"team_stats_{team_id}"),
            InlineKeyboardButton("📅 المباريات", callback_data=f"team_matches_{team_id}")
        )
    else:
        keyboard.add(
            InlineKeyboardButton("📊 Statistics", callback_data=f"team_stats_{team_id}"),
            InlineKeyboardButton("📅 Matches", callback_data=f"team_matches_{team_id}")
        )
    
    # Back button
    keyboard.add(
        InlineKeyboardButton(get_text('btn_back', lang), callback_data="menu_teams")
    )
    
    return keyboard


def standings_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create keyboard for selecting league standings.
    
    Args:
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with league buttons for standings
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Supported leagues
    leagues = [
        (39, "الدوري الإنجليزي", "Premier League"),
        (140, "الدوري الإسباني", "La Liga"),
        (78, "الدوري الألماني", "Bundesliga"),
        (135, "الدوري الإيطالي", "Serie A"),
        (61, "الدوري الفرنسي", "Ligue 1"),
        (307, "دوري روشن", "Saudi League")
    ]
    
    for lid, name_ar, name_en in leagues:
        name = name_ar if lang == 'ar' else name_en
        keyboard.add(
            InlineKeyboardButton(
                f"📊 {name}",
                callback_data=f"standings_{lid}"
            )
        )
    
    # Back button
    keyboard.add(
        InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_to_main")
    )
    
    return keyboard


def back_button_keyboard(callback_data: str = "back_to_main", lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create a simple keyboard with only a back button.
    
    Args:
        callback_data: Callback data for the back button
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with back button
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(get_text('btn_back', lang), callback_data=callback_data)
    )
    return keyboard


def pagination_keyboard(current_page: int, total_pages: int, prefix: str, lang: str = 'ar') -> InlineKeyboardMarkup:
    """
    Create pagination keyboard for navigating through pages.
    
    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        prefix: Callback data prefix (e.g., "matches_page")
        lang: Language code
        
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    buttons = []
    
    # Previous button
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton("⬅️", callback_data=f"{prefix}_{current_page - 1}")
        )
    
    # Page indicator
    buttons.append(
        InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
    )
    
    # Next button
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton("➡️", callback_data=f"{prefix}_{current_page + 1}")
        )
    
    keyboard.add(*buttons)
    
    # Back to main menu
    keyboard.add(
        InlineKeyboardButton(get_text('btn_main_menu', lang), callback_data="back_to_main")
    )
    
    return keyboard
