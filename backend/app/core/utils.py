"""
Core utility functions for the PulseCheck application.

This module provides centralized utility functions to prevent code duplication
and ensure consistent handling of common operations across the application.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DateTimeUtils:
    """Centralized datetime handling utilities."""
    
    @staticmethod
    def ensure_updated_at(entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure entry has a valid updated_at field.
        
        This function handles the recurring pattern found in 11 places across the codebase
        where we check if 'updated_at' is None or missing and set it to created_at or now.
        
        Args:
            entry: Dictionary containing entry data
            
        Returns:
            Dictionary with guaranteed updated_at field
        """
        if 'updated_at' not in entry or entry['updated_at'] is None:
            entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
        return entry
    
    @staticmethod
    def ensure_updated_at_bulk(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ensure multiple entries have valid updated_at fields.
        
        Args:
            entries: List of entry dictionaries
            
        Returns:
            List of entries with guaranteed updated_at fields
        """
        return [DateTimeUtils.ensure_updated_at(entry) for entry in entries]
    
    @staticmethod
    def normalize_datetime_fields(entry: Dict[str, Any], fields: List[str] = None) -> Dict[str, Any]:
        """
        Normalize datetime fields to ensure consistency.
        
        Args:
            entry: Dictionary containing entry data
            fields: List of field names to normalize (defaults to common datetime fields)
            
        Returns:
            Dictionary with normalized datetime fields
        """
        if fields is None:
            fields = ['created_at', 'updated_at', 'ai_generated_at', 'last_login', 'expires_at']
        
        for field in fields:
            if field in entry and entry[field] is not None:
                # Ensure timezone-aware datetime
                if isinstance(entry[field], str):
                    try:
                        entry[field] = datetime.fromisoformat(entry[field].replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Failed to parse datetime field {field}: {entry[field]}")
                        continue
                        
                # Ensure timezone-aware
                if isinstance(entry[field], datetime) and entry[field].tzinfo is None:
                    entry[field] = entry[field].replace(tzinfo=timezone.utc)
        
        return entry


class SupabaseQueryUtils:
    """Centralized Supabase query utilities to prevent common errors."""
    
    @staticmethod
    def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> tuple[int, int]:
        """
        Validate and normalize pagination parameters.
        
        Args:
            page: Page number
            per_page: Items per page
            max_per_page: Maximum allowed items per page
            
        Returns:
            Tuple of (validated_page, validated_per_page)
        """
        if page < 1:
            page = 1
        if per_page < 1 or per_page > max_per_page:
            per_page = min(max_per_page, max(1, per_page))
        return page, per_page
    
    @staticmethod
    def safe_count_query(client, table_name: str, filters: Dict[str, Any] = None) -> int:
        """
        Safely execute a count query with proper error handling.
        
        Args:
            client: Supabase client
            table_name: Name of the table
            filters: Optional filters to apply
            
        Returns:
            Count of records or 0 if error
        """
        try:
            query = client.table(table_name).select("id", count="exact")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.count if result.count else 0
        except Exception as e:
            logger.error(f"Error in count query for {table_name}: {str(e)}")
            return 0
    
    @staticmethod
    def safe_range_query(client, table_name: str, offset: int, limit: int, 
                        filters: Dict[str, Any] = None, order_by: str = "created_at",
                        order_desc: bool = True) -> List[Dict[str, Any]]:
        """
        Safely execute a range query with proper error handling.
        
        Args:
            client: Supabase client
            table_name: Name of the table
            offset: Starting offset
            limit: Number of records to fetch
            filters: Optional filters to apply
            order_by: Field to order by
            order_desc: Whether to order descending
            
        Returns:
            List of records or empty list if error
        """
        try:
            query = client.table(table_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            query = query.order(order_by, desc=order_desc)
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error in range query for {table_name}: {str(e)}")
            return []


class ValidationUtils:
    """Centralized validation utilities."""
    
    @staticmethod
    def validate_uuid(value: str) -> bool:
        """
        Validate if a string is a valid UUID.
        
        Args:
            value: String to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            import uuid
            uuid.UUID(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate that required fields are present and not empty.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        return missing_fields


class ResponseUtils:
    """Centralized response formatting utilities."""
    
    @staticmethod
    def format_pagination_response(data: List[Dict[str, Any]], page: int, per_page: int, 
                                 total: int) -> Dict[str, Any]:
        """
        Format a paginated response with consistent structure.
        
        Args:
            data: List of data items
            page: Current page number
            per_page: Items per page
            total: Total number of items
            
        Returns:
            Formatted pagination response
        """
        return {
            "data": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1
            }
        }
    
    @staticmethod
    def format_error_response(error_message: str, error_code: str = None, 
                            details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format an error response with consistent structure.
        
        Args:
            error_message: Main error message
            error_code: Optional error code
            details: Optional additional details
            
        Returns:
            Formatted error response
        """
        response = {
            "error": True,
            "message": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
            
        return response


# Backward compatibility aliases
ensure_updated_at = DateTimeUtils.ensure_updated_at
ensure_updated_at_bulk = DateTimeUtils.ensure_updated_at_bulk
validate_pagination = SupabaseQueryUtils.validate_pagination
safe_count_query = SupabaseQueryUtils.safe_count_query
safe_range_query = SupabaseQueryUtils.safe_range_query 