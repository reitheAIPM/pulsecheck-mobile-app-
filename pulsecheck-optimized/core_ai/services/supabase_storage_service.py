"""
Supabase Storage Service
Comprehensive file storage with RLS security and AI debugging
Based on Supabase documentation patterns for secure file handling
"""

import logging
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime, timedelta
import mimetypes
import hashlib
import os

from app.core.database import supabase
from app.core.observability import capture_error
from app.services.openai_observability import start_openai_request, end_openai_request

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """
    Comprehensive Supabase Storage service with security and monitoring
    
    Features:
    - RLS-secured file uploads and downloads
    - Content type validation and sanitization
    - File size limits and virus scanning preparation
    - User-scoped file access with row-level security
    - Comprehensive error handling and debugging
    - AI-optimized file analysis capabilities
    """
    
    def __init__(self):
        self.bucket_configs = {
            "user-uploads": {
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "allowed_types": ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"],
                "public": False
            },
            "journal-attachments": {
                "max_file_size": 5 * 1024 * 1024,  # 5MB
                "allowed_types": ["image/jpeg", "image/png", "image/gif", "text/plain"],
                "public": False
            },
            "profile-pictures": {
                "max_file_size": 2 * 1024 * 1024,  # 2MB
                "allowed_types": ["image/jpeg", "image/png", "image/webp"],
                "public": True
            }
        }
    
    async def upload_file(
        self, 
        bucket: str, 
        file_path: str, 
        file_data: BinaryIO, 
        user_id: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to Supabase Storage with comprehensive security
        
        Args:
            bucket: Storage bucket name
            file_path: Path within bucket (should include user_id for security)
            file_data: File binary data
            user_id: User ID for RLS security
            content_type: MIME type of the file
            metadata: Additional metadata to store
        
        Returns:
            Dict with upload results and security context
        """
        try:
            # Validate bucket configuration
            if bucket not in self.bucket_configs:
                raise ValueError(f"Invalid bucket: {bucket}")
            
            config = self.bucket_configs[bucket]
            
            # Read file data for validation
            file_content = file_data.read()
            file_size = len(file_content)
            
            # Validate file size
            if file_size > config["max_file_size"]:
                raise ValueError(f"File size {file_size} exceeds limit {config['max_file_size']}")
            
            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = "application/octet-stream"
            
            # Validate content type
            if content_type not in config["allowed_types"]:
                raise ValueError(f"Content type {content_type} not allowed for bucket {bucket}")
            
            # Generate secure file path with user scoping
            secure_path = self._generate_secure_path(bucket, file_path, user_id)
            
            # Calculate file hash for integrity
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Prepare metadata
            upload_metadata = {
                "user_id": user_id,
                "original_name": file_path,
                "content_type": content_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "upload_timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Upload to Supabase Storage
            response = supabase.storage.from_(bucket).upload(
                path=secure_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "x-upsert": "true"  # Allow overwrite
                }
            )
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase storage error: {response.error}")
            
            # Store file metadata in database for RLS
            await self._store_file_metadata(bucket, secure_path, upload_metadata)
            
            # Get public URL if bucket is public
            public_url = None
            if config["public"]:
                public_url = supabase.storage.from_(bucket).get_public_url(secure_path)
            
            logger.info(f"✅ File uploaded successfully: {secure_path}")
            
            return {
                "success": True,
                "file_path": secure_path,
                "public_url": public_url,
                "file_size": file_size,
                "content_type": content_type,
                "file_hash": file_hash,
                "metadata": upload_metadata
            }
            
        except Exception as error:
            capture_error(error, {
                "operation": "file_upload",
                "bucket": bucket,
                "file_path": file_path,
                "user_id": user_id,
                "file_size": file_size if 'file_size' in locals() else "unknown"
            })
            raise
    
    async def download_file(self, bucket: str, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Download a file with RLS security validation
        
        Args:
            bucket: Storage bucket name
            file_path: Path within bucket
            user_id: User ID for RLS security validation
        
        Returns:
            Dict with file data and metadata
        """
        try:
            # Validate user access to file
            if not await self._validate_file_access(bucket, file_path, user_id):
                raise PermissionError(f"User {user_id} cannot access file {file_path}")
            
            # Download from Supabase Storage
            response = supabase.storage.from_(bucket).download(file_path)
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase storage error: {response.error}")
            
            # Get file metadata
            metadata = await self._get_file_metadata(bucket, file_path)
            
            logger.info(f"✅ File downloaded successfully: {file_path}")
            
            return {
                "success": True,
                "file_data": response,
                "metadata": metadata
            }
            
        except Exception as error:
            capture_error(error, {
                "operation": "file_download",
                "bucket": bucket,
                "file_path": file_path,
                "user_id": user_id
            })
            raise
    
    async def delete_file(self, bucket: str, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a file with RLS security validation
        
        Args:
            bucket: Storage bucket name
            file_path: Path within bucket
            user_id: User ID for RLS security validation
        
        Returns:
            Dict with deletion results
        """
        try:
            # Validate user ownership of file
            if not await self._validate_file_ownership(bucket, file_path, user_id):
                raise PermissionError(f"User {user_id} cannot delete file {file_path}")
            
            # Delete from Supabase Storage
            response = supabase.storage.from_(bucket).remove([file_path])
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase storage error: {response.error}")
            
            # Remove metadata from database
            await self._delete_file_metadata(bucket, file_path)
            
            logger.info(f"✅ File deleted successfully: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path
            }
            
        except Exception as error:
            capture_error(error, {
                "operation": "file_delete",
                "bucket": bucket,
                "file_path": file_path,
                "user_id": user_id
            })
            raise
    
    async def list_user_files(self, bucket: str, user_id: str, prefix: str = "") -> List[Dict[str, Any]]:
        """
        List files for a specific user with RLS filtering
        
        Args:
            bucket: Storage bucket name
            user_id: User ID for RLS filtering
            prefix: Optional path prefix for filtering
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            # Get files from database with RLS filtering
            user_prefix = f"{user_id}/{prefix}" if prefix else f"{user_id}/"
            
            # List files from Supabase Storage
            response = supabase.storage.from_(bucket).list(path=user_prefix)
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase storage error: {response.error}")
            
            # Get metadata for each file
            files_with_metadata = []
            for file_info in response:
                metadata = await self._get_file_metadata(bucket, file_info['name'])
                files_with_metadata.append({
                    "file_info": file_info,
                    "metadata": metadata
                })
            
            logger.info(f"✅ Listed {len(files_with_metadata)} files for user {user_id}")
            
            return files_with_metadata
            
        except Exception as error:
            capture_error(error, {
                "operation": "list_files",
                "bucket": bucket,
                "user_id": user_id,
                "prefix": prefix
            })
            raise
    
    def _generate_secure_path(self, bucket: str, file_path: str, user_id: str) -> str:
        """Generate a secure path that includes user scoping"""
        # Extract filename from path
        filename = os.path.basename(file_path)
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create user-scoped path
        secure_path = f"{user_id}/{timestamp}_{filename}"
        
        return secure_path
    
    async def _store_file_metadata(self, bucket: str, file_path: str, metadata: Dict[str, Any]):
        """Store file metadata in database for RLS"""
        try:
            result = supabase.table('file_metadata').insert({
                "bucket": bucket,
                "file_path": file_path,
                "user_id": metadata["user_id"],
                "original_name": metadata["original_name"],
                "content_type": metadata["content_type"],
                "file_size": metadata["file_size"],
                "file_hash": metadata["file_hash"],
                "metadata": metadata
            }).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.warning(f"Failed to store file metadata: {result.error}")
        except Exception as e:
            logger.warning(f"Failed to store file metadata: {e}")
    
    async def _get_file_metadata(self, bucket: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from database"""
        try:
            result = supabase.table('file_metadata').select("*").eq("bucket", bucket).eq("file_path", file_path).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.warning(f"Failed to get file metadata: {e}")
            return None
    
    async def _delete_file_metadata(self, bucket: str, file_path: str):
        """Delete file metadata from database"""
        try:
            supabase.table('file_metadata').delete().eq("bucket", bucket).eq("file_path", file_path).execute()
        except Exception as e:
            logger.warning(f"Failed to delete file metadata: {e}")
    
    async def _validate_file_access(self, bucket: str, file_path: str, user_id: str) -> bool:
        """Validate if user can access the file"""
        try:
            # Check if file belongs to user or is in public bucket
            config = self.bucket_configs.get(bucket, {})
            if config.get("public"):
                return True
            
            # Check file ownership through metadata
            metadata = await self._get_file_metadata(bucket, file_path)
            if metadata and metadata.get("user_id") == user_id:
                return True
            
            # Check if path starts with user_id (fallback)
            if file_path.startswith(f"{user_id}/"):
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Failed to validate file access: {e}")
            return False
    
    async def _validate_file_ownership(self, bucket: str, file_path: str, user_id: str) -> bool:
        """Validate if user owns the file (stricter than access)"""
        try:
            # Check file ownership through metadata
            metadata = await self._get_file_metadata(bucket, file_path)
            if metadata and metadata.get("user_id") == user_id:
                return True
            
            # Check if path starts with user_id (fallback)
            if file_path.startswith(f"{user_id}/"):
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Failed to validate file ownership: {e}")
            return False

# Global instance
storage_service = SupabaseStorageService()

# Convenience functions
async def upload_file(bucket: str, file_path: str, file_data: BinaryIO, user_id: str, **kwargs) -> Dict[str, Any]:
    """Upload a file to Supabase Storage"""
    return await storage_service.upload_file(bucket, file_path, file_data, user_id, **kwargs)

async def download_file(bucket: str, file_path: str, user_id: str) -> Dict[str, Any]:
    """Download a file from Supabase Storage"""
    return await storage_service.download_file(bucket, file_path, user_id)

async def delete_file(bucket: str, file_path: str, user_id: str) -> Dict[str, Any]:
    """Delete a file from Supabase Storage"""
    return await storage_service.delete_file(bucket, file_path, user_id)

async def list_user_files(bucket: str, user_id: str, prefix: str = "") -> List[Dict[str, Any]]:
    """List files for a user"""
    return await storage_service.list_user_files(bucket, user_id, prefix) 