# 🛡️ **AI Content Safety Filter Best Practices**
**Created**: January 30, 2025  
**Purpose**: Prevent content safety filter issues that can cause AI response failures  
**Status**: Active Guidelines

---

## 🚨 **Critical Lesson: The "You're" Incident**

### **What Happened:**
On January 30, 2025, our AI system experienced complete response failure due to an overly aggressive content safety filter. The pattern `r"you're"` in the medical advice category was blocking **normal conversational responses**, causing:

- ✅ AI generation working (OpenAI API successful)
- ✅ Persona selection working ("pulse" selected)
- ❌ Content safety filter blocking normal responses
- ❌ Validation errors due to `None` responses
- ⚠️ Users receiving generic fallback responses instead of personalized AI

### **The Problem Pattern:**
```python
# DANGEROUS - Too broad!
"medical_advice": [
    r"you're",  # Blocks "you're doing great", "you're feeling", etc.
    # ...
]
```

### **The Solution:**
```python
# SAFE - Specific and contextual
"medical_advice": [
    r"you're (?:sick|ill|depressed|having|suffering)",
    r"you're experiencing (?:symptoms|medical|health)",
    r"you should (?:take|stop|start) (?:medication|pills|drugs)",
    # ... more specific patterns
]
```

---

## 📋 **Content Safety Filter Design Principles**

### **1. Specificity Over Breadth**
- ❌ **Don't**: Use common words like "you're", "feeling", "take"
- ✅ **Do**: Use specific contextual patterns that target actual harmful content
- ✅ **Example**: `r"take (?:medication|pills|drugs)"` instead of `r"take"`

### **2. Context-Aware Patterns**
- ❌ **Don't**: Block words in isolation
- ✅ **Do**: Use lookahead/lookbehind to ensure proper context
- ✅ **Example**: `r"you're (?:sick|ill)"` instead of `r"sick"`

### **3. False Positive Testing**
- ❌ **Don't**: Deploy patterns without testing normal conversation
- ✅ **Do**: Test every pattern against supportive, conversational content
- ✅ **Example**: Test "Hey there, you're doing great!" before deployment

### **4. Documentation and Justification**
- ❌ **Don't**: Add patterns without clear reasoning
- ✅ **Do**: Document why each pattern exists and what it should catch
- ✅ **Example**: Comments explaining the specific harmful content being prevented

---

## 🧪 **Content Safety Testing Protocol**

### **Pre-Deployment Testing:**
```python
# Test common supportive phrases
test_phrases = [
    "Hey there, you're doing great!",
    "You're feeling overwhelmed, and that's okay",
    "How are you feeling today?",
    "You're not alone in this",
    "I hear you're going through a tough time",
    "You're making progress, even if it doesn't feel like it",
    "Take your time to process this",
    "You are valued and important"
]

for phrase in test_phrases:
    result = test_content_safety(phrase)
    if result.blocked:
        print(f"❌ FALSE POSITIVE: '{phrase}' blocked by pattern: {result.pattern}")
    else:
        print(f"✅ PASSED: '{phrase}'")
```

### **Medical Advice Testing:**
```python
# Test actual medical advice that SHOULD be blocked
medical_advice_phrases = [
    "You should stop taking your medication",
    "You're sick and need to see a doctor immediately",
    "Take these pills to feel better",
    "You have depression and should start antidepressants",
    "Stop your prescribed medication and try this instead"
]

for phrase in medical_advice_phrases:
    result = test_content_safety(phrase)
    if result.blocked:
        print(f"✅ CORRECTLY BLOCKED: '{phrase}' by pattern: {result.pattern}")
    else:
        print(f"❌ SHOULD BE BLOCKED: '{phrase}'")
```

### **PowerShell Testing Script:**
```powershell
# Content Safety Testing Script
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

$supportivePhrases = @(
    "Hey there, you're doing great!",
    "You're feeling overwhelmed, and that's okay",
    "How are you feeling today?",
    "You're not alone in this"
)

$medicalPhrases = @(
    "You should stop taking your medication",
    "Take these pills to feel better",
    "You have depression and need antidepressants"
)

Write-Host "Testing Supportive Phrases (should NOT be blocked):" -ForegroundColor Green
foreach ($phrase in $supportivePhrases) {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/v1/debug/content-safety/test" -Method POST -Body (@{content=$phrase} | ConvertTo-Json) -ContentType "application/json"
    if ($result.blocked) {
        Write-Host "❌ FALSE POSITIVE: $phrase" -ForegroundColor Red
    } else {
        Write-Host "✅ PASSED: $phrase" -ForegroundColor Green
    }
}

Write-Host "`nTesting Medical Advice (should BE blocked):" -ForegroundColor Yellow
foreach ($phrase in $medicalPhrases) {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/v1/debug/content-safety/test" -Method POST -Body (@{content=$phrase} | ConvertTo-Json) -ContentType "application/json"
    if ($result.blocked) {
        Write-Host "✅ CORRECTLY BLOCKED: $phrase" -ForegroundColor Green
    } else {
        Write-Host "❌ SHOULD BE BLOCKED: $phrase" -ForegroundColor Red
    }
}
```

---

## 🎯 **Pattern Design Guidelines**

### **Medical Advice Patterns (Specific):**
```python
"medical_advice": [
    # Specific medication advice
    r"(?:you should|you need to|you must) (?:take|stop|start|increase|decrease) (?:medication|pills|drugs|antidepressants)",
    
    # Diagnostic statements
    r"you (?:have|are suffering from|are experiencing) (?:depression|anxiety|bipolar|ADHD|PTSD)",
    
    # Medical recommendations
    r"you should (?:see a doctor|get diagnosed|be hospitalized|check into)",
    
    # Specific symptom + medical context
    r"you're (?:sick|ill|having symptoms) and (?:should|need to|must)",
    
    # Emergency medical situations
    r"you need (?:immediate medical attention|to call 911|emergency help)"
]
```

### **Harmful Content Patterns (Specific):**
```python
"harmful_content": [
    # Self-harm (specific actions)
    r"(?:you should|you could) (?:hurt yourself|end it all|kill yourself)",
    
    # Worthlessness (extreme statements)
    r"you're (?:completely )?(?:worthless|useless|a failure) and (?:should|will never)",
    
    # Hopelessness (absolute statements)
    r"(?:nothing will|you'll never|there's no) (?:get better|improve|hope|point)"
]
```

### **What NOT to Block:**
```python
# DON'T block these common supportive phrases:
safe_patterns = [
    r"you're (?:doing great|amazing|strong|brave|not alone)",
    r"you're feeling (?:overwhelmed|stressed|anxious) and that's (?:okay|normal|understandable)",
    r"how are you feeling",
    r"you're making progress",
    r"take (?:your time|a break|care of yourself)",
    r"you are (?:valued|important|loved|worthy)"
]
```

---

## 📊 **Monitoring and Metrics**

### **Key Metrics to Track:**
1. **False Positive Rate**: % of supportive content blocked
2. **True Positive Rate**: % of harmful content correctly blocked
3. **Pattern Effectiveness**: Which patterns are most/least effective
4. **User Impact**: Response quality degradation due to blocking

### **Monitoring Dashboard:**
```json
{
  "content_safety_metrics": {
    "false_positive_rate": 0.05,  // Target: <5%
    "true_positive_rate": 0.95,   // Target: >95%
    "blocks_last_24h": 12,
    "most_triggered_patterns": [
      {"pattern": "medical_advice_medication", "triggers": 8, "false_positives": 0},
      {"pattern": "harmful_content_self_harm", "triggers": 3, "false_positives": 0},
      {"pattern": "medical_advice_diagnosis", "triggers": 1, "false_positives": 1}
    ],
    "recommendations": [
      "Review 'medical_advice_diagnosis' pattern - 100% false positive rate"
    ]
  }
}
```

### **Alert Thresholds:**
- 🚨 **Critical**: False positive rate >20%
- ⚠️ **Warning**: False positive rate >10%
- 📊 **Monitor**: Any pattern with >50% false positive rate

---

## 🔄 **Deployment and Maintenance Workflow**

### **Before Deploying New Patterns:**
1. **Design Review**: Ensure patterns are specific and contextual
2. **Test Suite**: Run against supportive phrase test suite
3. **Medical Test**: Verify actual harmful content is blocked
4. **Documentation**: Document pattern purpose and examples
5. **Staged Deployment**: Deploy to test environment first

### **Regular Maintenance:**
- **Weekly**: Review false positive reports and metrics
- **Monthly**: Analyze pattern effectiveness and optimize
- **Quarterly**: Comprehensive review of all safety patterns
- **As Needed**: Immediate fixes for patterns causing >20% false positives

### **Pattern Update Process:**
```python
# 1. Identify problematic pattern
problematic_pattern = r"you're"  # Too broad

# 2. Analyze what it should actually catch
intended_blocks = [
    "you're sick and should see a doctor",
    "you're depressed and need medication"
]

# 3. Design specific replacement
new_pattern = r"you're (?:sick|ill|depressed) and (?:should|need to|must)"

# 4. Test against both harmful and supportive content
test_content_safety_pattern(new_pattern, test_phrases)

# 5. Deploy with monitoring
deploy_pattern_with_monitoring(new_pattern)
```

---

## 🚨 **Emergency Response Protocol**

### **If False Positive Rate >20%:**
1. **Immediate**: Identify problematic pattern(s)
2. **Quick Fix**: Temporarily disable overly broad patterns
3. **Analysis**: Determine root cause and design specific replacement
4. **Test**: Validate new pattern against test suite
5. **Deploy**: Push fix with enhanced monitoring
6. **Monitor**: Track metrics for 24 hours post-deployment

### **Pattern Rollback Procedure:**
```python
# Emergency pattern disable
def emergency_disable_pattern(pattern_name):
    # Log the action
    logger.critical(f"Emergency disabling pattern: {pattern_name}")
    
    # Remove from active patterns
    safety_patterns[category].remove(pattern_name)
    
    # Notify monitoring
    alert_monitoring_system(f"Pattern {pattern_name} emergency disabled")
    
    # Schedule review
    schedule_pattern_review(pattern_name, urgency="high")
```

---

## 📚 **Best Practices Summary**

### **✅ DO:**
- Use specific, contextual patterns
- Test against normal supportive conversation
- Document pattern purpose and examples
- Monitor false positive rates continuously
- Design patterns to catch specific harmful content
- Use lookahead/lookbehind for context
- Regular pattern effectiveness reviews

### **❌ DON'T:**
- Use common conversational words as standalone patterns
- Deploy patterns without testing supportive content
- Create overly broad patterns that catch normal conversation
- Ignore false positive rate metrics
- Add patterns without clear justification
- Block words that appear in helpful, supportive responses

### **🎯 TARGET METRICS:**
- **False Positive Rate**: <5%
- **True Positive Rate**: >95%
- **Response Quality**: Maintain personalized, supportive AI responses
- **User Experience**: No disruption to normal conversation flow

---

## 🔗 **Related Documentation**

- [AI Debugging System](./AI-DEBUGGING-SYSTEM.md)
- [AI System Debugging Report](./detailed-reports/AI-SYSTEM-DEBUGGING-REPORT.md)
- [Content Safety API Documentation](../backend/docs/content-safety-api.md)

---

*Document Created: January 30, 2025*  
*Last Updated: January 30, 2025*  
*Next Review: February 6, 2025 (Weekly)* 