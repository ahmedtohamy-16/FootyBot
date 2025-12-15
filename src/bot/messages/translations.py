"""
Translations Module
Provides multilingual support for bot messages.
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'ar': {
        # Welcome messages
        'welcome': '🎉 مرحباً بك في FootyBot! ⚽\n\nبوتك المفضل لمتابعة أخبار ونتائج كرة القدم',
        'welcome_back': '👋 أهلاً بعودتك! ⚽',
        'welcome_with_referral': '🎉 مرحباً بك في FootyBot!\n\n✨ تم منحك نقطة بونص من صديقك!',
        
        # Main menu
        'main_menu': '📋 القائمة الرئيسية\n\nاختر ما تريد:',
        'select_option': 'اختر أحد الخيارات التالية:',
        
        # Points messages
        'points_info': '💰 معلومات النقاط:\n\n📊 طلبات مجانية: {free}\n⭐ نقاط مدفوعة: {premium}\n\n💡 تجدد الطلبات المجانية يومياً!',
        'no_points': '❌ لا توجد نقاط كافية!\n\n💡 يمكنك كسب نقاط إضافية عن طريق:\n• دعوة أصدقائك (+3 نقاط لكل دعوة)\n• انتظار تجديد الطلبات المجانية غداً',
        'points_deducted': '✅ تم خصم نقطة واحدة',
        'free_request_used': '✅ تم استخدام طلب مجاني ({remaining} متبقي)',
        'premium_point_used': '✅ تم استخدام نقطة ({remaining} متبقي)',
        'premium_warning': '⚠️ انتهت طلباتك المجانية!\n\nتم استخدام نقطة من النقاط المدفوعة ({remaining} متبقي)\n\n💡 قم بدعوة أصدقائك لكسب المزيد من النقاط',
        
        # Referral messages
        'referral_info': '🎁 نظام الإحالة\n\n📎 رمز الإحالة الخاص بك:\n<code>{code}</code>\n\n👥 عدد الإحالات: {count}\n⭐ نقاط مكتسبة: {points}\n\n💡 شارك رمزك مع أصدقائك واحصل على 3 نقاط لكل إحالة!',
        'referral_link': '🔗 رابط الإحالة:\n{link}\n\n📋 أو شارك الرمز:\n<code>{code}</code>',
        'referral_success': '🎉 تم تسجيل الإحالة بنجاح!\n\n✨ حصلت أنت على 1 نقطة\n✨ حصل صديقك على 3 نقاط',
        'referral_invalid': '❌ رمز الإحالة غير صالح',
        
        # Match messages
        'no_live_matches': '😴 لا توجد مباريات مباشرة الآن',
        'no_matches_today': '📅 لا توجد مباريات اليوم',
        'no_matches_tomorrow': '📅 لا توجد مباريات غداً',
        'loading': '⏳ جاري التحميل...',
        'error': '❌ حدث خطأ، يرجى المحاولة مرة أخرى',
        
        # Team messages
        'team_not_found': '❌ الفريق غير موجود',
        'teams_list': '📋 قائمة الفرق\n\nاختر الدوري:',
        'select_team': 'اختر فريق:',
        
        # League messages
        'leagues_list': '🏆 قائمة الدوريات\n\nاختر الدوري:',
        'league_not_found': '❌ الدوري غير موجود',
        
        # Settings
        'settings': '⚙️ الإعدادات',
        'language_changed': '✅ تم تغيير اللغة',
        'preferences_updated': '✅ تم تحديث التفضيلات',
        
        # Info
        'bot_info': '📊 معلومات البوت\n\n🤖 الإصدار: 1.0.0\n⚽ FootyBot - بوت متابعة كرة القدم\n\n📈 إحصائياتك:\n• طلبات مجانية: {free}\n• نقاط مدفوعة: {premium}\n• إحالات: {referrals}',
        
        # Buttons
        'btn_live': '⚽ مباريات مباشرة',
        'btn_today': '📅 مباريات اليوم',
        'btn_tomorrow': '📆 مباريات غداً',
        'btn_teams': '👕 الفرق',
        'btn_leagues': '🏆 الدوريات',
        'btn_standings': '📊 الترتيب',
        'btn_points': '💰 نقاطي',
        'btn_referral': '🎁 الدعوات',
        'btn_settings': '⚙️ الإعدادات',
        'btn_info': 'ℹ️ معلومات',
        'btn_back': '🔙 رجوع',
        'btn_main_menu': '🏠 القائمة الرئيسية',
        
        # Commands help
        'help': '/start - بدء البوت\n/info - معلومات البوت والإحصائيات',
    },
    'en': {
        # Welcome messages
        'welcome': '🎉 Welcome to FootyBot! ⚽\n\nYour favorite bot for football news and results',
        'welcome_back': '👋 Welcome back! ⚽',
        'welcome_with_referral': '🎉 Welcome to FootyBot!\n\n✨ You received a bonus point from your friend!',
        
        # Main menu
        'main_menu': '📋 Main Menu\n\nChoose what you want:',
        'select_option': 'Select one of the following options:',
        
        # Points messages
        'points_info': '💰 Points Info:\n\n📊 Free Requests: {free}\n⭐ Premium Points: {premium}\n\n💡 Free requests renew daily!',
        'no_points': '❌ Not enough points!\n\n💡 You can earn more points by:\n• Inviting friends (+3 points per invite)\n• Waiting for free requests to renew tomorrow',
        'points_deducted': '✅ One point deducted',
        'free_request_used': '✅ Free request used ({remaining} remaining)',
        'premium_point_used': '✅ Point used ({remaining} remaining)',
        'premium_warning': '⚠️ Free requests exhausted!\n\nUsed a premium point ({remaining} remaining)\n\n💡 Invite friends to earn more points',
        
        # Referral messages
        'referral_info': '🎁 Referral System\n\n📎 Your referral code:\n<code>{code}</code>\n\n👥 Referrals: {count}\n⭐ Points earned: {points}\n\n💡 Share your code and get 3 points per referral!',
        'referral_link': '🔗 Referral link:\n{link}\n\n📋 Or share code:\n<code>{code}</code>',
        'referral_success': '🎉 Referral registered successfully!\n\n✨ You got 1 point\n✨ Your friend got 3 points',
        'referral_invalid': '❌ Invalid referral code',
        
        # Match messages
        'no_live_matches': '😴 No live matches right now',
        'no_matches_today': '📅 No matches today',
        'no_matches_tomorrow': '📅 No matches tomorrow',
        'loading': '⏳ Loading...',
        'error': '❌ An error occurred, please try again',
        
        # Team messages
        'team_not_found': '❌ Team not found',
        'teams_list': '📋 Teams List\n\nSelect league:',
        'select_team': 'Select team:',
        
        # League messages
        'leagues_list': '🏆 Leagues List\n\nSelect league:',
        'league_not_found': '❌ League not found',
        
        # Settings
        'settings': '⚙️ Settings',
        'language_changed': '✅ Language changed',
        'preferences_updated': '✅ Preferences updated',
        
        # Info
        'bot_info': '📊 Bot Info\n\n🤖 Version: 1.0.0\n⚽ FootyBot - Football Tracking Bot\n\n📈 Your Stats:\n• Free requests: {free}\n• Premium points: {premium}\n• Referrals: {referrals}',
        
        # Buttons
        'btn_live': '⚽ Live Matches',
        'btn_today': '📅 Today\'s Matches',
        'btn_tomorrow': '📆 Tomorrow\'s Matches',
        'btn_teams': '👕 Teams',
        'btn_leagues': '🏆 Leagues',
        'btn_standings': '📊 Standings',
        'btn_points': '💰 My Points',
        'btn_referral': '🎁 Referrals',
        'btn_settings': '⚙️ Settings',
        'btn_info': 'ℹ️ Info',
        'btn_back': '🔙 Back',
        'btn_main_menu': '🏠 Main Menu',
        
        # Commands help
        'help': '/start - Start the bot\n/info - Bot info and statistics',
    }
}


def get_text(key: str, lang: str = 'ar', **kwargs) -> str:
    """
    Get translated text for a given key.
    
    Args:
        key: Translation key
        lang: Language code (default: 'ar')
        **kwargs: Format arguments for the text
        
    Returns:
        Translated and formatted text
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS['ar']).get(key, key)
    
    # Format with provided arguments
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            # If a key is missing, return unformatted text
            pass
    
    return text
