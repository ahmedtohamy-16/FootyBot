"""
Supabase Client Module for FootyBot
Provides database access and operations using Supabase.
"""

from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from config.settings import SupabaseConfig
from src.utils.logger import logger, log_database_operation
from src.utils.decorators import retry
import time


class SupabaseClient:
    """
    Wrapper class for Supabase client with helper methods for database operations.
    Provides convenient methods for user management, points, and referrals.
    """
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern to ensure single Supabase client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase client."""
        if self._client is None:
            try:
                self._client = create_client(
                    supabase_url=SupabaseConfig.URL,
                    supabase_key=SupabaseConfig.KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        return self._client
    
    # ==================== USER OPERATIONS ====================
    
    @retry(max_attempts=3, delay=1.0)
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User dictionary or None if not found
        """
        start_time = time.time()
        try:
            response = self._client.table('users').select('*').eq('telegram_id', telegram_id).single().execute()
            duration = (time.time() - start_time) * 1000
            log_database_operation('SELECT', 'users', True, duration, affected_rows=1)
            return response.data if response.data else None
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('SELECT', 'users', False, duration, error=str(e))
            logger.error(f"Error fetching user {telegram_id}: {str(e)}")
            return None
    
    @retry(max_attempts=3, delay=1.0)
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary with user information
            
        Returns:
            Created user dictionary or None on failure
        """
        start_time = time.time()
        try:
            response = self._client.table('users').insert(user_data).execute()
            duration = (time.time() - start_time) * 1000
            log_database_operation('INSERT', 'users', True, duration, affected_rows=1)
            logger.info(f"User created: {user_data.get('telegram_id')}")
            return response.data[0] if response.data else None
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('INSERT', 'users', False, duration, error=str(e))
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    @retry(max_attempts=3, delay=1.0)
    def update_user(self, telegram_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update user information.
        
        Args:
            telegram_id: Telegram user ID
            updates: Dictionary with fields to update
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        try:
            response = self._client.table('users').update(updates).eq('telegram_id', telegram_id).execute()
            duration = (time.time() - start_time) * 1000
            log_database_operation('UPDATE', 'users', True, duration, affected_rows=len(response.data))
            return True
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('UPDATE', 'users', False, duration, error=str(e))
            logger.error(f"Error updating user {telegram_id}: {str(e)}")
            return False
    
    # ==================== POINTS OPERATIONS ====================
    
    @retry(max_attempts=3, delay=1.0)
    def deduct_point(self, telegram_id: int) -> Dict[str, Any]:
        """
        Deduct a point from user using database function.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Dictionary with deduction result
        """
        start_time = time.time()
        try:
            response = self._client.rpc('deduct_point', {'user_telegram_id': telegram_id}).execute()
            duration = (time.time() - start_time) * 1000
            
            if response.data and len(response.data) > 0:
                result = response.data[0]
                log_database_operation('RPC:deduct_point', 'users', True, duration)
                logger.info(f"Point deducted for user {telegram_id}: {result}")
                return {
                    'allowed': result.get('success', False),
                    'points_type': result.get('points_type', 'none'),
                    'free_remaining': result.get('remaining_free', 0),
                    'premium_remaining': result.get('remaining_premium', 0),
                    'show_warning': result.get('show_warning', False)
                }
            else:
                log_database_operation('RPC:deduct_point', 'users', False, duration, error='No data returned')
                return {
                    'allowed': False,
                    'points_type': 'none',
                    'free_remaining': 0,
                    'premium_remaining': 0,
                    'show_warning': False
                }
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('RPC:deduct_point', 'users', False, duration, error=str(e))
            logger.error(f"Error deducting point for user {telegram_id}: {str(e)}")
            return {
                'allowed': False,
                'points_type': 'none',
                'free_remaining': 0,
                'premium_remaining': 0,
                'show_warning': False
            }
    
    @retry(max_attempts=3, delay=1.0)
    def process_referral(self, new_user_id: int, referral_code: str) -> Dict[str, Any]:
        """
        Process a referral using database function.
        
        Args:
            new_user_id: New user's Telegram ID
            referral_code: Referral code from referrer
            
        Returns:
            Dictionary with referral processing result
        """
        start_time = time.time()
        try:
            response = self._client.rpc('process_referral', {
                'new_user_id': new_user_id,
                'referral_code_input': referral_code
            }).execute()
            duration = (time.time() - start_time) * 1000
            
            if response.data and len(response.data) > 0:
                result = response.data[0]
                log_database_operation('RPC:process_referral', 'referrals', True, duration)
                logger.info(f"Referral processed for user {new_user_id}: {result}")
                return {
                    'success': result.get('success', False),
                    'referrer_id': result.get('referrer_id'),
                    'new_user_points': result.get('new_user_points', 0),
                    'referrer_points': result.get('referrer_points', 0)
                }
            else:
                log_database_operation('RPC:process_referral', 'referrals', False, duration, error='No data returned')
                return {
                    'success': False,
                    'referrer_id': None,
                    'new_user_points': 0,
                    'referrer_points': 0
                }
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('RPC:process_referral', 'referrals', False, duration, error=str(e))
            logger.error(f"Error processing referral for user {new_user_id}: {str(e)}")
            return {
                'success': False,
                'referrer_id': None,
                'new_user_points': 0,
                'referrer_points': 0
            }
    
    @retry(max_attempts=3, delay=1.0)
    def get_user_referrals(self, telegram_id: int) -> List[Dict[str, Any]]:
        """
        Get all referrals made by a user.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            List of referral dictionaries
        """
        start_time = time.time()
        try:
            response = self._client.table('referrals').select('*').eq('referrer_id', telegram_id).execute()
            duration = (time.time() - start_time) * 1000
            log_database_operation('SELECT', 'referrals', True, duration, affected_rows=len(response.data))
            return response.data if response.data else []
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('SELECT', 'referrals', False, duration, error=str(e))
            logger.error(f"Error fetching referrals for user {telegram_id}: {str(e)}")
            return []
    
    # ==================== REQUEST LOGGING ====================
    
    @retry(max_attempts=3, delay=1.0)
    def log_request(self, log_data: Dict[str, Any]) -> bool:
        """
        Log an API request to the database.
        
        Args:
            log_data: Dictionary with request log information
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        try:
            self._client.table('requests_log').insert(log_data).execute()
            duration = (time.time() - start_time) * 1000
            log_database_operation('INSERT', 'requests_log', True, duration, affected_rows=1)
            return True
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('INSERT', 'requests_log', False, duration, error=str(e))
            logger.error(f"Error logging request: {str(e)}")
            return False
    
    # ==================== PREFERENCES ====================
    
    @retry(max_attempts=3, delay=1.0)
    def get_user_preferences(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user preferences.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Preferences dictionary or None if not found
        """
        start_time = time.time()
        try:
            response = self._client.table('user_preferences').select('*').eq('user_id', telegram_id).single().execute()
            duration = (time.time() - start_time) * 1000
            log_database_operation('SELECT', 'user_preferences', True, duration, affected_rows=1)
            return response.data if response.data else None
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('SELECT', 'user_preferences', False, duration, error=str(e))
            logger.error(f"Error fetching preferences for user {telegram_id}: {str(e)}")
            return None
    
    @retry(max_attempts=3, delay=1.0)
    def update_user_preferences(self, telegram_id: int, preferences: Dict[str, Any]) -> bool:
        """
        Update or create user preferences.
        
        Args:
            telegram_id: Telegram user ID
            preferences: Dictionary with preference updates
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        try:
            # Try to update first
            response = self._client.table('user_preferences').update(preferences).eq('user_id', telegram_id).execute()
            
            # If no rows affected, insert new preferences
            if not response.data:
                preferences['user_id'] = telegram_id
                response = self._client.table('user_preferences').insert(preferences).execute()
            
            duration = (time.time() - start_time) * 1000
            log_database_operation('UPSERT', 'user_preferences', True, duration, affected_rows=1)
            return True
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation('UPSERT', 'user_preferences', False, duration, error=str(e))
            logger.error(f"Error updating preferences for user {telegram_id}: {str(e)}")
            return False


# Singleton instance getter
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """
    Get or create the Supabase client singleton instance.
    
    Returns:
        SupabaseClient instance
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
