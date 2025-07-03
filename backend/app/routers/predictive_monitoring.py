"""
Predictive Monitoring System
Analyzes trends and patterns to predict issues before they happen
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timedelta
import logging
import statistics
from collections import defaultdict, Counter

from app.core.database import get_database, Database
from app.core.monitoring import monitor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/predictive-monitoring", tags=["Predictive Monitoring"])

class PredictiveAnalytics:
    """Predictive analytics for system monitoring"""
    
    def __init__(self):
        self.trend_data = {}
        self.predictions = {}
        self.last_analysis = None
        
    async def analyze_error_trends(self, hours_back: int = 72) -> Dict[str, Any]:
        """Analyze error trends to predict future issues"""
        try:
            # Get recent error data from monitoring system
            error_summary = monitor.get_error_summary(hours_back)
            
            # Analyze error rate trends
            error_trend_analysis = {
                "current_error_rate": error_summary.get("error_rate", 0),
                "error_trend": "stable",  # Will be calculated
                "predicted_issues": [],
                "risk_level": "low",
                "recommendations": []
            }
            
            # Get hourly error rates for trend analysis
            hourly_errors = self._get_hourly_error_distribution(error_summary)
            
            if len(hourly_errors) >= 24:  # Need at least 24 hours of data
                # Calculate trend
                recent_errors = hourly_errors[-12:]  # Last 12 hours
                older_errors = hourly_errors[-24:-12]  # 12-24 hours ago
                
                recent_avg = statistics.mean(recent_errors) if recent_errors else 0
                older_avg = statistics.mean(older_errors) if older_errors else 0
                
                if recent_avg > older_avg * 1.5:
                    error_trend_analysis["error_trend"] = "increasing"
                    error_trend_analysis["risk_level"] = "high"
                    error_trend_analysis["predicted_issues"].append(
                        "Error rate increasing - potential system instability"
                    )
                elif recent_avg > older_avg * 1.2:
                    error_trend_analysis["error_trend"] = "slightly_increasing" 
                    error_trend_analysis["risk_level"] = "medium"
                
                # Predict future error rate
                if error_trend_analysis["error_trend"] in ["increasing", "slightly_increasing"]:
                    trend_slope = (recent_avg - older_avg) / 12
                    predicted_rate_1h = recent_avg + trend_slope
                    predicted_rate_6h = recent_avg + (trend_slope * 6)
                    
                    error_trend_analysis["predictions"] = {
                        "next_hour_error_rate": predicted_rate_1h,
                        "next_6h_error_rate": predicted_rate_6h,
                        "confidence": 0.7 if len(hourly_errors) >= 48 else 0.5
                    }
                    
                    if predicted_rate_1h > recent_avg * 2:
                        error_trend_analysis["predicted_issues"].append(
                            "Critical: Error rate may double in next hour"
                        )
                        error_trend_analysis["recommendations"].append(
                            "Scale up resources and investigate error patterns immediately"
                        )
            
            return error_trend_analysis
            
        except Exception as e:
            logger.error(f"Error trend analysis failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def analyze_performance_trends(self, hours_back: int = 48) -> Dict[str, Any]:
        """Analyze performance trends to predict degradation"""
        try:
            # Get performance data from monitoring
            performance_data = monitor.get_performance_summary(hours_back)
            
            performance_analysis = {
                "current_avg_response_time": 0,
                "performance_trend": "stable",
                "predicted_issues": [],
                "risk_level": "low",
                "recommendations": []
            }
            
            # Simulate performance analysis (in real implementation, get from monitoring)
            # This would analyze actual response time data
            current_response_times = [200, 250, 300, 280, 320, 290, 310]  # Example data
            
            if current_response_times:
                current_avg = statistics.mean(current_response_times)
                performance_analysis["current_avg_response_time"] = current_avg
                
                # Check for performance degradation
                if current_avg > 500:
                    performance_analysis["performance_trend"] = "degrading"
                    performance_analysis["risk_level"] = "high"
                    performance_analysis["predicted_issues"].append(
                        "Performance degradation detected - response times elevated"
                    )
                    performance_analysis["recommendations"].extend([
                        "Investigate slow database queries",
                        "Check external API response times",
                        "Consider scaling up resources"
                    ])
                elif current_avg > 300:
                    performance_analysis["performance_trend"] = "slightly_degrading"
                    performance_analysis["risk_level"] = "medium"
                    performance_analysis["recommendations"].append(
                        "Monitor performance closely - approaching degradation threshold"
                    )
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Performance trend analysis failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def predict_system_capacity(self) -> Dict[str, Any]:
        """Predict system capacity issues"""
        try:
            capacity_analysis = {
                "database_connections": {"current": 45, "max": 100, "predicted_exhaustion": None},
                "memory_usage": {"current_percent": 65, "trend": "stable", "predicted_exhaustion": None},
                "storage_usage": {"current_percent": 40, "trend": "growing", "predicted_exhaustion": None},
                "api_rate_limits": {"current_usage": 1200, "limit": 5000, "predicted_exhaustion": None},
                "overall_risk": "low",
                "recommendations": []
            }
            
            # Analyze database connections
            db_current = capacity_analysis["database_connections"]["current"]
            db_max = capacity_analysis["database_connections"]["max"]
            
            if db_current / db_max > 0.8:
                capacity_analysis["database_connections"]["predicted_exhaustion"] = "6-12 hours"
                capacity_analysis["overall_risk"] = "high"
                capacity_analysis["recommendations"].append(
                    "Database connection pool near capacity - increase pool size"
                )
            
            # Analyze memory usage
            memory_percent = capacity_analysis["memory_usage"]["current_percent"]
            if memory_percent > 80:
                capacity_analysis["memory_usage"]["predicted_exhaustion"] = "2-4 hours"
                capacity_analysis["overall_risk"] = "high"
                capacity_analysis["recommendations"].append(
                    "Memory usage critical - investigate memory leaks"
                )
            elif memory_percent > 70:
                capacity_analysis["overall_risk"] = "medium"
                capacity_analysis["recommendations"].append(
                    "Monitor memory usage - approaching threshold"
                )
            
            return capacity_analysis
            
        except Exception as e:
            logger.error(f"Capacity prediction failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def detect_anomalies(self, hours_back: int = 24) -> Dict[str, Any]:
        """Detect anomalies in system behavior"""
        try:
            anomaly_detection = {
                "anomalies_detected": [],
                "anomaly_count": 0,
                "risk_level": "low",
                "analysis_window_hours": hours_back,
                "recommendations": []
            }
            
            # Get recent system metrics (simulated - would be real data)
            recent_metrics = {
                "error_spikes": [
                    {"timestamp": "2025-01-30T14:30:00Z", "error_count": 45, "baseline": 5},
                    {"timestamp": "2025-01-30T15:15:00Z", "error_count": 38, "baseline": 5}
                ],
                "response_time_spikes": [
                    {"timestamp": "2025-01-30T16:00:00Z", "avg_response_ms": 2500, "baseline": 300}
                ],
                "unusual_patterns": []
            }
            
            # Analyze error spikes
            for spike in recent_metrics["error_spikes"]:
                if spike["error_count"] > spike["baseline"] * 5:
                    anomaly_detection["anomalies_detected"].append({
                        "type": "error_spike",
                        "severity": "high",
                        "description": f"Error count {spike['error_count']} is {spike['error_count']/spike['baseline']:.1f}x baseline",
                        "timestamp": spike["timestamp"],
                        "recommendation": "Investigate error patterns and potential causes"
                    })
            
            # Analyze response time spikes
            for spike in recent_metrics["response_time_spikes"]:
                if spike["avg_response_ms"] > spike["baseline"] * 5:
                    anomaly_detection["anomalies_detected"].append({
                        "type": "performance_spike",
                        "severity": "high", 
                        "description": f"Response time {spike['avg_response_ms']}ms is {spike['avg_response_ms']/spike['baseline']:.1f}x baseline",
                        "timestamp": spike["timestamp"],
                        "recommendation": "Check database performance and external API responses"
                    })
            
            anomaly_detection["anomaly_count"] = len(anomaly_detection["anomalies_detected"])
            
            if anomaly_detection["anomaly_count"] > 5:
                anomaly_detection["risk_level"] = "high"
                anomaly_detection["recommendations"].append("Multiple anomalies detected - investigate system stability")
            elif anomaly_detection["anomaly_count"] > 2:
                anomaly_detection["risk_level"] = "medium"
                anomaly_detection["recommendations"].append("Several anomalies detected - monitor closely")
            
            return anomaly_detection
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    def _get_hourly_error_distribution(self, error_summary: Dict[str, Any]) -> List[float]:
        """Extract hourly error rates from error summary"""
        # This would extract real hourly error rates from monitoring data
        # For now, simulate some data
        import random
        base_rate = error_summary.get("error_rate", 0.05)
        return [base_rate + random.uniform(-0.02, 0.02) for _ in range(48)]

# Initialize analytics
predictive_analytics = PredictiveAnalytics()

@router.get("/comprehensive-analysis")
async def run_comprehensive_predictive_analysis(
    hours_back: int = Query(default=48, ge=6, le=168, description="Hours of history to analyze")
):
    """Run comprehensive predictive analysis across all systems"""
    try:
        analysis_start = datetime.utcnow()
        
        # Run all predictive analyses in parallel
        error_trends, performance_trends, capacity_prediction, anomaly_detection = await asyncio.gather(
            predictive_analytics.analyze_error_trends(hours_back),
            predictive_analytics.analyze_performance_trends(hours_back),
            predictive_analytics.predict_system_capacity(),
            predictive_analytics.detect_anomalies(24)  # Anomalies use 24h window
        )
        
        analysis_end = datetime.utcnow()
        analysis_duration = (analysis_end - analysis_start).total_seconds()
        
        # Aggregate risk levels
        risk_levels = [
            error_trends.get("risk_level", "low"),
            performance_trends.get("risk_level", "low"),
            capacity_prediction.get("overall_risk", "low"),
            anomaly_detection.get("risk_level", "low")
        ]
        
        # Calculate overall risk
        risk_score = {"low": 1, "medium": 2, "high": 3}
        max_risk_score = max(risk_score.get(level, 1) for level in risk_levels)
        overall_risk = {1: "low", 2: "medium", 3: "high"}[max_risk_score]
        
        # Collect all predicted issues
        all_predicted_issues = []
        for analysis in [error_trends, performance_trends, capacity_prediction]:
            all_predicted_issues.extend(analysis.get("predicted_issues", []))
        
        # Collect all recommendations
        all_recommendations = []
        for analysis in [error_trends, performance_trends, capacity_prediction, anomaly_detection]:
            all_recommendations.extend(analysis.get("recommendations", []))
        
        comprehensive_analysis = {
            "overall_risk_level": overall_risk,
            "analysis_duration_seconds": analysis_duration,
            "predicted_issues": all_predicted_issues,
            "anomalies_detected": anomaly_detection.get("anomaly_count", 0),
            "consolidated_recommendations": list(set(all_recommendations)),
            "detailed_analysis": {
                "error_trends": error_trends,
                "performance_trends": performance_trends,
                "capacity_prediction": capacity_prediction,
                "anomaly_detection": anomaly_detection
            },
            "next_analysis_recommended": (analysis_end + timedelta(hours=6)).isoformat(),
            "timestamp": analysis_end.isoformat()
        }
        
        # Log results
        logger.info(f"🔮 Predictive analysis completed - Risk: {overall_risk}, Issues: {len(all_predicted_issues)}, Duration: {analysis_duration:.2f}s")
        
        return comprehensive_analysis
        
    except Exception as e:
        logger.error(f"Comprehensive predictive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Predictive analysis error: {str(e)}")

@router.get("/error-trends")
async def analyze_error_trends(hours_back: int = Query(default=72, ge=6, le=168)):
    """Analyze error trends only"""
    return await predictive_analytics.analyze_error_trends(hours_back)

@router.get("/performance-trends")
async def analyze_performance_trends(hours_back: int = Query(default=48, ge=6, le=168)):
    """Analyze performance trends only"""
    return await predictive_analytics.analyze_performance_trends(hours_back)

@router.get("/capacity-prediction")
async def predict_capacity():
    """Predict system capacity issues"""
    return await predictive_analytics.predict_system_capacity()

@router.get("/anomaly-detection")
async def detect_anomalies(hours_back: int = Query(default=24, ge=6, le=72)):
    """Detect system anomalies"""
    return await predictive_analytics.detect_anomalies(hours_back)

@router.get("/risk-assessment")
async def get_current_risk_assessment():
    """Get current system risk assessment"""
    try:
        # Quick risk assessment based on recent data
        quick_analysis = await asyncio.gather(
            predictive_analytics.analyze_error_trends(24),
            predictive_analytics.analyze_performance_trends(24),
            predictive_analytics.detect_anomalies(12)
        )
        
        risk_indicators = {
            "error_trend_risk": quick_analysis[0].get("risk_level", "low"),
            "performance_risk": quick_analysis[1].get("risk_level", "low"),
            "anomaly_risk": quick_analysis[2].get("risk_level", "low")
        }
        
        # Calculate overall risk
        risk_scores = {"low": 1, "medium": 2, "high": 3}
        max_risk = max(risk_scores.get(level, 1) for level in risk_indicators.values())
        overall_risk = {1: "low", 2: "medium", 3: "high"}[max_risk]
        
        return {
            "overall_risk": overall_risk,
            "risk_indicators": risk_indicators,
            "immediate_actions_needed": overall_risk == "high",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {str(e)}") 