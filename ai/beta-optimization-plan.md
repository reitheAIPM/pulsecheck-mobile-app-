# PulseCheck Beta Optimization Implementation Plan

## 🎯 **Implementation Overview**

**Goal**: Prepare for 10-20 user beta with cost-conscious AI, user tiers, and comprehensive analytics
**Timeline**: 3-5 days implementation
**Focus**: Scalable architecture, cost control, quality preservation

---

## 🧠 **Token-Conscious Journaling Logic**

### **Strategy 1: Intelligent Context Summarization**

#### **Weekly Summary Generation**
```python
class JournalSummarizer:
    def create_weekly_summary(self, entries: List[JournalEntry]) -> WeeklySummary:
        """Generate AI-powered weekly summary from journal entries"""
        
        # Aggregate mood/stress/energy patterns
        patterns = self._extract_patterns(entries)
        
        # Generate concise summary (50-100 tokens max)
        summary_prompt = f"""
        Summarize this week's wellness patterns in 2-3 bullet points:
        - Avg mood: {patterns.avg_mood}/10
        - Key themes: {patterns.top_themes}
        - Stress triggers: {patterns.stress_triggers}
        - Progress notes: {patterns.positive_changes}
        """
        
        return WeeklySummary(
            week_start=patterns.week_start,
            mood_trend=patterns.mood_trend,
            key_insights=ai_summary,
            token_count=50  # Massive reduction from 1000+ raw tokens
        )
```

#### **Context Layering Strategy**
```python
class ContextBuilder:
    def build_ai_context(self, user: User, current_entry: JournalEntry) -> AIContext:
        if user.is_premium:
            return self._build_premium_context(user, current_entry)
        else:
            return self._build_free_context(user, current_entry)
    
    def _build_free_context(self, user: User, current_entry: JournalEntry) -> AIContext:
        """Free tier: Last 3 entries + current week summary"""
        recent_entries = self.get_recent_entries(user.id, limit=3)
        current_week_summary = self.get_current_week_summary(user.id)
        
        return AIContext(
            recent_entries=recent_entries,  # ~300 tokens
            week_summary=current_week_summary,  # ~50 tokens
            current_entry=current_entry,  # ~100 tokens
            total_tokens=450  # vs 1500+ without optimization
        )
    
    def _build_premium_context(self, user: User, current_entry: JournalEntry) -> AIContext:
        """Premium tier: Last 7 entries + 4 weeks of summaries"""
        recent_entries = self.get_recent_entries(user.id, limit=7)
        monthly_summaries = self.get_monthly_summaries(user.id, limit=4)
        
        return AIContext(
            recent_entries=recent_entries,  # ~700 tokens
            monthly_summaries=monthly_summaries,  # ~200 tokens
            current_entry=current_entry,  # ~100 tokens
            total_tokens=1000  # Rich context for premium users
        )
```

### **Strategy 2: Smart Token Budgeting**

#### **Dynamic Context Allocation**
```python
class TokenBudgetManager:
    FREE_TIER_BUDGET = 500  # tokens per interaction
    PREMIUM_TIER_BUDGET = 1200  # tokens per interaction
    
    def optimize_context(self, user: User, available_entries: List[JournalEntry]) -> OptimizedContext:
        budget = self.PREMIUM_TIER_BUDGET if user.is_premium else self.FREE_TIER_BUDGET
        
        # Priority order: Current entry > Recent entries > Summaries
        context = OptimizedContext()
        remaining_budget = budget
        
        # Always include current entry
        context.add_current_entry(available_entries[0])
        remaining_budget -= context.current_entry_tokens
        
        # Add recent entries until budget exhausted
        for entry in available_entries[1:]:
            entry_cost = self._estimate_tokens(entry)
            if remaining_budget >= entry_cost:
                context.add_entry(entry)
                remaining_budget -= entry_cost
            else:
                break
        
        # Fill remaining budget with summaries if available
        if remaining_budget > 100:
            summaries = self.get_relevant_summaries(user.id, token_limit=remaining_budget)
            context.add_summaries(summaries)
        
        return context
```

---

## 👥 **User Tier Implementation**

### **Database Schema Updates**

#### **User Tiers Table**
```sql
-- Add to existing users table
ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN tier_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN daily_ai_usage INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN daily_usage_reset_at DATE DEFAULT CURRENT_DATE;

-- User tier limits table
CREATE TABLE user_tier_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier_name VARCHAR(50) NOT NULL,
    daily_ai_limit INTEGER NOT NULL,
    context_depth INTEGER NOT NULL, -- number of recent entries
    summary_access BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO user_tier_limits (tier_name, daily_ai_limit, context_depth, summary_access) VALUES
('free', 5, 3, FALSE),
('premium', 50, 7, TRUE),
('beta', 20, 5, TRUE); -- Special beta tier
```

#### **Journal Summaries Table**
```sql
CREATE TABLE journal_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    summary_type VARCHAR(20) NOT NULL, -- 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    mood_trend DECIMAL(3,1), -- avg mood for period
    energy_trend DECIMAL(3,1),
    stress_trend DECIMAL(3,1),
    key_insights TEXT NOT NULL, -- AI-generated summary
    top_themes TEXT[], -- array of main themes
    token_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, summary_type, period_start)
);
```

### **Tier Logic Implementation**

#### **Usage Tracking Service**
```python
class UsageTracker:
    def __init__(self, db: Database):
        self.db = db
    
    async def check_daily_limit(self, user_id: str) -> UsageStatus:
        """Check if user has exceeded daily AI usage limit"""
        user = await self.db.get_user_with_tier(user_id)
        
        # Reset daily counter if new day
        if user.daily_usage_reset_at < date.today():
            await self.reset_daily_usage(user_id)
            user.daily_ai_usage = 0
        
        tier_limits = await self.db.get_tier_limits(user.tier)
        
        return UsageStatus(
            can_use_ai=user.daily_ai_usage < tier_limits.daily_ai_limit,
            remaining_uses=tier_limits.daily_ai_limit - user.daily_ai_usage,
            tier=user.tier,
            resets_at=user.daily_usage_reset_at + timedelta(days=1)
        )
    
    async def increment_usage(self, user_id: str, tokens_used: int):
        """Track AI usage and token consumption"""
        await self.db.execute("""
            UPDATE users 
            SET daily_ai_usage = daily_ai_usage + 1
            WHERE id = $1
        """, user_id)
        
        # Log detailed usage for analytics
        await self.db.execute("""
            INSERT INTO ai_usage_logs (user_id, tokens_used, timestamp)
            VALUES ($1, $2, NOW())
        """, user_id, tokens_used)
```

---

## 📊 **Token Usage Tracking & Analytics**

### **Comprehensive Logging System**

#### **AI Usage Logs Table**
```sql
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    journal_entry_id UUID REFERENCES journal_entries(id),
    prompt_tokens INTEGER NOT NULL,
    response_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    model_used VARCHAR(50) NOT NULL,
    response_time_ms INTEGER,
    confidence_score DECIMAL(3,2),
    cost_usd DECIMAL(8,6), -- track actual cost
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_ai_usage_user_date ON ai_usage_logs(user_id, DATE(timestamp));
CREATE INDEX idx_ai_usage_date ON ai_usage_logs(DATE(timestamp));
```

#### **Real-time Cost Tracking**
```python
class CostTracker:
    MODEL_COSTS = {
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},  # per 1K tokens
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
        'gpt-4o': {'input': 0.0025, 'output': 0.01}
    }
    
    def calculate_cost(self, model: str, prompt_tokens: int, response_tokens: int) -> float:
        """Calculate exact cost for AI interaction"""
        costs = self.MODEL_COSTS[model]
        
        input_cost = (prompt_tokens / 1000) * costs['input']
        output_cost = (response_tokens / 1000) * costs['output']
        
        return round(input_cost + output_cost, 6)
    
    async def log_usage(self, user_id: str, interaction: AIInteraction):
        """Log usage with cost tracking"""
        cost = self.calculate_cost(
            interaction.model,
            interaction.prompt_tokens,
            interaction.response_tokens
        )
        
        await self.db.execute("""
            INSERT INTO ai_usage_logs 
            (user_id, journal_entry_id, prompt_tokens, response_tokens, 
             total_tokens, model_used, response_time_ms, confidence_score, cost_usd)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, user_id, interaction.entry_id, interaction.prompt_tokens,
             interaction.response_tokens, interaction.total_tokens,
             interaction.model, interaction.response_time_ms,
             interaction.confidence_score, cost)
```

---

## 👍 **Beta Feedback System**

### **Feedback Collection Infrastructure**

#### **AI Feedback Table**
```sql
CREATE TABLE ai_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    journal_entry_id UUID REFERENCES journal_entries(id),
    ai_response_id UUID, -- reference to the specific AI response
    feedback_type VARCHAR(20) NOT NULL, -- 'thumbs_up', 'thumbs_down', 'report'
    feedback_text TEXT, -- optional detailed feedback
    prompt_content TEXT NOT NULL, -- store prompt for analysis
    response_content TEXT NOT NULL, -- store response for analysis
    confidence_score DECIMAL(3,2),
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics indexes
CREATE INDEX idx_feedback_type_date ON ai_feedback(feedback_type, DATE(created_at));
CREATE INDEX idx_feedback_user ON ai_feedback(user_id);
```

#### **Feedback Collection Component**
```typescript
// React Native feedback component
interface FeedbackProps {
  aiResponse: PulseResponse;
  onFeedback: (feedback: FeedbackData) => void;
}

export const AIFeedbackComponent: React.FC<FeedbackProps> = ({ aiResponse, onFeedback }) => {
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  
  const handleFeedback = async (type: 'thumbs_up' | 'thumbs_down', text?: string) => {
    const feedback = {
      response_id: aiResponse.id,
      feedback_type: type,
      feedback_text: text,
      timestamp: new Date().toISOString()
    };
    
    await onFeedback(feedback);
    setFeedbackGiven(true);
    
    // Show thank you message
    showToast('Thank you for your feedback! This helps improve Pulse.');
  };
  
  if (feedbackGiven) {
    return <Text style={styles.thankYou}>✅ Feedback received</Text>;
  }
  
  return (
    <View style={styles.feedbackContainer}>
      <Text style={styles.feedbackPrompt}>Was this response helpful?</Text>
      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={styles.thumbsButton}
          onPress={() => handleFeedback('thumbs_up')}
        >
          <Text style={styles.thumbsUp}>👍</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.thumbsButton}
          onPress={() => handleFeedback('thumbs_down')}
        >
          <Text style={styles.thumbsDown}>👎</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};
```

---

## 🎯 **Implementation Priority & Timeline**

### **Phase 1: Core Infrastructure (Days 1-2)**
1. **Database Schema Updates**
2. **Token-Conscious Context Builder** 
3. **Usage Tracking Service**
4. **Rate Limiting Middleware**

### **Phase 2: Analytics & Feedback (Day 3)**
1. **AI Feedback Collection System**
2. **Admin Analytics Endpoints**
3. **Cost Tracking Implementation**

### **Phase 3: Frontend Integration (Day 4)**
1. **Feedback UI Components**
2. **Rate Limit Handling**
3. **Usage Indicators**

### **Phase 4: Testing & Launch (Day 5)**
1. **Load Testing Script**
2. **Beta Simulation**
3. **Performance Optimization**

---

## 💡 **Expected Outcomes**

### **Cost Reduction**
- **Free tier**: 60% cost reduction (500→200 tokens avg)
- **Premium tier**: Smart context, better value
- **Overall**: 40-60% cost savings across all users

### **Quality Preservation**
- **Recent context**: Maintains emotional continuity
- **Summarized history**: Preserves long-term patterns
- **Tier differentiation**: Clear value proposition

### **Beta Success Metrics**
- **Cost per user**: <$0.02/month (free), <$0.10/month (premium)
- **User satisfaction**: >70% positive feedback
- **Engagement**: 3+ interactions/week average
- **Retention**: >60% day-7 retention

This implementation provides a robust foundation for beta launch while maintaining cost-efficiency and preparing for sustainable growth. 