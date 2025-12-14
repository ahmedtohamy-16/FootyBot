"""
Supabase Client Wrapper

This module provides a comprehensive client wrapper for interacting with Supabase.
It includes CRUD operations, error handling, and database logging.

Author: FootyBot Team
Date: 2025-12-14
"""

import time
from typing import Dict, List, Optional, Any, Union
from supabase import create_client, Client

from config.settings import SupabaseConfig
from src.utils.logger import logger, log_database_operation, log_error
from src.utils.decorators import retry, timing


class SupabaseClientError(Exception):
    """Base exception for Supabase client errors."""
    pass


class SupabaseClient:
    """
    Wrapper for Supabase client with CRUD operations, error handling, and logging.
    
    Features:
    - CRUD operations (select, insert, update, delete, upsert)
    - Comprehensive error handling
    - Database operation logging
    - Automatic retry logic
    - Connection management
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase URL (uses SupabaseConfig.URL if not provided)
            key: Supabase API key (uses SupabaseConfig.KEY if not provided)
            timeout: Request timeout in seconds (uses SupabaseConfig.TIMEOUT if not provided)
        """
        self.url = url or SupabaseConfig.URL
        self.key = key or SupabaseConfig.KEY
        self.timeout = timeout or SupabaseConfig.TIMEOUT
        
        if not self.url or not self.key:
            raise SupabaseClientError(
                "Supabase URL and KEY must be provided. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("SupabaseClient initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize Supabase client: {str(e)}"
            log_error(e, {'url': self.url})
            raise SupabaseClientError(error_msg)
    
    @retry(max_attempts=SupabaseConfig.MAX_RETRIES, delay=SupabaseConfig.RETRY_DELAY, backoff=2.0)
    @timing()
    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Select data from a table.
        
        Args:
            table: Table name
            columns: Columns to select (default: "*" for all)
            filters: Optional dictionary of filters (e.g., {"id": 1, "status": "active"})
            
        Returns:
            List of matching rows as dictionaries
            
        Raises:
            SupabaseClientError: On database errors
        """
        start_time = time.time()
        
        try:
            query = self.client.table(table).select(columns)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            
            duration = (time.time() - start_time) * 1000  # Convert to ms
            row_count = len(response.data) if response.data else 0
            
            log_database_operation(
                operation="SELECT",
                table=table,
                success=True,
                duration=duration,
                affected_rows=row_count
            )
            
            return response.data or []
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"SELECT failed on table '{table}': {str(e)}"
            
            log_database_operation(
                operation="SELECT",
                table=table,
                success=False,
                duration=duration,
                error=error_msg
            )
            
            raise SupabaseClientError(error_msg)
    
    @retry(max_attempts=SupabaseConfig.MAX_RETRIES, delay=SupabaseConfig.RETRY_DELAY, backoff=2.0)
    @timing()
    def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Insert data into a table.
        
        Args:
            table: Table name
            data: Single dictionary or list of dictionaries to insert
            
        Returns:
            List of inserted rows as dictionaries
            
        Raises:
            SupabaseClientError: On database errors
        """
        start_time = time.time()
        
        try:
            response = self.client.table(table).insert(data).execute()
            
            duration = (time.time() - start_time) * 1000
            row_count = len(response.data) if response.data else 0
            
            log_database_operation(
                operation="INSERT",
                table=table,
                success=True,
                duration=duration,
                affected_rows=row_count
            )
            
            return response.data or []
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"INSERT failed on table '{table}': {str(e)}"
            
            log_database_operation(
                operation="INSERT",
                table=table,
                success=False,
                duration=duration,
                error=error_msg
            )
            
            raise SupabaseClientError(error_msg)
    
    @retry(max_attempts=SupabaseConfig.MAX_RETRIES, delay=SupabaseConfig.RETRY_DELAY, backoff=2.0)
    @timing()
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update data in a table.
        
        Args:
            table: Table name
            data: Dictionary of columns to update
            filters: Dictionary of filters to identify rows to update
            
        Returns:
            List of updated rows as dictionaries
            
        Raises:
            SupabaseClientError: On database errors
        """
        start_time = time.time()
        
        try:
            query = self.client.table(table).update(data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            duration = (time.time() - start_time) * 1000
            row_count = len(response.data) if response.data else 0
            
            log_database_operation(
                operation="UPDATE",
                table=table,
                success=True,
                duration=duration,
                affected_rows=row_count
            )
            
            return response.data or []
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"UPDATE failed on table '{table}': {str(e)}"
            
            log_database_operation(
                operation="UPDATE",
                table=table,
                success=False,
                duration=duration,
                error=error_msg
            )
            
            raise SupabaseClientError(error_msg)
    
    @retry(max_attempts=SupabaseConfig.MAX_RETRIES, delay=SupabaseConfig.RETRY_DELAY, backoff=2.0)
    @timing()
    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Delete data from a table.
        
        Args:
            table: Table name
            filters: Dictionary of filters to identify rows to delete
            
        Returns:
            List of deleted rows as dictionaries
            
        Raises:
            SupabaseClientError: On database errors
        """
        start_time = time.time()
        
        try:
            query = self.client.table(table).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            duration = (time.time() - start_time) * 1000
            row_count = len(response.data) if response.data else 0
            
            log_database_operation(
                operation="DELETE",
                table=table,
                success=True,
                duration=duration,
                affected_rows=row_count
            )
            
            return response.data or []
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"DELETE failed on table '{table}': {str(e)}"
            
            log_database_operation(
                operation="DELETE",
                table=table,
                success=False,
                duration=duration,
                error=error_msg
            )
            
            raise SupabaseClientError(error_msg)
    
    @retry(max_attempts=SupabaseConfig.MAX_RETRIES, delay=SupabaseConfig.RETRY_DELAY, backoff=2.0)
    @timing()
    def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        on_conflict: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Upsert (insert or update) data in a table.
        
        Args:
            table: Table name
            data: Single dictionary or list of dictionaries to upsert
            on_conflict: Column(s) to check for conflicts (default: primary key)
            
        Returns:
            List of upserted rows as dictionaries
            
        Raises:
            SupabaseClientError: On database errors
        """
        start_time = time.time()
        
        try:
            # Use upsert with on_conflict parameter directly
            response = self.client.table(table).upsert(
                data,
                on_conflict=on_conflict if on_conflict else None
            ).execute()
            
            duration = (time.time() - start_time) * 1000
            row_count = len(response.data) if response.data else 0
            
            log_database_operation(
                operation="UPSERT",
                table=table,
                success=True,
                duration=duration,
                affected_rows=row_count
            )
            
            return response.data or []
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"UPSERT failed on table '{table}': {str(e)}"
            
            log_database_operation(
                operation="UPSERT",
                table=table,
                success=False,
                duration=duration,
                error=error_msg
            )
            
            raise SupabaseClientError(error_msg)
    
    _table_names_cache: Optional[List[str]] = None
    
    def get_table_names(self) -> List[str]:
        """
        Get list of configured table names.
        
        Returns:
            List of table names from configuration (cached)
        """
        if SupabaseClient._table_names_cache is None:
            SupabaseClient._table_names_cache = list(SupabaseConfig.TABLES.values())
        return SupabaseClient._table_names_cache
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"SupabaseClient(url={self.url[:30]}..., tables={len(SupabaseConfig.TABLES)})"


# Global client instance
_supabase_instance: Optional[SupabaseClient] = None


def get_supabase_client(
    url: Optional[str] = None,
    key: Optional[str] = None,
    timeout: Optional[int] = None
) -> SupabaseClient:
    """
    Get or create a global Supabase client instance.
    
    Args:
        url: Optional Supabase URL (uses config if not provided)
        key: Optional Supabase API key (uses config if not provided)
        timeout: Optional request timeout (uses config if not provided)
        
    Returns:
        SupabaseClient instance
    """
    global _supabase_instance
    
    if _supabase_instance is None:
        _supabase_instance = SupabaseClient(
            url=url,
            key=key,
            timeout=timeout
        )
        logger.info("Global SupabaseClient instance created")
    
    return _supabase_instance


if __name__ == "__main__":
    # Example usage
    try:
        client = get_supabase_client()
        
        # Example: Select users
        users = client.select('users', columns='id,username,email', filters={'active': True})
        print(f"Found {len(users)} active users")
        
        # Example: Insert a new user
        new_user = {
            'username': 'test_user',
            'email': 'test@example.com',
            'active': True
        }
        # result = client.insert('users', new_user)
        # print(f"Inserted user: {result}")
        
    except SupabaseClientError as e:
        logger.error(f"Supabase Error: {e}")
