"""
Database package for FootyBot.
Provides Supabase client and database utilities.
"""

from src.database.supabase_client import get_supabase_client, SupabaseClient

__all__ = ['get_supabase_client', 'SupabaseClient']
