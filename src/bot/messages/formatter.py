"""
Message Formatter Module
Formats data into readable messages for Telegram.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import pytz


class MessageFormatter:
    """
    Formatter class for converting data structures into formatted Telegram messages.
    """
    
    @staticmethod
    def format_live_match(match: Dict[str, Any], lang: str = 'ar') -> str:
        """
        Format a live match into a readable message.
        
        Args:
            match: Match dictionary from API
            lang: Language code
            
        Returns:
            Formatted match string
        """
        try:
            home_team = match.get('teams', {}).get('home', {}).get('name', 'Unknown')
            away_team = match.get('teams', {}).get('away', {}).get('name', 'Unknown')
            home_score = match.get('goals', {}).get('home', 0)
            away_score = match.get('goals', {}).get('away', 0)
            status = match.get('fixture', {}).get('status', {})
            elapsed = status.get('elapsed', 0)
            
            league_name = match.get('league', {}).get('name', 'Unknown League')
            
            if lang == 'ar':
                message = (
                    f"⚽ <b>{home_team}</b> {home_score} - {away_score} <b>{away_team}</b>\n"
                    f"⏱ الدقيقة: {elapsed}'\n"
                    f"🏆 {league_name}"
                )
            else:
                message = (
                    f"⚽ <b>{home_team}</b> {home_score} - {away_score} <b>{away_team}</b>\n"
                    f"⏱ Minute: {elapsed}'\n"
                    f"🏆 {league_name}"
                )
            
            return message
            
        except Exception as e:
            return f"❌ Error formatting match: {str(e)}"
    
    @staticmethod
    def format_upcoming_match(match: Dict[str, Any], lang: str = 'ar') -> str:
        """
        Format an upcoming match into a readable message.
        
        Args:
            match: Match dictionary from API
            lang: Language code
            
        Returns:
            Formatted match string
        """
        try:
            home_team = match.get('teams', {}).get('home', {}).get('name', 'Unknown')
            away_team = match.get('teams', {}).get('away', {}).get('name', 'Unknown')
            
            # Parse match date
            match_date_str = match.get('fixture', {}).get('date', '')
            match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            
            # Convert to local time (assuming Riyadh timezone)
            riyadh_tz = pytz.timezone('Asia/Riyadh')
            match_date_local = match_date.astimezone(riyadh_tz)
            time_str = match_date_local.strftime('%H:%M')
            
            league_name = match.get('league', {}).get('name', 'Unknown League')
            venue = match.get('fixture', {}).get('venue', {}).get('name', 'TBD')
            
            if lang == 'ar':
                message = (
                    f"📅 <b>{home_team}</b> vs <b>{away_team}</b>\n"
                    f"⏰ الوقت: {time_str}\n"
                    f"🏆 {league_name}\n"
                    f"🏟 {venue}"
                )
            else:
                message = (
                    f"📅 <b>{home_team}</b> vs <b>{away_team}</b>\n"
                    f"⏰ Time: {time_str}\n"
                    f"🏆 {league_name}\n"
                    f"🏟 {venue}"
                )
            
            return message
            
        except Exception as e:
            return f"❌ Error formatting match: {str(e)}"
    
    @staticmethod
    def format_team_info(team: Dict[str, Any], lang: str = 'ar') -> str:
        """
        Format team information into a readable message.
        
        Args:
            team: Team dictionary
            lang: Language code
            
        Returns:
            Formatted team info string
        """
        try:
            name = team.get('name_ar' if lang == 'ar' else 'name', team.get('name', 'Unknown'))
            code = team.get('code', 'N/A')
            founded = team.get('founded', 'N/A')
            
            venue = team.get('venue', {})
            venue_name = venue.get('name_ar' if lang == 'ar' else 'name', venue.get('name', 'Unknown'))
            capacity = venue.get('capacity', 'N/A')
            city = venue.get('city_ar' if lang == 'ar' else 'city', venue.get('city', 'Unknown'))
            
            if lang == 'ar':
                message = (
                    f"👕 <b>{name}</b>\n\n"
                    f"🔖 الرمز: {code}\n"
                    f"📅 التأسيس: {founded}\n\n"
                    f"🏟 <b>الملعب:</b>\n"
                    f"• الاسم: {venue_name}\n"
                    f"• السعة: {capacity:,} متفرج\n"
                    f"• المدينة: {city}"
                )
            else:
                message = (
                    f"👕 <b>{name}</b>\n\n"
                    f"🔖 Code: {code}\n"
                    f"📅 Founded: {founded}\n\n"
                    f"🏟 <b>Stadium:</b>\n"
                    f"• Name: {venue_name}\n"
                    f"• Capacity: {capacity:,}\n"
                    f"• City: {city}"
                )
            
            return message
            
        except Exception as e:
            return f"❌ Error formatting team info: {str(e)}"
    
    @staticmethod
    def format_player_info(player: Dict[str, Any], lang: str = 'ar') -> str:
        """
        Format player information into a readable message.
        
        Args:
            player: Player dictionary
            lang: Language code
            
        Returns:
            Formatted player info string
        """
        try:
            name = player.get('name_ar' if lang == 'ar' else 'name', player.get('name', 'Unknown'))
            nationality = player.get('nationality_ar' if lang == 'ar' else 'nationality', 'Unknown')
            team = player.get('current_team_ar' if lang == 'ar' else 'current_team', 'Unknown')
            position = player.get('position_ar' if lang == 'ar' else 'position', 'Unknown')
            age = player.get('age', 'N/A')
            
            if lang == 'ar':
                message = (
                    f"⭐ <b>{name}</b>\n\n"
                    f"🎂 العمر: {age}\n"
                    f"🏳️ الجنسية: {nationality}\n"
                    f"👕 النادي: {team}\n"
                    f"⚽ المركز: {position}"
                )
            else:
                message = (
                    f"⭐ <b>{name}</b>\n\n"
                    f"🎂 Age: {age}\n"
                    f"🏳️ Nationality: {nationality}\n"
                    f"👕 Club: {team}\n"
                    f"⚽ Position: {position}"
                )
            
            return message
            
        except Exception as e:
            return f"❌ Error formatting player info: {str(e)}"
    
    @staticmethod
    def format_league_info(league: Dict[str, Any], lang: str = 'ar') -> str:
        """
        Format league information into a readable message.
        
        Args:
            league: League dictionary
            lang: Language code
            
        Returns:
            Formatted league info string
        """
        try:
            name = league.get('name_ar' if lang == 'ar' else 'name', league.get('name', 'Unknown'))
            country = league.get('country_ar' if lang == 'ar' else 'country', 'Unknown')
            season = league.get('season', 'N/A')
            
            if lang == 'ar':
                message = (
                    f"🏆 <b>{name}</b>\n\n"
                    f"🌍 الدولة: {country}\n"
                    f"📅 الموسم: {season}"
                )
            else:
                message = (
                    f"🏆 <b>{name}</b>\n\n"
                    f"🌍 Country: {country}\n"
                    f"📅 Season: {season}"
                )
            
            return message
            
        except Exception as e:
            return f"❌ Error formatting league info: {str(e)}"
    
    @staticmethod
    def format_standings(standings: List[Dict[str, Any]], league_name: str, lang: str = 'ar') -> str:
        """
        Format league standings into a readable message.
        
        Args:
            standings: List of team standings
            league_name: Name of the league
            lang: Language code
            
        Returns:
            Formatted standings string
        """
        try:
            if lang == 'ar':
                message = f"📊 <b>ترتيب {league_name}</b>\n\n"
            else:
                message = f"📊 <b>{league_name} Standings</b>\n\n"
            
            for team in standings[:10]:  # Show top 10
                rank = team.get('rank', 0)
                team_name = team.get('team', {}).get('name', 'Unknown')
                points = team.get('points', 0)
                played = team.get('all', {}).get('played', 0)
                won = team.get('all', {}).get('win', 0)
                draw = team.get('all', {}).get('draw', 0)
                lost = team.get('all', {}).get('lose', 0)
                
                message += f"{rank}. <b>{team_name}</b>\n"
                if lang == 'ar':
                    message += f"   النقاط: {points} | لعب: {played} | فاز: {won} | تعادل: {draw} | خسر: {lost}\n\n"
                else:
                    message += f"   Pts: {points} | P: {played} | W: {won} | D: {draw} | L: {lost}\n\n"
            
            return message
            
        except Exception as e:
            return f"❌ Error formatting standings: {str(e)}"
    
    @staticmethod
    def format_matches_list(matches: List[Dict[str, Any]], title: str, lang: str = 'ar') -> str:
        """
        Format a list of matches into a readable message.
        
        Args:
            matches: List of match dictionaries
            title: Title for the list
            lang: Language code
            
        Returns:
            Formatted matches list string
        """
        if not matches:
            if lang == 'ar':
                return f"{title}\n\n😴 لا توجد مباريات"
            else:
                return f"{title}\n\n😴 No matches"
        
        message = f"{title}\n\n"
        
        for match in matches[:10]:  # Limit to 10 matches
            if match.get('fixture', {}).get('status', {}).get('short') in ['LIVE', '1H', '2H', 'HT']:
                message += MessageFormatter.format_live_match(match, lang) + "\n\n"
            else:
                message += MessageFormatter.format_upcoming_match(match, lang) + "\n\n"
        
        return message
