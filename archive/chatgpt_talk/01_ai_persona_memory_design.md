# ai_persona_memory_design.md

This document focuses on implementing memory architecture for AI personas in a journaling and emotional organization app. The intent is to enable long-term, context-aware interactions and improve persona consistency across sessions.

## context
- App uses Supabase, Railway, Vercel, OpenAI, and is built via Cursor.
- User interactions are structured via journaling entries with delayed AI responses.
- Personas: Pulse, Spark, Anchor, Sage — each with distinct tone + purpose.

## memory_model

### memory_persistence_schema
```sql
CREATE TABLE persona_state (
  user_id TEXT,
  persona TEXT,
  known_topics TEXT[],
  active_goals TEXT[],
  last_updated TIMESTAMP
);

CREATE TABLE insight_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  journal_id UUID,
  persona TEXT,
  tags TEXT[],
  ai_summary TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### purpose
- Store active user themes and goals
- Let AI recall emotional history and provide intelligent follow-up
- Improve personalization over time

## memory_usage_in_prompts
```yaml
system: |
  You are {{persona}}, an AI with memory of the user's recent emotional states and topics.
  Use that memory to provide continuity, ask better questions, and guide future insights.

user: |
  Current entry: {{journal_entry}}
  Memory snapshot: {{prior_ai_notes}}, {{known_topics}}, {{active_goals}}
```

## memory_enrichment_logic
- Claude should extract emotional tags and goals from journal entries
- Write logic to keep only recent or most frequent items
- Can rotate memory snapshot by persona (Echo tracks themes, Spark tracks tasks)
