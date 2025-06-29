# prompt_templates_and_supabase_functions.md

This document defines prompt templates used for AI interactions and includes Supabase functions to support journaling summaries, emotion tagging, and memory enrichment.

## prompt_templates

### journaling_response
```yaml
system: |
  You are {{persona_name}}, a helpful and emotionally intelligent companion.
  Reflect gently on the user’s journal entry, referencing recurring themes or goals.

user: |
  Entry: {{latest_journal_entry}}
  Mood: {{mood_summary}}
  Memory: {{known_topics}}, {{active_goals}}, {{prior_ai_notes}}
```

### weekly_summary
```yaml
system: |
  You are {{persona}}, a reflective AI summarizing the user’s week.
  Mention recurring moods, trends, and offer gentle reflection.

user: |
  Entries (7 days): {{journal_snippets}}
  Summary history: {{previous_summaries}}
```

### follow_up_prompt
```yaml
system: |
  You are {{persona}}, following up thoughtfully.
  Reference past entry and offer useful insights or questions.

user: |
  Re: {{entry_snippet}}, Reason: {{follow_up_trigger}}, Context: {{user_mood}}, {{recent_tags}}
```

## supabase_functions

### function_generate_summary
```sql
CREATE FUNCTION function_generate_summary(user_id TEXT)
RETURNS TEXT AS $$
DECLARE
  result TEXT;
BEGIN
  SELECT string_agg(content, '\n') INTO result
  FROM journal_entries
  WHERE user_id = function_generate_summary.user_id
    AND created_at >= NOW() - INTERVAL '7 days';
  RETURN result;
END;
$$ LANGUAGE plpgsql;
```

### function_tag_emotions
```sql
CREATE FUNCTION function_tag_emotions(entry TEXT)
RETURNS TEXT[] AS $$
DECLARE
  tags TEXT[] := ARRAY[]::TEXT[];
BEGIN
  IF entry ILIKE '%anxious%' THEN tags := array_append(tags, 'anxiety'); END IF;
  IF entry ILIKE '%burnout%' THEN tags := array_append(tags, 'burnout'); END IF;
  IF entry ILIKE '%overwhelmed%' THEN tags := array_append(tags, 'overwhelm'); END IF;
  RETURN tags;
END;
$$ LANGUAGE plpgsql;
```

### follow_up_injection
Claude should write logic to queue a follow-up if:
- Repeated theme within 3 days
- No journal entry after high-intensity tag
- Tracked goal mentioned but not marked complete
