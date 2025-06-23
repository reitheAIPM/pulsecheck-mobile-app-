import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { 
  Calendar, 
  BookOpen, 
  TrendingUp, 
  ChevronLeft, 
  ChevronRight,
  MessageCircle,
  Heart,
  Star,
  Clock,
  Filter,
  Search,
  MoreHorizontal,
  Trash2,
  Copy,
  Edit
} from 'lucide-react';
import { apiService, JournalEntry } from '@/services/api';

// Calendar utilities
const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const History = () => {
  const navigate = useNavigate();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntry, setSelectedEntry] = useState<JournalEntry | null>(null);
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');
  
  // Delete confirmation dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [entryToDelete, setEntryToDelete] = useState<JournalEntry | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Mock AI responses for entries (in real app, these would come from backend)
  const mockAIResponses = {
    'entry-1': {
      reactions: ['❤️', '💪', '🌟'],
      comment: "I can see you're really growing in self-awareness. Your reflection on work-life balance shows incredible insight.",
      timestamp: '2 hours ago'
    },
    'entry-2': {
      reactions: ['🤗', '✨', '👏'],
      comment: "Your gratitude practice is beautiful. These small moments of appreciation are building your resilience.",
      timestamp: '1 day ago'
    }
  };

  useEffect(() => {
    loadJournalEntries();
  }, []);

  const loadJournalEntries = async () => {
    setLoading(true);
    try {
      const entries = await apiService.getJournalEntries(1, 100); // Get more entries for calendar view
      setJournalEntries(entries);
    } catch (error) {
      console.error('Failed to load journal entries:', error);
      // Use mock data for development
      setJournalEntries([
        {
          id: 'entry-1',
          user_id: 'user-123',
          content: "Today was challenging but I managed to find some balance. The new project at work is demanding, but I'm learning to set boundaries. Grateful for my morning coffee ritual - it's become my moment of peace before the day begins.",
          mood_level: 7,
          energy_level: 6,
          stress_level: 4,
          sleep_hours: 7,
          work_hours: 9,
          tags: ['work', 'balance', 'gratitude'],
          work_challenges: ['tight deadlines', 'team coordination'],
          gratitude_items: ['morning coffee', 'supportive team', 'good weather'],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'entry-2',
          user_id: 'user-123',
          content: "Feeling more centered today. The meditation app recommendation from Pulse really helped. I'm starting to notice patterns in my stress levels - they peak around 3pm. Maybe I should schedule breaks differently.",
          mood_level: 8,
          energy_level: 7,
          stress_level: 3,
          sleep_hours: 8,
          work_hours: 8,
          tags: ['meditation', 'patterns', 'self-care'],
          work_challenges: ['afternoon energy dip'],
          gratitude_items: ['meditation practice', 'pattern recognition', 'flexible schedule'],
          created_at: new Date(Date.now() - 86400000).toISOString(), // Yesterday
          updated_at: new Date(Date.now() - 86400000).toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Get entries for a specific date
  const getEntriesForDate = (date: Date): JournalEntry[] => {
    const dateStr = date.toDateString();
    return journalEntries.filter(entry => {
      const entryDate = new Date(entry.created_at);
      return entryDate.toDateString() === dateStr;
    });
  };

  // Check if a date has entries
  const hasEntriesForDate = (date: Date): boolean => {
    return getEntriesForDate(date).length > 0;
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const currentDateObj = new Date(startDate);
    
    for (let i = 0; i < 42; i++) { // 6 weeks * 7 days
      days.push(new Date(currentDateObj));
      currentDateObj.setDate(currentDateObj.getDate() + 1);
    }
    
    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
    setSelectedDate(null);
  };

  const selectDate = (date: Date) => {
    setSelectedDate(date);
    const entries = getEntriesForDate(date);
    if (entries.length > 0) {
      setSelectedEntry(entries[0]); // Show first entry for the date
    } else {
      setSelectedEntry(null);
    }
  };

  const getMoodColor = (mood: number) => {
    if (mood >= 8) return 'bg-green-500';
    if (mood >= 6) return 'bg-yellow-500';
    if (mood >= 4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleDeleteEntry = async (entry: JournalEntry) => {
    setEntryToDelete(entry);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!entryToDelete) return;

    setIsDeleting(true);
    try {
      await apiService.deleteJournalEntry(entryToDelete.id);
      
      // Remove the entry from local state
      setJournalEntries(prev => prev.filter(e => e.id !== entryToDelete.id));
      
      // Clear selected entry if it was the deleted one
      if (selectedEntry?.id === entryToDelete.id) {
        setSelectedEntry(null);
      }
      
      setDeleteDialogOpen(false);
      setEntryToDelete(null);
    } catch (error) {
      console.error('Failed to delete journal entry:', error);
      alert('Failed to delete entry. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCopyEntry = async (entry: JournalEntry) => {
    try {
      await navigator.clipboard.writeText(entry.content);
      alert('Entry copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <div className="max-w-lg mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">Journal History</h1>
                <p className="text-sm text-muted-foreground">
                  Your wellness journey over time
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'calendar' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('calendar')}
              >
                <Calendar className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <Filter className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6">
        {viewMode === 'calendar' ? (
          <div className="space-y-6">
            {/* Calendar Navigation */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigateMonth('prev')}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <CardTitle className="text-lg">
                    {MONTHS[currentDate.getMonth()]} {currentDate.getFullYear()}
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigateMonth('next')}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-1 mb-4">
                  {DAYS_OF_WEEK.map(day => (
                    <div key={day} className="text-center text-xs font-medium text-muted-foreground py-2">
                      {day}
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {generateCalendarDays().map((date, index) => {
                    const isCurrentMonth = date.getMonth() === currentDate.getMonth();
                    const isToday = date.toDateString() === new Date().toDateString();
                    const isSelected = selectedDate?.toDateString() === date.toDateString();
                    const hasEntries = hasEntriesForDate(date);
                    const entries = getEntriesForDate(date);
                    
                    return (
                      <button
                        key={index}
                        onClick={() => selectDate(date)}
                        className={`
                          relative aspect-square p-1 text-sm rounded-lg transition-all
                          ${!isCurrentMonth ? 'text-muted-foreground/50' : ''}
                          ${isToday ? 'ring-2 ring-primary' : ''}
                          ${isSelected ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}
                          ${hasEntries ? 'font-semibold' : ''}
                        `}
                      >
                        <span>{date.getDate()}</span>
                        {hasEntries && (
                          <div className="absolute bottom-0.5 left-1/2 transform -translate-x-1/2">
                            <div className={`w-1.5 h-1.5 rounded-full ${getMoodColor(entries[0].mood_level)}`} />
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Selected Date Details */}
            {selectedDate && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {formatDate(selectedDate)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedEntry ? (
                    <div className="space-y-4">
                      {/* Entry Content */}
                      <div className="space-y-3">
                        <p className="text-sm leading-relaxed">{selectedEntry.content}</p>
                        
                        {/* Metrics */}
                        <div className="flex gap-4 text-xs">
                          <div className="flex items-center gap-1">
                            <div className={`w-2 h-2 rounded-full ${getMoodColor(selectedEntry.mood_level)}`} />
                            <span>Mood {selectedEntry.mood_level}/10</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" />
                            <span>Energy {selectedEntry.energy_level}/10</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span>{selectedEntry.sleep_hours}h sleep</span>
                          </div>
                        </div>

                        {/* Tags */}
                        {selectedEntry.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {selectedEntry.tags.map(tag => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>

                      <Separator />

                      {/* AI Response */}
                      {mockAIResponses[selectedEntry.id as keyof typeof mockAIResponses] && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
                              <MessageCircle className="w-3 h-3 text-primary" />
                            </div>
                            <span className="text-sm font-medium">Pulse's Response</span>
                            <span className="text-xs text-muted-foreground ml-auto">
                              {mockAIResponses[selectedEntry.id as keyof typeof mockAIResponses].timestamp}
                            </span>
                          </div>
                          
                          <p className="text-sm text-muted-foreground leading-relaxed pl-8">
                            {mockAIResponses[selectedEntry.id as keyof typeof mockAIResponses].comment}
                          </p>
                          
                          {/* Reactions */}
                          <div className="flex items-center gap-2 pl-8">
                            {mockAIResponses[selectedEntry.id as keyof typeof mockAIResponses].reactions.map((reaction, index) => (
                              <span key={index} className="text-lg">{reaction}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2 pt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/journal/${selectedEntry.id}`)}
                          className="flex-1"
                        >
                          View Full Entry
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate('/insights')}
                        >
                          <TrendingUp className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <BookOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No journal entry for this day</p>
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-3"
                        onClick={() => navigate('/journal')}
                      >
                        Create Entry
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          /* List View */
          <div className="space-y-4">
            {journalEntries.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="text-lg font-semibold mb-2">No entries yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Start your wellness journey by creating your first entry
                  </p>
                  <Button onClick={() => navigate('/journal')}>
                    Create First Entry
                  </Button>
                </CardContent>
              </Card>
            ) : (
              journalEntries.map((entry) => (
                <Card key={entry.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          {new Date(entry.created_at).toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric'
                          })}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getMoodColor(entry.mood_level)}`} />
                          <span className="text-xs text-muted-foreground">
                            Mood {entry.mood_level}/10
                          </span>
                          
                          {/* Entry Actions Dropdown */}
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0"
                                onClick={(e) => e.stopPropagation()} // Prevent card click
                              >
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/journal/${entry.id}`);
                                }}
                              >
                                <Edit className="h-4 w-4 mr-2" />
                                View/Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCopyEntry(entry);
                                }}
                              >
                                <Copy className="h-4 w-4 mr-2" />
                                Copy text
                              </DropdownMenuItem>
                              <DropdownMenuItem 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteEntry(entry);
                                }}
                                className="text-red-600 focus:text-red-600"
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete entry
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                      
                      <p className="text-sm leading-relaxed line-clamp-3">
                        {entry.content}
                      </p>
                      
                      {entry.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {entry.tags.slice(0, 3).map(tag => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {entry.tags.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{entry.tags.length - 3}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        )}
      </main>

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

export default History; 