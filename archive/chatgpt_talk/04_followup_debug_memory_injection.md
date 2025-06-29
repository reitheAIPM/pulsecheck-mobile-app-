# followup_debug_memory_injection.md

This document defines logic for follow-up prompt triggering, a lightweight debug dashboard plan, and memory context injection patterns. These systems are designed to enhance response continuity, developer visibility, and AI intelligence in a journaling app context.

## follow_up_logic

### when_to_trigger_follow_up
1. Repeated theme in 3 entries within 5 days
2. Journal ends with uncertainty (keywords: "not sure", "I guess", "maybe")
3. High-intensity emotional tag (e.g. "burnout", "panic") not followed by next entry within 48–72h
4. Unfinished tracked goal still open for >5 days

### schema
```sql
CREATE TABLE follow_up_queue (
  user_id TEXT,
  persona TEXT,
  entry_id UUID,
  reason TEXT,
  scheduled_at TIMESTAMP
);
```

### follow_up_generator_function
```ts
function queueFollowUp({ entryId, persona, reason }) {
  const followUpDate = Date.now() + 2 * 24 * 60 * 60 * 1000;
  insertInto('follow_up_queue', {
    user_id: getUserId(),
    entry_id: entryId,
    persona,
    reason,
    scheduled_at: new Date(followUpDate),
  });
}
```

Claude should write logic to:
- Scan latest 5 entries for repeat patterns
- Flag entries for emotional spikes
- Schedule `follow_up_prompt` using stored templates

---

## debug_dashboard

### purpose
Provide non-coders with easy visibility into AI function call results, failures, and fallback status.

### components
- Last 10 AI logs (from `ai_logs` table)
- Latest error codes or fallback reasons
- Display last inserted journal + matching response
- Show queued follow-ups

### frontend_panel_example
```tsx
if (debugMode) {
  return (
    <DebugPanel>
      <PromptPreview prompt={lastPrompt} />
      <AIResponseView response={lastResponse} />
      <LogViewer logs={aiLogs.slice(0, 10)} />
      <FollowUpQueueList queue={followUpQueue} />
    </DebugPanel>
  );
}
```

Claude should build a mock panel using local props or Supabase real-time queries.

---

## memory_injection_flow

### concept
Use memory snapshot for every AI call, updated weekly or incrementally.

### memory_sources
- `persona_state.known_topics`
- `persona_state.active_goals`
- Last 3 `insight_log` summaries

### prompt_context_model
```ts
function generatePromptContext({ entry, memory }) {
  return {
    user: `Entry: ${entry}`,
    memory: `Themes: ${memory.known_topics.join(', ')}\nGoals: ${memory.active_goals.join(', ')}`,
    prior_insights: memory.insight_summaries.join('\n'),
  };
}
```

Claude should:
- Write helper to fetch + compile memory
- Suggest fallback to recent entries if memory is empty

---

## task_list_for_claude
1. Implement follow-up scheduling logic using Supabase and tagging rules
2. Build `/debug` dashboard UI or dev-only React panel
3. Write helper function to inject memory into prompts consistently
4. Schedule cleanup: expire unused follow-up items after N days
5. Optional: Add `follow_up_triggered_at` to `journal_entries` to prevent duplication
