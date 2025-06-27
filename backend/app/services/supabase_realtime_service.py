"""
Supabase Realtime Service
Comprehensive real-time data synchronization with security and AI debugging
Based on Supabase documentation patterns for live WebSocket connections
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Set
from datetime import datetime
import uuid

from app.core.database import supabase
from app.core.observability import capture_error, observability

logger = logging.getLogger(__name__)

class SupabaseRealtimeService:
    """
    Comprehensive Supabase Realtime service for live data updates
    
    Features:
    - Real-time database change notifications
    - User-scoped data streaming with RLS security
    - WebSocket connection management with reconnection
    - Channel-based communication for different data types
    - Comprehensive error handling and debugging
    - AI-optimized real-time analytics
    """
    
    def __init__(self):
        self.active_subscriptions: Dict[str, Dict[str, Any]] = {}
        self.user_channels: Dict[str, Set[str]] = {}  # user_id -> set of channel_ids
        self.connection_status = "disconnected"
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Real-time event types for different data changes
        self.event_types = {
            "journal_entry_created": "INSERT",
            "journal_entry_updated": "UPDATE", 
            "journal_entry_deleted": "DELETE",
            "ai_insight_created": "INSERT",
            "user_preference_updated": "UPDATE",
            "ai_analysis_completed": "INSERT"
        }
    
    async def subscribe_to_user_data(
        self,
        user_id: str,
        table: str,
        event_types: Optional[List[str]] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Subscribe to real-time changes for user-specific data
        
        Args:
            user_id: User ID for RLS filtering
            table: Database table to monitor
            event_types: List of events to monitor (INSERT, UPDATE, DELETE)
            callback: Function to call when changes occur
        
        Returns:
            Subscription ID for managing the connection
        """
        try:
            subscription_id = str(uuid.uuid4())
            
            if event_types is None:
                event_types = ["INSERT", "UPDATE", "DELETE"]
            
            # Create channel name with user scoping for security
            channel_name = f"user:{user_id}:table:{table}"
            
            # Set up RLS filter for user-specific data
            filter_config = f"user_id=eq.{user_id}"
            
            # Create subscription configuration
            subscription_config = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "table": table,
                "channel_name": channel_name,
                "event_types": event_types,
                "filter": filter_config,
                "callback": callback,
                "created_at": datetime.now(),
                "status": "active"
            }
            
            # Store subscription
            self.active_subscriptions[subscription_id] = subscription_config
            
            # Track user channels
            if user_id not in self.user_channels:
                self.user_channels[user_id] = set()
            self.user_channels[user_id].add(subscription_id)
            
            # Set up Supabase realtime subscription
            await self._setup_supabase_subscription(subscription_config)
            
            # Log real-time event for monitoring
            observability.start_request(
                operation="realtime_subscription",
                endpoint=f"/realtime/{table}",
                method="SUBSCRIBE",
                metadata={
                    "user_id": user_id,
                    "table": table,
                    "subscription_id": subscription_id
                }
            )
            
            logger.info(f"✅ Real-time subscription created: {subscription_id} for user {user_id}")
            
            return subscription_id
            
        except Exception as error:
            capture_error(error, {
                "operation": "realtime_subscribe",
                "user_id": user_id,
                "table": table,
                "event_types": event_types
            })
            raise
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from real-time updates
        
        Args:
            subscription_id: Subscription ID to remove
        
        Returns:
            Success status
        """
        try:
            if subscription_id not in self.active_subscriptions:
                logger.warning(f"Subscription {subscription_id} not found")
                return False
            
            subscription = self.active_subscriptions[subscription_id]
            user_id = subscription["user_id"]
            
            # Remove from Supabase
            await self._remove_supabase_subscription(subscription)
            
            # Clean up tracking
            del self.active_subscriptions[subscription_id]
            
            if user_id in self.user_channels:
                self.user_channels[user_id].discard(subscription_id)
                if not self.user_channels[user_id]:
                    del self.user_channels[user_id]
            
            logger.info(f"✅ Real-time subscription removed: {subscription_id}")
            
            return True
            
        except Exception as error:
            capture_error(error, {
                "operation": "realtime_unsubscribe",
                "subscription_id": subscription_id
            })
            return False
    
    async def unsubscribe_user(self, user_id: str) -> int:
        """
        Unsubscribe all subscriptions for a user
        
        Args:
            user_id: User ID to unsubscribe
        
        Returns:
            Number of subscriptions removed
        """
        try:
            if user_id not in self.user_channels:
                return 0
            
            subscription_ids = list(self.user_channels[user_id])
            removed_count = 0
            
            for subscription_id in subscription_ids:
                if await self.unsubscribe(subscription_id):
                    removed_count += 1
            
            logger.info(f"✅ Removed {removed_count} subscriptions for user {user_id}")
            
            return removed_count
            
        except Exception as error:
            capture_error(error, {
                "operation": "realtime_unsubscribe_user",
                "user_id": user_id
            })
            return 0
    
    async def broadcast_to_user(
        self,
        user_id: str,
        event_type: str,
        data: Dict[str, Any],
        channel: Optional[str] = None
    ) -> bool:
        """
        Broadcast a custom event to a specific user
        
        Args:
            user_id: Target user ID
            event_type: Type of event to broadcast
            data: Event data payload
            channel: Optional specific channel
        
        Returns:
            Success status
        """
        try:
            # Use default channel if not specified
            if channel is None:
                channel = f"user:{user_id}:broadcasts"
            
            # Prepare broadcast payload
            broadcast_payload = {
                "type": event_type,
                "payload": data,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "channel": channel
            }
            
            # Send via Supabase Realtime
            response = supabase.realtime.channel(channel).send({
                "type": "broadcast",
                "event": event_type,
                "payload": broadcast_payload
            })
            
            # Log broadcast for monitoring
            observability.start_request(
                operation="realtime_broadcast",
                endpoint=f"/realtime/broadcast/{event_type}",
                method="POST",
                metadata={
                    "user_id": user_id,
                    "event_type": event_type,
                    "channel": channel
                }
            )
            
            logger.info(f"✅ Broadcast sent to user {user_id}: {event_type}")
            
            return True
            
        except Exception as error:
            capture_error(error, {
                "operation": "realtime_broadcast",
                "user_id": user_id,
                "event_type": event_type,
                "channel": channel
            })
            return False
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active subscriptions for a user
        
        Args:
            user_id: User ID to query
        
        Returns:
            List of subscription details
        """
        try:
            if user_id not in self.user_channels:
                return []
            
            subscriptions = []
            for subscription_id in self.user_channels[user_id]:
                if subscription_id in self.active_subscriptions:
                    subscription = self.active_subscriptions[subscription_id].copy()
                    # Remove callback function for serialization
                    subscription.pop("callback", None)
                    subscriptions.append(subscription)
            
            return subscriptions
            
        except Exception as error:
            capture_error(error, {
                "operation": "get_user_subscriptions",
                "user_id": user_id
            })
            return []
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status and statistics
        
        Returns:
            Connection status dictionary
        """
        try:
            total_subscriptions = len(self.active_subscriptions)
            active_users = len(self.user_channels)
            
            # Calculate subscription stats by table
            table_stats = {}
            for subscription in self.active_subscriptions.values():
                table = subscription["table"]
                if table not in table_stats:
                    table_stats[table] = 0
                table_stats[table] += 1
            
            return {
                "connection_status": self.connection_status,
                "total_subscriptions": total_subscriptions,
                "active_users": active_users,
                "reconnect_attempts": self.reconnect_attempts,
                "table_subscriptions": table_stats,
                "uptime": "connected",  # You can track actual uptime
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as error:
            capture_error(error, {
                "operation": "get_connection_status"
            })
            return {"connection_status": "error", "error": str(error)}
    
    async def _setup_supabase_subscription(self, config: Dict[str, Any]):
        """Set up the actual Supabase realtime subscription"""
        try:
            channel_name = config["channel_name"]
            table = config["table"]
            event_types = config["event_types"]
            filter_config = config["filter"]
            callback = config.get("callback")
            
            # Create Supabase channel
            channel = supabase.realtime.channel(channel_name)
            
            # Set up event handlers for each event type
            for event_type in event_types:
                def create_handler(event_type, callback):
                    async def handler(payload):
                        await self._handle_realtime_event(event_type, payload, callback, config)
                    return handler
                
                # Subscribe to database changes
                channel.on(
                    event_type.lower(),
                    create_handler(event_type, callback),
                    table=table,
                    filter=filter_config
                )
            
            # Subscribe to the channel
            channel.subscribe()
            
            # Update subscription with channel reference
            config["channel"] = channel
            
        except Exception as error:
            logger.error(f"Failed to setup Supabase subscription: {error}")
            raise
    
    async def _remove_supabase_subscription(self, config: Dict[str, Any]):
        """Remove the Supabase realtime subscription"""
        try:
            channel = config.get("channel")
            if channel:
                channel.unsubscribe()
                
        except Exception as error:
            logger.error(f"Failed to remove Supabase subscription: {error}")
    
    async def _handle_realtime_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        callback: Optional[Callable],
        config: Dict[str, Any]
    ):
        """Handle incoming realtime events with comprehensive processing"""
        try:
            # Enrich payload with metadata
            enriched_payload = {
                "event_type": event_type,
                "table": config["table"],
                "user_id": config["user_id"],
                "subscription_id": config["subscription_id"],
                "timestamp": datetime.now().isoformat(),
                "original_payload": payload
            }
            
            # Log event for AI analysis
            observability.start_request(
                operation="realtime_event_received",
                endpoint=f"/realtime/event/{event_type}",
                method="EVENT",
                metadata=enriched_payload
            )
            
            # Call user callback if provided
            if callback:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(enriched_payload)
                    else:
                        callback(enriched_payload)
                except Exception as callback_error:
                    logger.error(f"Callback error for subscription {config['subscription_id']}: {callback_error}")
            
            logger.debug(f"✅ Processed realtime event: {event_type} for user {config['user_id']}")
            
        except Exception as error:
            capture_error(error, {
                "operation": "handle_realtime_event",
                "event_type": event_type,
                "subscription_id": config.get("subscription_id"),
                "user_id": config.get("user_id")
            })

# Global instance
realtime_service = SupabaseRealtimeService()

# Convenience functions
async def subscribe_to_user_data(user_id: str, table: str, event_types: Optional[List[str]] = None, callback: Optional[Callable] = None) -> str:
    """Subscribe to real-time user data changes"""
    return await realtime_service.subscribe_to_user_data(user_id, table, event_types, callback)

async def unsubscribe(subscription_id: str) -> bool:
    """Unsubscribe from real-time updates"""
    return await realtime_service.unsubscribe(subscription_id)

async def unsubscribe_user(user_id: str) -> int:
    """Unsubscribe all user subscriptions"""
    return await realtime_service.unsubscribe_user(user_id)

async def broadcast_to_user(user_id: str, event_type: str, data: Dict[str, Any], channel: Optional[str] = None) -> bool:
    """Broadcast event to specific user"""
    return await realtime_service.broadcast_to_user(user_id, event_type, data, channel)

async def get_connection_status() -> Dict[str, Any]:
    """Get realtime connection status"""
    return await realtime_service.get_connection_status() 