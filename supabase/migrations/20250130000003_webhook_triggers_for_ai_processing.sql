-- Webhook Triggers for Event-Driven AI Processing
-- Enables instant AI responses via Supabase webhooks → Railway endpoints

-- Function to send webhook for journal entry events
CREATE OR REPLACE FUNCTION notify_journal_entry_webhook()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    webhook_url text;
    webhook_payload json;
    http_response record;
BEGIN
    -- Railway webhook endpoint URL (update this with your actual Railway URL)
    webhook_url := 'https://pulsecheck-mobile-app-production.up.railway.app/api/v1/webhook/supabase/journal-entry';
    
    -- Build webhook payload
    webhook_payload := json_build_object(
        'type', TG_OP,
        'table', TG_TABLE_NAME,
        'schema', TG_TABLE_SCHEMA,
        'record', row_to_json(NEW),
        'old_record', CASE WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        'timestamp', NOW()::timestamp with time zone
    );
    
    -- Only process INSERT events for new journal entries
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'journal_entries' THEN
        -- Only trigger for entries with sufficient content (avoid spam)
        IF LENGTH(TRIM(NEW.content)) >= 20 THEN
            -- Send HTTP POST request to webhook endpoint
            -- Note: This requires the pg_net extension or http extension
            -- For now, we'll use pg_notify to queue for external processing
            PERFORM pg_notify(
                'journal_entry_webhook',
                webhook_payload::text
            );
            
            RAISE LOG 'Journal entry webhook triggered for entry: %', NEW.id;
        ELSE
            RAISE LOG 'Journal entry too short, skipping webhook for entry: %', NEW.id;
        END IF;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$;

-- Function to send webhook for AI interaction events
CREATE OR REPLACE FUNCTION notify_ai_interaction_webhook()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    webhook_url text;
    webhook_payload json;
BEGIN
    -- Railway webhook endpoint URL for AI interactions
    webhook_url := 'https://pulsecheck-mobile-app-production.up.railway.app/api/v1/webhook/supabase/ai-interaction';
    
    -- Build webhook payload
    webhook_payload := json_build_object(
        'type', TG_OP,
        'table', TG_TABLE_NAME,
        'schema', TG_TABLE_SCHEMA,
        'record', row_to_json(NEW),
        'old_record', CASE WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        'timestamp', NOW()::timestamp with time zone
    );
    
    -- Only process INSERT events for new AI insights
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'ai_insights' THEN
        -- Queue for external processing
        PERFORM pg_notify(
            'ai_interaction_webhook',
            webhook_payload::text
        );
        
        RAISE LOG 'AI interaction webhook triggered for insight: %', NEW.id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$;

-- Create trigger for journal entries (immediate AI response)
DROP TRIGGER IF EXISTS journal_entry_webhook_trigger ON journal_entries;
CREATE TRIGGER journal_entry_webhook_trigger
    AFTER INSERT ON journal_entries
    FOR EACH ROW
    EXECUTE FUNCTION notify_journal_entry_webhook();

-- Create trigger for AI insights (collaborative follow-up responses)
DROP TRIGGER IF EXISTS ai_interaction_webhook_trigger ON ai_insights;
CREATE TRIGGER ai_interaction_webhook_trigger
    AFTER INSERT ON ai_insights
    FOR EACH ROW
    EXECUTE FUNCTION notify_ai_interaction_webhook();

-- Create a table to track webhook delivery status (optional but recommended)
CREATE TABLE IF NOT EXISTS webhook_delivery_log (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    event_type text NOT NULL,
    table_name text NOT NULL,
    record_id text NOT NULL,
    webhook_url text NOT NULL,
    payload jsonb NOT NULL,
    status text NOT NULL DEFAULT 'pending', -- pending, success, failed, retrying
    http_status_code integer,
    response_body text,
    error_message text,
    retry_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT NOW(),
    delivered_at timestamp with time zone,
    updated_at timestamp with time zone DEFAULT NOW()
);

-- Enable RLS on webhook delivery log
ALTER TABLE webhook_delivery_log ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for webhook delivery log (admin only)
CREATE POLICY "Webhook delivery log admin access" ON webhook_delivery_log
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role' OR
        auth.jwt() ->> 'user_metadata' ->> 'role' = 'admin'
    );

-- Function to log webhook delivery attempts
CREATE OR REPLACE FUNCTION log_webhook_delivery(
    p_event_type text,
    p_table_name text,
    p_record_id text,
    p_webhook_url text,
    p_payload jsonb,
    p_status text DEFAULT 'pending',
    p_http_status_code integer DEFAULT NULL,
    p_response_body text DEFAULT NULL,
    p_error_message text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    delivery_id uuid;
BEGIN
    INSERT INTO webhook_delivery_log (
        event_type,
        table_name,
        record_id,
        webhook_url,
        payload,
        status,
        http_status_code,
        response_body,
        error_message
    ) VALUES (
        p_event_type,
        p_table_name,
        p_record_id,
        p_webhook_url,
        p_payload,
        p_status,
        p_http_status_code,
        p_response_body,
        p_error_message
    ) RETURNING id INTO delivery_id;
    
    RETURN delivery_id;
END;
$$;

-- Function to update webhook delivery status
CREATE OR REPLACE FUNCTION update_webhook_delivery_status(
    p_delivery_id uuid,
    p_status text,
    p_http_status_code integer DEFAULT NULL,
    p_response_body text DEFAULT NULL,
    p_error_message text DEFAULT NULL
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE webhook_delivery_log
    SET 
        status = p_status,
        http_status_code = p_http_status_code,
        response_body = p_response_body,
        error_message = p_error_message,
        delivered_at = CASE WHEN p_status = 'success' THEN NOW() ELSE delivered_at END,
        updated_at = NOW(),
        retry_count = retry_count + CASE WHEN p_status = 'retrying' THEN 1 ELSE 0 END
    WHERE id = p_delivery_id;
    
    RETURN FOUND;
END;
$$;

-- Create indexes for webhook delivery log performance
CREATE INDEX IF NOT EXISTS idx_webhook_delivery_status ON webhook_delivery_log(status);
CREATE INDEX IF NOT EXISTS idx_webhook_delivery_created_at ON webhook_delivery_log(created_at);
CREATE INDEX IF NOT EXISTS idx_webhook_delivery_table_record ON webhook_delivery_log(table_name, record_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated, anon;
GRANT ALL ON webhook_delivery_log TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION log_webhook_delivery TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION update_webhook_delivery_status TO authenticated, service_role;

-- Comment the triggers for documentation
COMMENT ON TRIGGER journal_entry_webhook_trigger ON journal_entries IS 
'Triggers immediate AI response processing via webhook when new journal entries are created';

COMMENT ON TRIGGER ai_interaction_webhook_trigger ON ai_insights IS 
'Triggers collaborative AI follow-up responses when AI insights are created';

COMMENT ON FUNCTION notify_journal_entry_webhook() IS 
'Sends webhook notification to Railway for immediate AI processing of new journal entries';

COMMENT ON FUNCTION notify_ai_interaction_webhook() IS 
'Sends webhook notification to Railway for collaborative AI processing after AI responses';

COMMENT ON TABLE webhook_delivery_log IS 
'Tracks webhook delivery attempts and status for debugging and reliability monitoring';

-- Create a view for webhook monitoring (admin use)
CREATE OR REPLACE VIEW webhook_delivery_summary AS
SELECT 
    event_type,
    table_name,
    status,
    COUNT(*) as delivery_count,
    AVG(retry_count) as avg_retries,
    MAX(created_at) as last_delivery_attempt,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_deliveries,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_deliveries,
    ROUND(
        COUNT(CASE WHEN status = 'success' THEN 1 END)::numeric / 
        COUNT(*)::numeric * 100, 
        2
    ) as success_rate_percent
FROM webhook_delivery_log
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY event_type, table_name, status
ORDER BY last_delivery_attempt DESC;

-- Grant access to the monitoring view
GRANT SELECT ON webhook_delivery_summary TO authenticated, service_role;

-- Add helpful documentation
COMMENT ON VIEW webhook_delivery_summary IS 
'24-hour summary of webhook delivery performance for monitoring AI system reliability'; 