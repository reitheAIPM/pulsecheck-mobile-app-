#!/usr/bin/env python3
"""
PulseCheck Phase 2 End-to-End Testing Script
Tests the enhanced AI capabilities including structured responses, multi-persona processing, and streaming.

Usage: python phase2_end_to_end_test.py
"""

import asyncio
import json
import time
import websockets
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2E2ETester:
    def __init__(self):
        self.base_url = "https://pulsecheck-mobile-app-production.up.railway.app"
        self.ws_url = "wss://pulsecheck-mobile-app-production.up.railway.app"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PulseCheck-Phase2-E2E-Test/1.0'
        }
        self.test_results = []
        self.test_data = {}
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log a test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            logger.info(f"   Details: {details}")
    
    def test_system_health(self) -> bool:
        """Test overall system health"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                details = f"Status: {health_data.get('status', 'unknown')}"
                self.log_test_result("System Health Check", True, details, duration)
                return True
            else:
                self.log_test_result("System Health Check", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("System Health Check", False, f"Error: {str(e)}", duration)
            return False
    
    def test_structured_ai_endpoint(self, entry_id: str) -> bool:
        """Test structured AI response endpoint"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response"
            params = {"structured": "true"}
            
            response = requests.post(url, headers=self.headers, params=params, timeout=60)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate structured response format
                required_fields = ['insight', 'persona_used', 'generated_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    details = f"Missing fields: {missing_fields}"
                    self.log_test_result("Structured AI Response", False, details, duration)
                    return False
                
                # Check for metadata
                has_metadata = 'metadata' in data
                metadata_info = f"Metadata: {'present' if has_metadata else 'missing'}"
                
                details = f"Persona: {data['persona_used']}, Response length: {len(data['insight'])}, {metadata_info}"
                self.log_test_result("Structured AI Response", True, details, duration)
                return True
            else:
                self.log_test_result("Structured AI Response", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Structured AI Response", False, f"Error: {str(e)}", duration)
            return False
    
    def test_multi_persona_endpoint(self, entry_id: str) -> bool:
        """Test multi-persona response endpoint"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response"
            params = {"multi_persona": "true"}
            
            response = requests.post(url, headers=self.headers, params=params, timeout=120)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate multi-persona response
                persona_used = data.get('persona_used', 'unknown')
                response_length = len(data.get('insight', ''))
                
                # Check for enhanced metadata indicating multi-persona processing
                metadata = data.get('metadata', {})
                multi_persona_flag = metadata.get('multi_persona_response', False)
                
                details = f"Persona: {persona_used}, Response length: {response_length}, Multi-persona: {multi_persona_flag}"
                
                # Performance check: should be significantly faster than sequential processing
                if duration < 15:  # Should be under 15 seconds (vs 60s sequential)
                    performance_note = f"Performance: {duration:.1f}s (Good)"
                else:
                    performance_note = f"Performance: {duration:.1f}s (Slow)"
                
                details += f", {performance_note}"
                self.log_test_result("Multi-Persona Response", True, details, duration)
                return True
            else:
                self.log_test_result("Multi-Persona Response", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Multi-Persona Response", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_streaming_endpoint(self, entry_id: str, auth_token: str) -> bool:
        """Test WebSocket streaming endpoint"""
        start_time = time.time()
        try:
            ws_url = f"{self.ws_url}/api/v1/journal/entries/{entry_id}/stream"
            params = f"persona=auto&token={auth_token}"
            full_url = f"{ws_url}?{params}"
            
            messages_received = []
            connection_success = False
            content_received = False
            typing_indicator_seen = False
            completion_received = False
            
            async with websockets.connect(full_url) as websocket:
                connection_success = True
                
                # Listen for messages with timeout
                timeout_time = time.time() + 30  # 30 second timeout
                
                while time.time() < timeout_time:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        messages_received.append(data)
                        
                        message_type = data.get('type')
                        if message_type == 'typing':
                            typing_indicator_seen = True
                        elif message_type == 'content':
                            content_received = True
                        elif message_type == 'complete':
                            completion_received = True
                            break
                        elif message_type == 'error':
                            raise Exception(f"Streaming error: {data.get('message', 'Unknown error')}")
                            
                    except asyncio.TimeoutError:
                        break
                
                duration = time.time() - start_time
                
                # Evaluate streaming test results
                if content_received and completion_received:
                    details = f"Messages: {len(messages_received)}, Typing: {typing_indicator_seen}, Content: {content_received}, Complete: {completion_received}"
                    self.log_test_result("Streaming Response", True, details, duration)
                    return True
                else:
                    details = f"Incomplete: Typing: {typing_indicator_seen}, Content: {content_received}, Complete: {completion_received}"
                    self.log_test_result("Streaming Response", False, details, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Streaming Response", False, f"Error: {str(e)}", duration)
            return False
    
    def test_performance_comparison(self, entry_id: str) -> bool:
        """Test performance improvements by comparing different response types"""
        start_time = time.time()
        try:
            # Test basic response time
            basic_start = time.time()
            basic_response = requests.post(
                f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response",
                headers=self.headers,
                timeout=60
            )
            basic_duration = time.time() - basic_start
            
            # Test structured response time
            structured_start = time.time()
            structured_response = requests.post(
                f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response",
                headers=self.headers,
                params={"structured": "true"},
                timeout=60
            )
            structured_duration = time.time() - structured_start
            
            # Test multi-persona response time
            multi_start = time.time()
            multi_response = requests.post(
                f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response",
                headers=self.headers,
                params={"multi_persona": "true"},
                timeout=120
            )
            multi_duration = time.time() - multi_start
            
            total_duration = time.time() - start_time
            
            # Validate performance expectations
            performance_good = True
            performance_details = []
            
            # Basic response should be under 5 seconds (83% improvement target)
            if basic_duration <= 5:
                performance_details.append(f"Basic: {basic_duration:.1f}s (Good)")
            else:
                performance_details.append(f"Basic: {basic_duration:.1f}s (Slow)")
                performance_good = False
            
            # Structured response should be similar to basic
            if structured_duration <= 6:
                performance_details.append(f"Structured: {structured_duration:.1f}s (Good)")
            else:
                performance_details.append(f"Structured: {structured_duration:.1f}s (Slow)")
                performance_good = False
            
            # Multi-persona should be under 10 seconds (92% improvement target)
            if multi_duration <= 10:
                performance_details.append(f"Multi-persona: {multi_duration:.1f}s (Good)")
            else:
                performance_details.append(f"Multi-persona: {multi_duration:.1f}s (Slow)")
                performance_good = False
            
            details = ", ".join(performance_details)
            self.log_test_result("Performance Comparison", performance_good, details, total_duration)
            return performance_good
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Performance Comparison", False, f"Error: {str(e)}", duration)
            return False
    
    def test_api_compatibility(self, entry_id: str) -> bool:
        """Test backward compatibility of enhanced endpoints"""
        start_time = time.time()
        try:
            # Test that existing API calls still work
            legacy_response = requests.post(
                f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response",
                headers=self.headers,
                timeout=60
            )
            
            # Test enhanced API calls
            enhanced_response = requests.post(
                f"{self.base_url}/api/v1/journal/entries/{entry_id}/adaptive-response",
                headers=self.headers,
                params={"structured": "true", "multi_persona": "true"},
                timeout=120
            )
            
            duration = time.time() - start_time
            
            if legacy_response.status_code == 200 and enhanced_response.status_code == 200:
                legacy_data = legacy_response.json()
                enhanced_data = enhanced_response.json()
                
                # Both should have basic required fields
                required_fields = ['insight', 'persona_used', 'generated_at']
                legacy_valid = all(field in legacy_data for field in required_fields)
                enhanced_valid = all(field in enhanced_data for field in required_fields)
                
                if legacy_valid and enhanced_valid:
                    details = f"Legacy format: valid, Enhanced format: valid"
                    self.log_test_result("API Compatibility", True, details, duration)
                    return True
                else:
                    details = f"Legacy format: {legacy_valid}, Enhanced format: {enhanced_valid}"
                    self.log_test_result("API Compatibility", False, details, duration)
                    return False
            else:
                details = f"Legacy: HTTP {legacy_response.status_code}, Enhanced: HTTP {enhanced_response.status_code}"
                self.log_test_result("API Compatibility", False, details, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("API Compatibility", False, f"Error: {str(e)}", duration)
            return False
    
    def create_test_entry(self) -> Optional[str]:
        """Create a test journal entry for testing"""
        start_time = time.time()
        try:
            test_entry = {
                "content": "Phase 2 testing entry: I'm feeling excited about the new AI capabilities we've implemented. The structured responses, multi-persona processing, and streaming features seem very promising. I'm curious to see how they perform in practice and whether users will find them valuable.",
                "mood_level": 7,
                "energy_level": 8,
                "stress_level": 3,
                "gratitude_note": "Grateful for the progress we've made",
                "goals": ["Test new AI features", "Validate performance improvements"],
                "challenges": ["Ensuring system reliability", "Optimizing user experience"],
                "tags": ["development", "testing", "ai", "phase2"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/journal/entries",
                headers=self.headers,
                json=test_entry,
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                entry_data = response.json()
                entry_id = entry_data.get('id')
                
                self.log_test_result("Test Entry Creation", True, f"Entry ID: {entry_id}", duration)
                return entry_id
            else:
                self.log_test_result("Test Entry Creation", False, f"HTTP {response.status_code}", duration)
                return None
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Test Entry Creation", False, f"Error: {str(e)}", duration)
            return None
    
    def cleanup_test_entry(self, entry_id: str) -> bool:
        """Clean up test entry after testing"""
        start_time = time.time()
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/journal/entries/{entry_id}",
                headers=self.headers,
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code in [200, 204]:
                self.log_test_result("Test Entry Cleanup", True, f"Entry {entry_id} deleted", duration)
                return True
            else:
                self.log_test_result("Test Entry Cleanup", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Test Entry Cleanup", False, f"Error: {str(e)}", duration)
            return False
    
    async def run_all_tests(self):
        """Run all Phase 2 end-to-end tests"""
        print("🚀 Starting PulseCheck Phase 2 End-to-End Testing")
        print("=" * 60)
        
        # Test system health first
        if not self.test_system_health():
            print("❌ System health check failed. Stopping tests.")
            return
        
        # Create test entry
        entry_id = self.create_test_entry()
        if not entry_id:
            print("❌ Failed to create test entry. Stopping tests.")
            return
        
        # Wait for entry to be processed
        print("⏳ Waiting for entry to be processed...")
        await asyncio.sleep(2)
        
        try:
            # Run all Phase 2 tests
            tests = [
                ("Structured AI Response", lambda: self.test_structured_ai_endpoint(entry_id)),
                ("Multi-Persona Response", lambda: self.test_multi_persona_endpoint(entry_id)),
                ("Performance Comparison", lambda: self.test_performance_comparison(entry_id)),
                ("API Compatibility", lambda: self.test_api_compatibility(entry_id)),
            ]
            
            for test_name, test_func in tests:
                print(f"\n🔍 Running {test_name}...")
                test_func()
            
            # Run streaming test (requires async)
            print(f"\n🔍 Running Streaming Response...")
            # Note: This requires a valid auth token - in production test, you'd get this from auth system
            fake_token = "test_token_for_streaming"  # This will likely fail without real auth
            await self.test_streaming_endpoint(entry_id, fake_token)
            
        finally:
            # Cleanup
            print(f"\n🧹 Cleaning up test data...")
            self.cleanup_test_entry(entry_id)
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate and display test summary"""
        print("\n" + "=" * 60)
        print("📊 Phase 2 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        # Save detailed results
        with open('phase2_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: phase2_test_results.json")
        
        # Overall assessment
        if passed_tests == total_tests:
            print("\n🎉 All Phase 2 tests passed! System is ready for production.")
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️  Most tests passed. Review failures before production deployment.")
        else:
            print("\n🚨 Multiple test failures detected. System needs attention before production.")

async def main():
    """Main function to run the Phase 2 end-to-end tests"""
    tester = Phase2E2ETester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 