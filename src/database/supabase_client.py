"""
Supabase Client Wrapper for FootyBot
"""

from typing import Optional, Dict, Any, List
import time
from supabase import create_client, Client
from config.settings import SupabaseConfig
from src.utils.logger import logger, log_database_operation, log_error


class SupabaseClientError(Exception):
    """Base exception for Supabase client errors."""
    pass


class SupabaseClient:
    """
    Wrapper for Supabase client with error handling and logging.
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """Initialize Supabase client."""
        self.url = url or SupabaseConfig.URL
        self.key = key or SupabaseConfig.KEY
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key are required")
        
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            log_error(e, context={'url': self.url})
            raise SupabaseClientError(f"Failed to initialize: {str(e)}")
    
    def select(self, table: str, columns: str = "*", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Select data from table with optional filters.
        
        Args:
            table: Table name
            columns: Columns to select (default: "*")
            filters: Dictionary of filters to apply (e.g., {'id': 1, 'status': 'active'})
            
        Returns:
            List of rows as dictionaries
            
        Raises:
            SupabaseClientError: If query fails
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
            
            log_database_operation(
                operation="SELECT",
                table=table,
                success=True,
                duration=duration,
                affected_rows=len(response.data)
            )
            
            return response.data
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation(
                operation="SELECT",
                table=table,
                success=False,
                duration=duration,
                error=str(e)
            )
            log_error(e, context={'table': table, 'filters': filters})
            raise SupabaseClientError(f"Select failed: {str(e)}")
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert data into table.
        
        Args:
            table: Table name
            data: Dictionary of data to insert
            
        Returns:
            Inserted row as dictionary
            
        Raises:
            SupabaseClientError: If insert fails
        """
        start_time = time.time()
        try:
            response = self.client.table(table).insert(data).execute()
            duration = (time.time() - start_time) * 1000
            
            log_database_operation(
                operation="INSERT",
                table=table,
                success=True,
                duration=duration,
                affected_rows=len(response.data)
            )
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation(
                operation="INSERT",
                table=table,
                success=False,
                duration=duration,
                error=str(e)
            )
            log_error(e, context={'table': table, 'data': data})
            raise SupabaseClientError(f"Insert failed: {str(e)}")
    
    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Update data in table.
        
        Args:
            table: Table name
            data: Dictionary of data to update
            filters: Dictionary of filters to identify rows (e.g., {'id': 1})
            
        Returns:
            List of updated rows as dictionaries
            
        Raises:
            SupabaseClientError: If update fails
        """
        start_time = time.time()
        try:
            query = self.client.table(table).update(data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            duration = (time.time() - start_time) * 1000
            
            log_database_operation(
                operation="UPDATE",
                table=table,
                success=True,
                duration=duration,
                affected_rows=len(response.data)
            )
            
            return response.data
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation(
                operation="UPDATE",
                table=table,
                success=False,
                duration=duration,
                error=str(e)
            )
            log_error(e, context={'table': table, 'data': data, 'filters': filters})
            raise SupabaseClientError(f"Update failed: {str(e)}")
    
    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Delete data from table.
        
        Args:
            table: Table name
            filters: Dictionary of filters to identify rows (e.g., {'id': 1})
            
        Returns:
            List of deleted rows as dictionaries
            
        Raises:
            SupabaseClientError: If delete fails
        """
        start_time = time.time()
        try:
            query = self.client.table(table).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            duration = (time.time() - start_time) * 1000
            
            log_database_operation(
                operation="DELETE",
                table=table,
                success=True,
                duration=duration,
                affected_rows=len(response.data)
            )
            
            return response.data
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation(
                operation="DELETE",
                table=table,
                success=False,
                duration=duration,
                error=str(e)
            )
            log_error(e, context={'table': table, 'filters': filters})
            raise SupabaseClientError(f"Delete failed: {str(e)}")
    
    def upsert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert or update data.
        
        Args:
            table: Table name
            data: Dictionary of data to upsert
            
        Returns:
            Upserted row as dictionary
            
        Raises:
            SupabaseClientError: If upsert fails
        """
        start_time = time.time()
        try:
            response = self.client.table(table).upsert(data).execute()
            duration = (time.time() - start_time) * 1000
            
            log_database_operation(
                operation="UPSERT",
                table=table,
                success=True,
                duration=duration,
                affected_rows=len(response.data)
            )
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_database_operation(
                operation="UPSERT",
                table=table,
                success=False,
                duration=duration,
                error=str(e)
            )
            log_error(e, context={'table': table, 'data': data})
            raise SupabaseClientError(f"Upsert failed: {str(e)}")


# Global instance
_supabase_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """Get or create global Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


__all__ = ['SupabaseClient', 'SupabaseClientError', 'get_supabase_client']
