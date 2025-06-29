import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';

interface AIHealthMetrics {
  timestamp: string;
  ai_status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL' | 'ERROR';
  status_color: string;
  metrics: {
    total_entries_24h: number;
    entries_with_ai_response: number;
    entries_without_ai_response: number;
    ai_response_rate_percent: number;
    pending_entries_count: number;
    stuck_entries_count: number;
  };
  pending_entries: Array<{
    entry_id: string;
    user_id: string;
    content_preview: string;
    minutes_waiting: number;
    created_at: string;
  }>;
  stuck_entries: Array<{
    entry_id: string;
    user_id: string;
    content_preview: string;
    minutes_waiting: number;
    created_at: string;
  }>;
  recommendations: string[];
  error?: string;
}

interface ProcessingQueue {
  timestamp: string;
  queue_summary: {
    total_in_queue: number;
    processing: number;
    delayed: number;
    stuck: number;
  };
  processing_items: any[];
  delayed_items: any[];
  stuck_items: any[];
  queue_health: 'HEALTHY' | 'DEGRADED' | 'CRITICAL';
}

interface ResponseTimes {
  timestamp: string;
  hours_analyzed: number;
  total_responses: number;
  performance_metrics: {
    average_response_time_minutes: number;
    min_response_time_minutes: number;
    max_response_time_minutes: number;
    fast_responses_under_2min: number;
    normal_responses_2_5min: number;
    slow_responses_over_5min: number;
  };
  performance_distribution: {
    fast_percentage: number;
    normal_percentage: number;
    slow_percentage: number;
  };
  recent_responses: any[];
}

const AIMonitoring: React.FC = () => {
  const [aiHealth, setAIHealth] = useState<AIHealthMetrics | null>(null);
  const [processingQueue, setProcessingQueue] = useState<ProcessingQueue | null>(null);
  const [responseTimes, setResponseTimes] = useState<ResponseTimes | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const API_BASE = process.env.REACT_APP_API_URL || 'https://pulsecheck-backend-production.up.railway.app';

  const fetchAIHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/ai-monitor/health`);
      if (response.ok) {
        const data = await response.json();
        setAIHealth(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      console.error('Failed to fetch AI health:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch AI health');
    }
  };

  const fetchProcessingQueue = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/ai-monitor/processing-queue`);
      if (response.ok) {
        const data = await response.json();
        setProcessingQueue(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      console.error('Failed to fetch processing queue:', err);
    }
  };

  const fetchResponseTimes = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/ai-monitor/response-times`);
      if (response.ok) {
        const data = await response.json();
        setResponseTimes(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      console.error('Failed to fetch response times:', err);
    }
  };

  const triggerAIResponse = async (entryId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/ai-monitor/trigger-response/${entryId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`AI response triggered successfully!\nResponse: ${data.ai_response?.substring(0, 200)}...`);
        // Refresh data after triggering
        await fetchAllData();
      } else {
        const errorData = await response.json();
        alert(`Failed to trigger AI response: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Failed to trigger AI response:', err);
      alert(`Error triggering AI response: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    await Promise.all([
      fetchAIHealth(),
      fetchProcessingQueue(),
      fetchResponseTimes()
    ]);
    
    setLoading(false);
  };

  useEffect(() => {
    fetchAllData();
    
    // Auto-refresh every 30 seconds if enabled
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchAllData, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'HEALTHY': return 'bg-green-500';
      case 'DEGRADED': return 'bg-yellow-500';
      case 'CRITICAL': return 'bg-red-500';
      case 'ERROR': return 'bg-red-600';
      default: return 'bg-gray-500';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading && !aiHealth) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-lg">Loading AI monitoring data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">AI Monitoring Dashboard</h1>
        <div className="flex gap-2">
          <Button
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant={autoRefresh ? "default" : "outline"}
          >
            {autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
          </Button>
          <Button onClick={fetchAllData} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh Now"}
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="border-red-500">
          <AlertDescription>
            ⚠️ Error loading data: {error}
          </AlertDescription>
        </Alert>
      )}

      {/* AI Health Status */}
      {aiHealth && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              AI Health Status
              <Badge className={`${getStatusBadgeColor(aiHealth.ai_status)} text-white`}>
                {aiHealth.ai_status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{aiHealth.metrics.ai_response_rate_percent}%</div>
                <div className="text-sm text-gray-600">Response Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{aiHealth.metrics.pending_entries_count}</div>
                <div className="text-sm text-gray-600">Pending Entries</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{aiHealth.metrics.stuck_entries_count}</div>
                <div className="text-sm text-gray-600">Stuck Entries</div>
              </div>
            </div>

            <div className="text-sm text-gray-500 mb-4">
              Last updated: {formatTimestamp(aiHealth.timestamp)}
            </div>

            {aiHealth.recommendations.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">Recommendations:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {aiHealth.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm">{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            {aiHealth.error && (
              <Alert className="mt-4 border-red-500">
                <AlertDescription>
                  Error: {aiHealth.error}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Processing Queue */}
      {processingQueue && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Processing Queue
              <Badge className={`${getStatusBadgeColor(processingQueue.queue_health)} text-white`}>
                {processingQueue.queue_health}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className="text-xl font-bold">{processingQueue.queue_summary.total_in_queue}</div>
                <div className="text-sm text-gray-600">Total in Queue</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-blue-600">{processingQueue.queue_summary.processing}</div>
                <div className="text-sm text-gray-600">Processing</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-yellow-600">{processingQueue.queue_summary.delayed}</div>
                <div className="text-sm text-gray-600">Delayed</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-red-600">{processingQueue.queue_summary.stuck}</div>
                <div className="text-sm text-gray-600">Stuck</div>
              </div>
            </div>

            {processingQueue.stuck_items.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Stuck Entries (require manual intervention):</h4>
                <div className="space-y-2">
                  {processingQueue.stuck_items.map((item: any) => (
                    <div key={item.id} className="border p-3 rounded bg-red-50">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="text-sm font-medium">Entry ID: {item.id}</div>
                          <div className="text-sm text-gray-600">Waiting: {Math.round(item.minutes_waiting)} minutes</div>
                          <div className="text-sm mt-1">{item.content.substring(0, 100)}...</div>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => triggerAIResponse(item.id)}
                          className="ml-2"
                        >
                          Trigger AI
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Response Times */}
      {responseTimes && responseTimes.total_responses > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Response Time Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-xl font-bold">{responseTimes.performance_metrics.average_response_time_minutes.toFixed(1)}m</div>
                <div className="text-sm text-gray-600">Average Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-green-600">{responseTimes.performance_distribution.fast_percentage}%</div>
                <div className="text-sm text-gray-600">Fast Responses (&lt;2m)</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-red-600">{responseTimes.performance_distribution.slow_percentage}%</div>
                <div className="text-sm text-gray-600">Slow Responses (&gt;5m)</div>
              </div>
            </div>

            <div className="text-sm text-gray-500">
              Analysis of {responseTimes.total_responses} responses in the last {responseTimes.hours_analyzed} hours
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stuck Entries Action Panel */}
      {aiHealth && aiHealth.stuck_entries.length > 0 && (
        <Card className="border-red-500">
          <CardHeader>
            <CardTitle className="text-red-600">🚨 Stuck Entries Requiring Attention</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {aiHealth.stuck_entries.map((entry) => (
                <div key={entry.entry_id} className="border p-3 rounded bg-red-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="text-sm font-medium">Entry ID: {entry.entry_id}</div>
                      <div className="text-sm text-gray-600">
                        User: {entry.user_id} | Waiting: {entry.minutes_waiting} minutes
                      </div>
                      <div className="text-sm mt-1">{entry.content_preview}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Created: {formatTimestamp(entry.created_at)}
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => triggerAIResponse(entry.entry_id)}
                      className="ml-2 bg-red-600 hover:bg-red-700"
                    >
                      Trigger AI Response
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIMonitoring; 