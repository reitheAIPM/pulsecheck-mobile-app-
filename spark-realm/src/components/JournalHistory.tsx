import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Calendar, Search, Filter, Clock, Heart, Brain, Zap, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import { JournalEntry, AIInsightResponse } from '../services/api';

// Extended journal entry with AI insights for history display
interface JournalEntryWithInsights extends JournalEntry {
  ai_insights?: AIInsightResponse[];
}

interface JournalHistoryProps {
  userId: string;
  entries: JournalEntryWithInsights[];
  isLoading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

const JournalHistory: React.FC<JournalHistoryProps> = ({
  userId,
  entries,
  isLoading = false,
  onLoadMore,
  hasMore = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());
  const [filteredEntries, setFilteredEntries] = useState<JournalEntryWithInsights[]>([]);

  useEffect(() => {
    let filtered = [...entries];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(entry =>
        entry.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Mood filter
    if (filterBy !== 'all') {
      switch (filterBy) {
        case 'high-mood':
          filtered = filtered.filter(entry => entry.mood_level >= 7);
          break;
        case 'low-mood':
          filtered = filtered.filter(entry => entry.mood_level <= 4);
          break;
        case 'high-stress':
          filtered = filtered.filter(entry => entry.stress_level >= 7);
          break;
        case 'low-energy':
          filtered = filtered.filter(entry => entry.energy_level <= 4);
          break;
        case 'with-ai':
          // Filter entries that have AI responses
          filtered = filtered.filter(entry => entry.ai_insights && entry.ai_insights.length > 0);
          break;
      }
    }

    // Sort
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        break;
      case 'mood-high':
        filtered.sort((a, b) => b.mood_level - a.mood_level);
        break;
      case 'mood-low':
        filtered.sort((a, b) => a.mood_level - b.mood_level);
        break;
    }

    setFilteredEntries(filtered);
  }, [entries, searchTerm, sortBy, filterBy]);

  const toggleExpanded = (entryId: string) => {
    const newExpanded = new Set(expandedEntries);
    if (newExpanded.has(entryId)) {
      newExpanded.delete(entryId);
    } else {
      newExpanded.add(entryId);
    }
    setExpandedEntries(newExpanded);
  };

  const getMoodIcon = (mood: number) => {
    if (mood >= 8) return <Heart className="h-4 w-4 text-green-500" />;
    if (mood >= 6) return <TrendingUp className="h-4 w-4 text-blue-500" />;
    if (mood >= 4) return <Brain className="h-4 w-4 text-yellow-500" />;
    return <Zap className="h-4 w-4 text-red-500" />;
  };

  const getMoodColor = (mood: number) => {
    if (mood >= 8) return 'bg-green-100 text-green-800 border-green-200';
    if (mood >= 6) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (mood >= 4) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  if (isLoading && entries.length === 0) {
    return (
      <div className="space-y-4">
        <div className="h-6 bg-gray-200 rounded w-1/3 animate-pulse"></div>
        {[1, 2, 3].map(i => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-500" />
          <h2 className="text-xl font-semibold">Journal History</h2>
          <Badge variant="secondary" className="text-xs">
            {filteredEntries.length} {filteredEntries.length === 1 ? 'entry' : 'entries'}
          </Badge>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search your journal entries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="newest">Newest First</SelectItem>
            <SelectItem value="oldest">Oldest First</SelectItem>
            <SelectItem value="mood-high">Highest Mood</SelectItem>
            <SelectItem value="mood-low">Lowest Mood</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterBy} onValueChange={setFilterBy}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Entries</SelectItem>
            <SelectItem value="high-mood">High Mood (7+)</SelectItem>
            <SelectItem value="low-mood">Low Mood (≤4)</SelectItem>
            <SelectItem value="high-stress">High Stress (7+)</SelectItem>
            <SelectItem value="low-energy">Low Energy (≤4)</SelectItem>
            <SelectItem value="with-ai">With AI Responses</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Journal Entries */}
      <div className="space-y-4">
        {filteredEntries.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No entries found</h3>
              <p className="text-gray-600">
                {searchTerm || filterBy !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Start journaling to see your entries here'
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredEntries.map((entry) => {
            const isExpanded = expandedEntries.has(entry.id);
            const previewText = entry.content.length > 150 
              ? entry.content.substring(0, 150) + '...'
              : entry.content;

            return (
              <Card key={entry.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        {getMoodIcon(entry.mood_level)}
                        <span className="text-sm font-medium">
                          {formatDate(entry.created_at)}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <Badge variant="outline" className={`text-xs ${getMoodColor(entry.mood_level)}`}>
                          Mood {entry.mood_level}/10
                        </Badge>
                        {entry.stress_level >= 7 && (
                          <Badge variant="outline" className="text-xs bg-red-100 text-red-800">
                            High Stress
                          </Badge>
                        )}
                        {entry.energy_level <= 3 && (
                          <Badge variant="outline" className="text-xs bg-orange-100 text-orange-800">
                            Low Energy
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {new Date(entry.created_at).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="space-y-3">
                    <p className="text-gray-700 leading-relaxed">
                      {isExpanded ? entry.content : previewText}
                    </p>

                    {entry.content.length > 150 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleExpanded(entry.id)}
                        className="p-0 h-auto text-blue-600 hover:text-blue-800"
                      >
                        {isExpanded ? (
                          <>
                            <ChevronUp className="h-4 w-4 mr-1" />
                            Show less
                          </>
                        ) : (
                          <>
                            <ChevronDown className="h-4 w-4 mr-1" />
                            Read more
                          </>
                        )}
                      </Button>
                    )}

                    {/* AI Responses */}
                    {entry.ai_insights && entry.ai_insights.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">AI Responses</h4>
                        <div className="space-y-2">
                          {entry.ai_insights.map((insight, index) => (
                            <div key={index} className="bg-blue-50 p-3 rounded-lg">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge variant="secondary" className="text-xs">
                                  {insight.persona_used || 'Pulse'}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-700">{insight.insight}</p>
                              {insight.suggested_action && (
                                <p className="text-sm text-blue-700 mt-1">
                                  💡 {insight.suggested_action}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Load More */}
      {hasMore && (
        <div className="text-center">
          <Button 
            variant="outline" 
            onClick={onLoadMore}
            disabled={isLoading}
            className="w-full sm:w-auto"
          >
            {isLoading ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-gray-500 border-t-transparent rounded-full mr-2"></div>
                Loading...
              </>
            ) : (
              'Load More Entries'
            )}
          </Button>
        </div>
      )}
    </div>
  );
};

export default JournalHistory; 