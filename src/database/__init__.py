"""
Database Module

This module provides the Supabase client wrapper for database operations.
Includes CRUD operations, error handling, and comprehensive logging.
"""

from .supabase_client import (
    SupabaseClient,
    SupabaseClientError,
    get_supabase_client,
)

__all__ = [
    'SupabaseClient',
    'SupabaseClientError',
    'get_supabase_client',
]

__version__ = "1.0.0"
