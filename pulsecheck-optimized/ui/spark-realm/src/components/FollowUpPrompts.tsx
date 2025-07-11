import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Clock, TrendingUp, Heart, Brain, Target, Calendar } from 'lucide-react';

interface FollowUpPrompt {
  id: string;
  type: 'reflection' | 'action' | 'check_in' | 'pattern' | 'goal_progress' | 'mood_follow_up';
  prompt: string;
  context: string;
  urgency: 'low' | 'medium' | 'high';
  days_since_trigger: number;
  related_entry_id?: string;
  related_topics: string[];
  suggested_timing: 'morning' | 'afternoon' | 'evening' | 'anytime';
}

interface JournalEntryData {
  id: string;
  content: string;
  mood_level: number;
  stress_level: number;
  created_at: string;
  tags?: string[];
}

interface FollowUpPromptsProps {
  userId: string;
  recentEntries: JournalEntryData[]; // Journal entries from the last week
  onPromptSelect: (prompt: FollowUpPrompt) => void;
  className?: string;
}

const FollowUpPrompts: React.FC<FollowUpPromptsProps> = ({
  userId,
  recentEntries,
  onPromptSelect,
  className = ""
}) => {
  const [activePrompts, setActivePrompts] = useState<FollowUpPrompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<FollowUpPrompt | null>(null);
  const [showAllPrompts, setShowAllPrompts] = useState(false);

  useEffect(() => {
    generateFollowUpPrompts();
  }, [recentEntries]);

  const generateFollowUpPrompts = () => {
    const prompts: FollowUpPrompt[] = [];
    const now = new Date();

    // Analyze recent entries for follow-up opportunities
    recentEntries.forEach((entry, index) => {
      const entryDate = new Date(entry.created_at);
      const daysSince = Math.floor((now.getTime() - entryDate.getTime()) / (1000 * 60 * 60 * 24));
      
      // Skip entries older than 7 days
      if (daysSince > 7) return;

      // Generate different types of follow-ups based on entry content and timing
      
      // 1. Reflection Follow-ups (2-3 days after significant entries)
      if (daysSince >= 2 && daysSince <= 3 && entry.content.length > 200) {
        prompts.push({
          id: `reflection_${entry.id}`,
          type: 'reflection',
          prompt: `A few days ago, you shared some deep thoughts. How are those feelings sitting with you now?`,
          context: `Following up on your entry from ${daysSince} days ago`,
          urgency: 'medium',
          days_since_trigger: daysSince,
          related_entry_id: entry.id,
          related_topics: entry.tags || [],
          suggested_timing: 'evening'
        });
      }

      // 2. Action Follow-ups (1 day after goal-setting entries)
      if (daysSince === 1 && (entry.content.includes('goal') || entry.content.includes('plan') || entry.content.includes('want to'))) {
        prompts.push({
          id: `action_${entry.id}`,
          type: 'action',
          prompt: `Yesterday you mentioned some intentions. How did today go with those in mind?`,
          context: `Following up on goals from yesterday`,
          urgency: 'high',
          days_since_trigger: daysSince,
          related_entry_id: entry.id,
          related_topics: entry.tags || [],
          suggested_timing: 'evening'
        });
      }

      // 3. Mood Follow-ups (for concerning mood patterns)
      if (entry.mood_level <= 4 && daysSince >= 1 && daysSince <= 2) {
        prompts.push({
          id: `mood_${entry.id}`,
          type: 'mood_follow_up',
          prompt: `I noticed you were having a tough time recently. How are you feeling today?`,
          context: `Checking in after a difficult day`,
          urgency: 'high',
          days_since_trigger: daysSince,
          related_entry_id: entry.id,
          related_topics: ['mood', 'support'],
          suggested_timing: 'afternoon'
        });
      }

      // 4. Stress Follow-ups (for high stress entries)
      if (entry.stress_level >= 7 && daysSince >= 1 && daysSince <= 3) {
        prompts.push({
          id: `stress_${entry.id}`,
          type: 'check_in',
          prompt: `You mentioned feeling stressed recently. What's helping you manage that stress today?`,
          context: `Following up on stress management`,
          urgency: 'medium',
          days_since_trigger: daysSince,
          related_entry_id: entry.id,
          related_topics: ['stress', 'coping'],
          suggested_timing: 'afternoon'
        });
      }
    });

    // 5. Pattern Recognition Prompts (based on recurring themes)
    const topicCounts: Record<string, number> = recentEntries.reduce((acc, entry) => {
      (entry.tags || []).forEach(tag => {
        acc[tag] = (acc[tag] || 0) + 1;
      });
      return acc;
    }, {} as Record<string, number>);

    Object.entries(topicCounts).forEach(([topic, count]) => {
      if (count >= 3) { // Topic appeared 3+ times in recent entries
        prompts.push({
          id: `pattern_${topic}`,
          type: 'pattern',
          prompt: `I've noticed ${topic.replace('_', ' ')} has been on your mind lately. What patterns are you seeing?`,
          context: `Recurring theme: ${topic.replace('_', ' ')}`,
          urgency: 'medium',
          days_since_trigger: 0,
          related_topics: [topic],
          suggested_timing: 'anytime'
        });
      }
    });

    // 6. General Check-ins (if no entries in 2+ days)
    const lastEntryDate = recentEntries.length > 0 ? new Date(recentEntries[0].created_at) : null;
    const daysSinceLastEntry = lastEntryDate ? Math.floor((now.getTime() - lastEntryDate.getTime()) / (1000 * 60 * 60 * 24)) : 0;
    
    if (daysSinceLastEntry >= 2) {
      prompts.push({
        id: 'general_checkin',
        type: 'check_in',
        prompt: `It's been a few days since you last checked in. What's been on your mind?`,
        context: `General check-in after ${daysSinceLastEntry} days`,
        urgency: 'low',
        days_since_trigger: daysSinceLastEntry,
        related_topics: ['general'],
        suggested_timing: 'anytime'
      });
    }

    // Sort by urgency and recency
    const sortedPrompts = prompts.sort((a, b) => {
      const urgencyOrder = { high: 3, medium: 2, low: 1 };
      if (urgencyOrder[a.urgency] !== urgencyOrder[b.urgency]) {
        return urgencyOrder[b.urgency] - urgencyOrder[a.urgency];
      }
      return a.days_since_trigger - b.days_since_trigger;
    });

    setActivePrompts(sortedPrompts);
  };

  const getPromptIcon = (type: string) => {
    switch (type) {
      case 'reflection': return <Brain className="w-4 h-4" />;
      case 'action': return <Target className="w-4 h-4" />;
      case 'check_in': return <Heart className="w-4 h-4" />;
      case 'pattern': return <TrendingUp className="w-4 h-4" />;
      case 'goal_progress': return <Target className="w-4 h-4" />;
      case 'mood_follow_up': return <Heart className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const handlePromptSelect = (prompt: FollowUpPrompt) => {
    setSelectedPrompt(prompt);
    onPromptSelect(prompt);
  };

  const displayPrompts = showAllPrompts ? activePrompts : activePrompts.slice(0, 3);

  if (activePrompts.length === 0) {
    return null; // Don't show component if no prompts
  }

  return (
    <Card className={`border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-purple-700 text-base">
          <Clock className="w-4 h-4" />
          Smart Follow-ups
        </CardTitle>
        <p className="text-sm text-purple-600">
          Personalized prompts based on your recent reflections
        </p>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {displayPrompts.map((prompt) => (
          <div
            key={prompt.id}
            className={`p-3 rounded-lg border transition-all cursor-pointer hover:shadow-md ${
              selectedPrompt?.id === prompt.id 
                ? 'bg-purple-100 border-purple-300 shadow-md' 
                : 'bg-white/70 border-purple-200 hover:bg-purple-50'
            }`}
            onClick={() => handlePromptSelect(prompt)}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 p-2 rounded-full bg-purple-100">
                {getPromptIcon(prompt.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Badge 
                    variant="secondary" 
                    className={`text-xs ${getUrgencyColor(prompt.urgency)}`}
                  >
                    {prompt.urgency} priority
                  </Badge>
                  <span className="text-xs text-gray-500">
                    {prompt.suggested_timing}
                  </span>
                </div>
                
                <p className="text-sm font-medium text-gray-800 mb-1">
                  {prompt.prompt}
                </p>
                
                <p className="text-xs text-gray-600">
                  {prompt.context}
                </p>
                
                {prompt.related_topics.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {prompt.related_topics.slice(0, 3).map(topic => (
                      <Badge key={topic} variant="outline" className="text-xs">
                        {topic.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="flex-shrink-0">
                <Button
                  size="sm"
                  variant={selectedPrompt?.id === prompt.id ? "default" : "ghost"}
                  className="text-xs"
                >
                  {selectedPrompt?.id === prompt.id ? "Selected" : "Use"}
                </Button>
              </div>
            </div>
          </div>
        ))}

        {/* Show More/Less */}
        {activePrompts.length > 3 && (
          <div className="flex justify-center pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAllPrompts(!showAllPrompts)}
              className="text-xs text-purple-600 hover:text-purple-700"
            >
              {showAllPrompts ? "Show fewer" : `Show ${activePrompts.length - 3} more`}
            </Button>
          </div>
        )}

        {/* Selected Prompt Action */}
        {selectedPrompt && (
          <div className="mt-4 p-3 bg-white rounded-lg border border-purple-300">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-700">
                Ready to reflect?
              </span>
            </div>
            <p className="text-sm text-gray-700">
              This prompt will be used as your journal starter. You can modify it or write freely about anything else.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FollowUpPrompts; 