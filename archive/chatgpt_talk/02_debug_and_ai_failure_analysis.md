# debug_and_ai_failure_analysis.md

This document addresses the ongoing issue where the AI does not respond to journal entries despite correct setup. It outlines diagnostic hypotheses, backend checks, and implementation patterns to resolve the issue.

## problem_context
- ENV variables, API routing, and CORS are already verified
- Supabase insertions and LLM call triggers are active
- App is developed with Cursor; user is non-technical

## failure_hypotheses

### 1. async_timing_or_write_race
- AI may call before journal record commit
- DB write may fail silently

### 2. frontend_polling_issue
- App does not re-fetch or poll after submission
- State update may not trigger rerender

### 3. model_response_success_but_discarded
- LLM returns result but it isn't inserted into `ai_responses`
- Insert error is not surfaced

### 4. silent_failure_no_logs
- Missing error boundary, response logs, or async fail visibility

## logging_improvements

### ai_logs table
```sql
CREATE TABLE ai_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  persona TEXT,
  model TEXT,
  latency_ms INT,
  status TEXT,
  error_code TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### recommended debug log lines
```ts
console.log("LLM response received", llm_result);
console.log("Attempting to write to DB", llm_result);
```

### logging_insertion
- Add fallback try/catch around `insert()` logic
- Write log of final payload and insertion status

## fallback_and_retries
- Implement retry pattern with backoff on LLM response or DB insert
- Claude can suggest a safe retry architecture compatible with Supabase triggers or async queueing

## simulate_mode
```ts
GET /api/simulate?persona=echo
// returns dummy payload for UI testing
```

## task_list_for_claude
1. Trace backend LLM call → DB insert → frontend render
2. Propose logging wrapper with log storage
3. Write safe retry pattern with visibility
4. Build debug toggle for UI (show prompt + response JSON)
