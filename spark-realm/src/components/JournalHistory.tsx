import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from './ui/dropdown-menu';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';
import { 
  Calendar, 
  Search, 
  Filter, 
  Clock, 
  Heart, 
  Brain, 
  Zap, 
  TrendingUp, 
  ChevronDown, 
  ChevronUp, 
  MoreHorizontal, 
  Trash2, 
  Edit,
  Copy,
  Sparkles,
  BookOpen,
  Shield
} from 'lucide-react';
import { JournalEntry, AIInsightResponse, apiService } from '../services/api';
import { formatDistanceToNow } from 'date-fns';

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
  onEntryDeleted?: (entryId: string) => void; // New callback for when entry is deleted
}

const JournalHistory: React.FC<JournalHistoryProps> = ({
  userId,
  entries,
  isLoading = false,
  onLoadMore,
  hasMore = false,
  onEntryDeleted
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());
  const [filteredEntries, setFilteredEntries] = useState<JournalEntryWithInsights[]>([]);
  
  // Delete confirmation dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [entryToDelete, setEntryToDelete] = useState<JournalEntryWithInsights | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Streaming state management
  const [streamingConnections, setStreamingConnections] = useState<Map<string, WebSocket>>(new Map());
  const [streamingResponses, setStreamingResponses] = useState<Map<string, {
    persona: string;
    content: string;
    isTyping: boolean;
    isComplete: boolean;
  }>>(new Map());
  const [streamingErrors, setStreamingErrors] = useState<Map<string, string>>(new Map());

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

  const handleDeleteEntry = async (entry: JournalEntryWithInsights) => {
    setEntryToDelete(entry);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!entryToDelete) return;

    setIsDeleting(true);
    try {
      await apiService.deleteJournalEntry(entryToDelete.id);
      
      // Call the callback to update parent component
      if (onEntryDeleted) {
        onEntryDeleted(entryToDelete.id);
      }
      
      setDeleteDialogOpen(false);
      setEntryToDelete(null);
    } catch (error) {
      console.error('Failed to delete journal entry:', error);
      // You could add a toast notification here
      alert('Failed to delete entry. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCopyEntry = async (entry: JournalEntryWithInsights) => {
    try {
      await navigator.clipboard.writeText(entry.content);
      // You could add a toast notification here
      alert('Entry copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleGetStructuredResponse = async (entryId: string) => {
    try {
      const response = await apiService.getStructuredAIResponse(entryId);
      alert('Enhanced AI Response generated! Check the console for details.');
      console.log('Structured AI Response:', response);
      // TODO: Update the entry with the new structured response
    } catch (error) {
      console.error('Failed to get structured response:', error);
      alert('Failed to get enhanced response. Please try again.');
    }
  };

  const handleGetMultiPersonaResponse = async (entryId: string) => {
    try {
      const response = await apiService.getMultiPersonaResponse(entryId);
      alert('Multi-AI Response generated! Check the console for details.');
      console.log('Multi-persona AI Response:', response);
      // TODO: Update the entry with the new multi-persona response
    } catch (error) {
      console.error('Failed to get multi-persona response:', error);
      alert('Failed to get multi-AI response. Please try again.');
    }
  };

  const handleStreamingResponse = async (entryId: string, persona: string = "auto") => {
    try {
      // Check if there's already a streaming connection for this entry
      if (streamingConnections.has(entryId)) {
        console.log('Streaming connection already exists for this entry');
        return;
      }

      // Get JWT token from localStorage or your auth system
      const token = localStorage.getItem('authToken');
      if (!token) {
        alert('Please log in to use streaming AI responses.');
        return;
      }

      // Initialize streaming response state
      setStreamingResponses(prev => new Map(prev.set(entryId, {
        persona,
        content: '',
        isTyping: true,
        isComplete: false
      })));

      // Clear any previous errors
      setStreamingErrors(prev => {
        const newErrors = new Map(prev);
        newErrors.delete(entryId);
        return newErrors;
      });

      // Create WebSocket connection
      const ws = apiService.connectToAIStream(entryId, persona, token);
      
      // Store connection
      setStreamingConnections(prev => new Map(prev.set(entryId, ws)));

      // Handle WebSocket messages
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Streaming message:', data);

          switch (data.type) {
            case 'connected':
              console.log('WebSocket connected for entry:', entryId);
              break;
              
            case 'typing':
              setStreamingResponses(prev => new Map(prev.set(entryId, {
                persona: data.persona || persona,
                content: '',
                isTyping: true,
                isComplete: false
              })));
              break;
              
            case 'content':
              setStreamingResponses(prev => {
                const current = prev.get(entryId) || { persona, content: '', isTyping: false, isComplete: false };
                return new Map(prev.set(entryId, {
                  ...current,
                  content: current.content + data.content,
                  isTyping: false
                }));
              });
              break;
              
            case 'complete':
              setStreamingResponses(prev => {
                const current = prev.get(entryId) || { persona, content: '', isTyping: false, isComplete: false };
                return new Map(prev.set(entryId, {
                  ...current,
                  isTyping: false,
                  isComplete: true
                }));
              });
              console.log('Streaming complete for entry:', entryId);
              break;
              
            case 'error':
              setStreamingErrors(prev => new Map(prev.set(entryId, data.message || 'Streaming error occurred')));
              setStreamingResponses(prev => {
                const current = prev.get(entryId) || { persona, content: '', isTyping: false, isComplete: false };
                return new Map(prev.set(entryId, {
                  ...current,
                  isTyping: false,
                  isComplete: true
                }));
              });
              break;
          }
        } catch (error) {
          console.error('Error parsing streaming message:', error);
        }
      };

      // Handle WebSocket errors
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStreamingErrors(prev => new Map(prev.set(entryId, 'Connection error occurred')));
        setStreamingResponses(prev => {
          const current = prev.get(entryId) || { persona, content: '', isTyping: false, isComplete: false };
          return new Map(prev.set(entryId, {
            ...current,
            isTyping: false,
            isComplete: true
          }));
        });
      };

      // Handle WebSocket close
      ws.onclose = () => {
        console.log('WebSocket closed for entry:', entryId);
        setStreamingConnections(prev => {
          const newConnections = new Map(prev);
          newConnections.delete(entryId);
          return newConnections;
        });
      };

    } catch (error) {
      console.error('Failed to start streaming response:', error);
      setStreamingErrors(prev => new Map(prev.set(entryId, 'Failed to start streaming. Please try again.')));
    }
  };

  const stopStreaming = (entryId: string) => {
    const ws = streamingConnections.get(entryId);
    if (ws) {
      ws.close();
      setStreamingConnections(prev => {
        const newConnections = new Map(prev);
        newConnections.delete(entryId);
        return newConnections;
      });
    }
  };

  // Cleanup WebSocket connections on unmount
  useEffect(() => {
    return () => {
      streamingConnections.forEach((ws) => {
        ws.close();
      });
    };
  }, [streamingConnections]);

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
            const previewText = entry.content.length > 600 
              ? entry.content.substring(0, 600) + '...'
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
                      
                      {/* Entry Actions Dropdown */}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleCopyEntry(entry)}>
                            <Copy className="h-4 w-4 mr-2" />
                            Copy text
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleDeleteEntry(entry)}
                            className="text-red-600 focus:text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete entry
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="space-y-3">
                    <p className="text-gray-700 leading-relaxed">
                      {isExpanded ? entry.content : previewText}
                    </p>

                    {entry.content.length > 600 && (
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
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-sm font-medium text-gray-900">AI Responses</h4>
                          {/* Enhanced AI Features Buttons */}
                          <div className="flex gap-1">
                            <button
                              onClick={() => handleGetStructuredResponse(entry.id)}
                              className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition-colors"
                              title="Get structured AI response with rich metadata"
                            >
                              Enhanced
                            </button>
                            <button
                              onClick={() => streamingConnections.has(entry.id) ? stopStreaming(entry.id) : handleStreamingResponse(entry.id)}
                              className={`text-xs px-2 py-1 rounded transition-colors ${
                                streamingConnections.has(entry.id) 
                                  ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                                  : 'bg-green-100 text-green-700 hover:bg-green-200'
                              }`}
                              title={streamingConnections.has(entry.id) ? "Stop streaming response" : "Get real-time streaming AI response"}
                            >
                              {streamingConnections.has(entry.id) ? 'Stop' : 'Stream'}
                            </button>
                          </div>
                        </div>
                        <div className="space-y-3">
                          {/* Display streaming response if active */}
                          {streamingResponses.has(entry.id) && (
                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-lg border border-blue-200">
                              <div className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 flex items-center justify-center flex-shrink-0">
                                  <Sparkles className="h-4 w-4 text-blue-600" />
                                </div>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-medium text-sm text-blue-600">
                                      {streamingResponses.get(entry.id)?.persona.charAt(0).toUpperCase() + streamingResponses.get(entry.id)?.persona.slice(1)} AI
                                    </span>
                                    <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-700">
                                      Streaming
                                    </Badge>
                                    <span className="text-xs text-gray-500">
                                      live
                                    </span>
                                  </div>
                                  
                                  {streamingResponses.get(entry.id)?.isTyping ? (
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                      <div className="flex gap-1">
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                      </div>
                                      <span>AI is thinking...</span>
                                    </div>
                                  ) : (
                                    <div>
                                      <p className="text-sm text-gray-700">{streamingResponses.get(entry.id)?.content}</p>
                                      {streamingResponses.get(entry.id)?.isComplete && (
                                        <div className="mt-2 pt-2 border-t border-gray-200">
                                          <Badge variant="outline" className="bg-green-50 text-green-700 text-xs">
                                            Complete
                                          </Badge>
                                        </div>
                                      )}
                                    </div>
                                  )}
                                  
                                  {streamingErrors.has(entry.id) && (
                                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                                      <strong>Error:</strong> {streamingErrors.get(entry.id)}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {entry.ai_insights.map((insight, index) => {
                            // Define persona-specific styling
                            const personaStyles = {
                              pulse: { bg: 'bg-blue-50', icon: 'bg-blue-100', iconColor: 'text-blue-600', nameColor: 'text-blue-600' },
                              sage: { bg: 'bg-purple-50', icon: 'bg-purple-100', iconColor: 'text-purple-600', nameColor: 'text-purple-600' },
                              spark: { bg: 'bg-orange-50', icon: 'bg-orange-100', iconColor: 'text-orange-600', nameColor: 'text-orange-600' },
                              anchor: { bg: 'bg-green-50', icon: 'bg-green-100', iconColor: 'text-green-600', nameColor: 'text-green-600' }
                            };
                            
                            const persona = insight.persona_used || 'pulse';
                            const style = personaStyles[persona] || personaStyles.pulse;
                            
                            return (
                              <div key={index} className={`${style.bg} p-3 rounded-lg`}>
                                <div className="flex items-start gap-3">
                                  {/* Persona Avatar */}
                                  <div className={`w-8 h-8 rounded-full ${style.icon} flex items-center justify-center flex-shrink-0`}>
                                    {persona === 'pulse' && <Sparkles className={`h-4 w-4 ${style.iconColor}`} />}
                                    {persona === 'sage' && <BookOpen className={`h-4 w-4 ${style.iconColor}`} />}
                                    {persona === 'spark' && <Zap className={`h-4 w-4 ${style.iconColor}`} />}
                                    {persona === 'anchor' && <Shield className={`h-4 w-4 ${style.iconColor}`} />}
                                  </div>
                                  
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className={`font-medium text-sm ${style.nameColor}`}>
                                        {persona.charAt(0).toUpperCase() + persona.slice(1)} AI
                                      </span>
                                      <Badge variant="secondary" className="text-xs">
                                        AI Assistant
                                      </Badge>
                                      <span className="text-xs text-gray-500">
                                        {insight.generated_at ? formatDistanceToNow(new Date(insight.generated_at), { addSuffix: true }) : 'just now'}
                                      </span>
                                    </div>
                                    
                                    <p className="text-sm text-gray-700">{insight.insight}</p>
                                    
                                    {insight.suggested_action && (
                                      <p className="text-sm text-blue-700 mt-1">
                                        💡 {insight.suggested_action}
                                      </p>
                                    )}
                                    
                                    {/* Enhanced metadata display */}
                                    {insight.metadata && (
                                      <div className="mt-2 pt-2 border-t border-gray-200">
                                        <div className="flex flex-wrap gap-1 text-xs">
                                          {insight.metadata.structured_response && (
                                            <Badge variant="outline" className="bg-blue-50 text-blue-700">
                                              Enhanced
                                            </Badge>
                                          )}
                                          {insight.metadata.multi_persona_response && (
                                            <Badge variant="outline" className="bg-purple-50 text-purple-700">
                                              Multi-AI
                                            </Badge>
                                          )}
                                          {insight.metadata.emotional_tone && (
                                            <Badge variant="outline" className="bg-gray-50 text-gray-600">
                                              {insight.metadata.emotional_tone}
                                            </Badge>
                                          )}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Journal Entry?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this journal entry. This action cannot be undone.
              {entryToDelete && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                  <strong>Entry preview:</strong> {entryToDelete.content.substring(0, 100)}
                  {entryToDelete.content.length > 100 && '...'}
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmDelete}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? 'Deleting...' : 'Delete Entry'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default JournalHistory; 