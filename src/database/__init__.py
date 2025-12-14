"""
Database layer for FootyBot
"""

from .supabase_client import (
    SupabaseClient,
    SupabaseClientError,
    get_supabase_client,
)

__version__ = "1.0.0"

__all__ = [
    'SupabaseClient',
    'SupabaseClientError',
    'get_supabase_client',
]
