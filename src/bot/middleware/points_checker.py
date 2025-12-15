"""
Points Checker Middleware
Handles point verification and deduction for API requests.
"""

from typing import Dict, Any
from functools import wraps
from src.database.supabase_client import get_supabase_client
from src.utils.logger import logger


# تصنيف الميزات (Feature Classification)
# Features that don't require API calls or points
FREE_NO_API = [
    'menu_info', 
    'menu_points', 
    'menu_settings', 
    'referral_stats',
    'back_to_main',
    'menu_referral'
]

# Features that use cached/static data (free)
FREE_CACHED = [
    'menu_teams', 
    'menu_leagues', 
    'search_team', 
    'search_player',
    'team_static_',  # Prefix for static team info
    'league_info_'   # Prefix for static league info
]

# Features that require API calls and points
REQUIRES_POINTS = [
    'menu_live', 
    'menu_today', 
    'menu_tomorrow', 
    'standings',
    'team_stats_',   # Prefix for team statistics
    'match_details_',
    'head_to_head_'
]


class PointsChecker:
    """
    Middleware class for checking and deducting points before API requests.
    """
    
    @staticmethod
    async def check_and_deduct(user_id: int) -> Dict[str, Any]:
        """
        Check if user has points and deduct one if available.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with:
                - allowed (bool): Whether request is allowed
                - points_type (str): Type of points used ('free', 'premium', 'none')
                - show_warning (bool): Whether to show premium points warning
                - free_remaining (int): Remaining free requests
                - premium_remaining (int): Remaining premium points
                - message (str): Message to show user
        """
        try:
            db = get_supabase_client()
            result = db.deduct_point(user_id)
            
            # Build appropriate message
            if result['allowed']:
                if result['points_type'] == 'free':
                    message = f"✅ تم استخدام طلب مجاني ({result['free_remaining']} متبقي)"
                elif result['points_type'] == 'premium':
                    if result['show_warning']:
                        message = (
                            f"⚠️ انتهت طلباتك المجانية!\n"
                            f"تم استخدام نقطة من النقاط المدفوعة ({result['premium_remaining']} متبقي)\n"
                            f"💡 قم بدعوة أصدقائك لكسب المزيد من النقاط"
                        )
                    else:
                        message = f"✅ تم استخدام نقطة ({result['premium_remaining']} متبقي)"
                else:
                    message = "✅ تم معالجة الطلب"
            else:
                message = (
                    "❌ لا توجد نقاط كافية!\n\n"
                    "💡 يمكنك كسب نقاط إضافية عن طريق:\n"
                    "• دعوة أصدقائك (+3 نقاط لكل دعوة)\n"
                    "• انتظار تجديد الطلبات المجانية غداً"
                )
            
            result['message'] = message
            logger.info(f"Points check for user {user_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error checking points for user {user_id}: {str(e)}")
            return {
                'allowed': False,
                'points_type': 'none',
                'show_warning': False,
                'free_remaining': 0,
                'premium_remaining': 0,
                'message': "❌ حدث خطأ في التحقق من النقاط"
            }
    
    @staticmethod
    def needs_points(callback_data: str) -> bool:
        """
        Check if a callback requires points deduction.
        
        Args:
            callback_data: Callback data string
            
        Returns:
            True if points are required, False otherwise
        """
        # Check if it's a free feature
        if callback_data in FREE_NO_API:
            return False
        
        # Check free cached features
        for prefix in FREE_CACHED:
            if callback_data.startswith(prefix):
                return False
        
        # Check if it requires points
        for prefix in REQUIRES_POINTS:
            if callback_data.startswith(prefix):
                return True
        
        # Default to requiring points for unknown features
        return True


def requires_points(func):
    """
    Decorator to check points before executing a callback handler.
    
    Usage:
        @requires_points
        async def handle_live_matches(call):
            # Handler code
    
    Args:
        func: Async callback handler function
        
    Returns:
        Wrapped function with points checking
    """
    @wraps(func)
    async def wrapper(call_or_message):
        # Import here to avoid circular imports
        from telebot.types import CallbackQuery, Message
        
        # Determine if it's a callback query or message
        if isinstance(call_or_message, CallbackQuery):
            call = call_or_message
            user_id = call.from_user.id
            callback_data = call.data
            
            # Check if this callback needs points
            if not PointsChecker.needs_points(callback_data):
                # Execute without points check
                return await func(call)
            
            # Check and deduct points
            result = await PointsChecker.check_and_deduct(user_id)
            
            if not result['allowed']:
                # Not enough points, show error message
                await call.answer(result['message'], show_alert=True)
                logger.warning(f"Points check failed for user {user_id}")
                return
            
            # Show success message briefly (not as alert)
            if result['show_warning']:
                await call.answer(result['message'], show_alert=True)
            else:
                await call.answer(result['message'], show_alert=False)
            
            # Execute the handler
            return await func(call)
            
        elif isinstance(call_or_message, Message):
            # For message handlers, execute without points check
            # (points are typically only for callback queries with API calls)
            return await func(call_or_message)
        
        else:
            logger.error(f"Unknown type for points checker: {type(call_or_message)}")
            return await func(call_or_message)
    
    return wrapper
