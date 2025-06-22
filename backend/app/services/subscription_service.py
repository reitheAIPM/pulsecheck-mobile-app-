"""
Subscription Service for PulseCheck - Beta Testing Focus
Handles premium feature toggles for beta testers (free during beta)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import logging

from app.models.user import UserTable, SubscriptionTier
from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

class SubscriptionService:
    """
    Handles subscription logic and premium feature access
    During beta: All premium features are FREE for beta testers
    """
    
    def __init__(self):
        # Beta testing configuration
        self.beta_mode = True  # Set to False when launching paid subscriptions
        self.free_personas = ["pulse"]  # Always free
        self.premium_personas = ["sage", "spark", "anchor"]  # Premium (free during beta)
        
        # Usage limits (generous during beta)
        self.free_daily_limit = 10  # Free tier: 10 AI requests per day
        self.premium_daily_limit = 100  # Premium tier: 100 AI requests per day
        self.beta_daily_limit = 50  # Beta testers: 50 AI requests per day
    
    def get_user_subscription_status(self, user: UserTable) -> Dict[str, Any]:
        """
        Get comprehensive subscription status for a user
        """
        try:
            # Determine if user has premium access
            has_premium_access = self._has_premium_access(user)
            
            # Get available personas based on subscription
            available_personas = self._get_available_personas(user, has_premium_access)
            
            # Get daily limit
            daily_limit = self._get_daily_limit(user, has_premium_access)
            
            return {
                "tier": user.subscription_tier,
                "is_premium_active": has_premium_access,
                "premium_expires_at": user.premium_expires_at,
                "is_beta_tester": user.is_beta_tester,
                "beta_premium_enabled": user.beta_premium_enabled,
                "available_personas": available_personas,
                "ai_requests_today": user.ai_requests_today or 0,
                "daily_limit": daily_limit,
                "beta_mode": self.beta_mode,
                "premium_features": {
                    "advanced_personas": has_premium_access,
                    "pattern_insights": has_premium_access,
                    "unlimited_history": has_premium_access,
                    "priority_support": has_premium_access
                }
            }
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": str(user.id),
                "operation": "get_subscription_status"
            })
            # Return safe defaults
            return {
                "tier": SubscriptionTier.FREE,
                "is_premium_active": False,
                "premium_expires_at": None,
                "is_beta_tester": False,
                "beta_premium_enabled": False,
                "available_personas": self.free_personas,
                "ai_requests_today": 0,
                "daily_limit": self.free_daily_limit,
                "beta_mode": self.beta_mode,
                "premium_features": {
                    "advanced_personas": False,
                    "pattern_insights": False,
                    "unlimited_history": False,
                    "priority_support": False
                }
            }
    
    def _has_premium_access(self, user: UserTable) -> bool:
        """
        Determine if user has premium access
        During beta: Beta testers with toggle enabled get free premium
        """
        # Beta testers with premium toggle enabled (FREE during beta)
        if user.is_beta_tester and user.beta_premium_enabled:
            return True
        
        # Paid premium subscribers (when not in beta mode)
        if not self.beta_mode and user.subscription_tier == SubscriptionTier.PREMIUM:
            if user.premium_expires_at and user.premium_expires_at > datetime.now(timezone.utc):
                return True
        
        return False
    
    def _get_available_personas(self, user: UserTable, has_premium: bool) -> List[str]:
        """
        Get list of available AI personas for user
        """
        if has_premium:
            return self.free_personas + self.premium_personas
        else:
            return self.free_personas
    
    def _get_daily_limit(self, user: UserTable, has_premium: bool) -> int:
        """
        Get daily AI request limit for user
        """
        if user.is_beta_tester:
            return self.beta_daily_limit
        elif has_premium:
            return self.premium_daily_limit
        else:
            return self.free_daily_limit
    
    def can_use_persona(self, user: UserTable, persona: str) -> bool:
        """
        Check if user can use a specific AI persona
        """
        try:
            has_premium = self._has_premium_access(user)
            available_personas = self._get_available_personas(user, has_premium)
            return persona.lower() in [p.lower() for p in available_personas]
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": str(user.id),
                "persona": persona,
                "operation": "can_use_persona"
            })
            # Default to allowing only free personas
            return persona.lower() in [p.lower() for p in self.free_personas]
    
    def can_make_ai_request(self, user: UserTable) -> tuple[bool, str]:
        """
        Check if user can make an AI request (within daily limits)
        Returns: (can_request, reason_if_not)
        """
        try:
            has_premium = self._has_premium_access(user)
            daily_limit = self._get_daily_limit(user, has_premium)
            current_usage = user.ai_requests_today or 0
            
            if current_usage >= daily_limit:
                if user.is_beta_tester:
                    return False, f"Beta daily limit reached ({daily_limit} requests)"
                elif has_premium:
                    return False, f"Premium daily limit reached ({daily_limit} requests)"
                else:
                    return False, f"Free daily limit reached ({daily_limit} requests). Upgrade for more!"
            
            return True, ""
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": str(user.id),
                "operation": "can_make_ai_request"
            })
            # Default to allowing request but with conservative limit
            return (user.ai_requests_today or 0) < 5, "Error checking limits"
    
    def toggle_beta_premium(self, db: Session, user_id: str, enabled: bool) -> Dict[str, Any]:
        """
        Toggle premium features for beta tester (FREE during beta)
        """
        try:
            user = db.query(UserTable).filter(UserTable.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            if not user.is_beta_tester:
                return {"success": False, "error": "User is not a beta tester"}
            
            # Toggle beta premium (FREE during beta)
            user.beta_premium_enabled = enabled
            db.commit()
            
            # Get updated status
            status = self.get_user_subscription_status(user)
            
            logger.info(f"Beta premium toggled for user {user_id}: {enabled}")
            
            return {
                "success": True,
                "beta_premium_enabled": enabled,
                "subscription_status": status,
                "message": f"Beta premium features {'enabled' if enabled else 'disabled'} (FREE during beta)"
            }
            
        except Exception as e:
            log_error(e, ErrorSeverity.HIGH, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": user_id,
                "enabled": enabled,
                "operation": "toggle_beta_premium"
            })
            return {"success": False, "error": "Failed to toggle beta premium"}
    
    def make_user_beta_tester(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Grant beta tester status to a user
        """
        try:
            user = db.query(UserTable).filter(UserTable.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            user.is_beta_tester = True
            user.beta_features_enabled = True
            # Don't auto-enable premium, let them toggle it
            db.commit()
            
            logger.info(f"User {user_id} granted beta tester status")
            
            return {
                "success": True,
                "is_beta_tester": True,
                "message": "Beta tester status granted. You can now toggle premium features for free!"
            }
            
        except Exception as e:
            log_error(e, ErrorSeverity.HIGH, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": user_id,
                "operation": "make_user_beta_tester"
            })
            return {"success": False, "error": "Failed to grant beta tester status"}
    
    def increment_ai_usage(self, db: Session, user_id: str) -> bool:
        """
        Increment user's daily AI usage counter
        """
        try:
            user = db.query(UserTable).filter(UserTable.id == user_id).first()
            if not user:
                return False
            
            # Reset daily counter if it's a new day
            if user.last_ai_request:
                last_request_date = user.last_ai_request.date()
                today = datetime.now(timezone.utc).date()
                if last_request_date != today:
                    user.ai_requests_today = 0
            
            # Increment counters
            user.ai_requests_today = (user.ai_requests_today or 0) + 1
            user.ai_requests_this_month = (user.ai_requests_this_month or 0) + 1
            user.last_ai_request = datetime.now(timezone.utc)
            
            db.commit()
            return True
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": user_id,
                "operation": "increment_ai_usage"
            })
            return False
    
    def get_usage_analytics(self, user: UserTable) -> Dict[str, Any]:
        """
        Get usage analytics for user
        """
        try:
            has_premium = self._has_premium_access(user)
            daily_limit = self._get_daily_limit(user, has_premium)
            
            return {
                "ai_requests_today": user.ai_requests_today or 0,
                "ai_requests_this_month": user.ai_requests_this_month or 0,
                "daily_limit": daily_limit,
                "requests_remaining": max(0, daily_limit - (user.ai_requests_today or 0)),
                "usage_percentage": min(100, ((user.ai_requests_today or 0) / daily_limit) * 100),
                "last_ai_request": user.last_ai_request,
                "subscription_tier": user.subscription_tier,
                "is_beta_tester": user.is_beta_tester,
                "beta_premium_enabled": user.beta_premium_enabled
            }
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": str(user.id),
                "operation": "get_usage_analytics"
            })
            return {
                "ai_requests_today": 0,
                "ai_requests_this_month": 0,
                "daily_limit": self.free_daily_limit,
                "requests_remaining": self.free_daily_limit,
                "usage_percentage": 0,
                "last_ai_request": None,
                "subscription_tier": SubscriptionTier.FREE,
                "is_beta_tester": False,
                "beta_premium_enabled": False
            }

# Global subscription service instance
subscription_service = SubscriptionService() 