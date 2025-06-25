import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Heart, Sparkles, Brain, Crown, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { JournalCard } from "@/components/JournalCard";
import { StatusIndicator, LoadingCard, EmptyState } from "@/components/ui/loading-states";
import FollowUpPrompts from "@/components/FollowUpPrompts";
import { apiService } from "@/services/api";
import { toast } from "@/hooks/use-toast";
import { authService } from "@/services/authService";

// Mock data for development
const mockEntries = [
  {
    id: "1",
    content:
      "Today was one of those days where everything felt overwhelming. The deadline for the project is approaching and I can feel the pressure building. Sometimes I wonder if I'm pushing myself too hard. But there's also this part of me that feels like I need to prove myself...",
    mood: 4,
    timestamp: "2024-01-15T10:30:00Z",
    aiResponse: {
      emoji: "🤗",
      comments: [
        "It sounds like you're carrying a lot right now. That pressure you're feeling is so valid.",
        "Remember that proving yourself doesn't have to come at the cost of your wellbeing. What's one small thing you could do today to ease that load?",
      ],
      timestamp: "2024-01-15T13:45:00Z",
    },
  },
  {
    id: "2",
    content:
      "Had a really good conversation with my teammate today. We actually figured out a solution to the problem that's been bugging us for weeks. Feeling pretty accomplished right now! Sometimes collaboration really does make all the difference.",
    mood: 8,
    timestamp: "2024-01-14T16:22:00Z",
    aiResponse: {
      emoji: "✨",
      comments: [
        "That spark of collaboration hitting just right - there's nothing quite like it!",
        "It's beautiful how sharing the mental load can suddenly make complex things feel simple again.",
      ],
      timestamp: "2024-01-14T19:30:00Z",
    },
  },
  {
    id: "3",
    content:
      "Feeling pretty burned out lately. The constant context switching between meetings and coding is exhausting. I miss having longer stretches of deep work time.",
    mood: 3,
    timestamp: "2024-01-13T14:15:00Z",
  },
];

const Index = () => {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoadingEntries, setIsLoadingEntries] = useState(false);
  const [premiumEnabled, setPremiumEnabled] = useState(false);
  const [hasNotifications, setHasNotifications] = useState(false);
  
  // Get authenticated user ID
  const [userId, setUserId] = useState<string | null>(null);
  
  useEffect(() => {
    const getUserId = async () => {
      // The authToken IS the user ID in our mock auth system
      const authToken = localStorage.getItem('authToken');
      if (authToken) {
        setUserId(authToken);
      } else {
        // Try to get user from authService as fallback
        const { user } = await authService.getCurrentUser();
        setUserId(user?.id || null);
      }
    };
    getUserId();
  }, []);

  useEffect(() => {
    // Test API connection on component mount
    const testApiConnection = async () => {
      try {
        const isConnected = await apiService.testConnection();
        setApiStatus(isConnected ? 'connected' : 'error');
        
        if (isConnected) {
          toast({
            title: "Connected to PulseCheck",
            description: "Your wellness companion is ready to support you.",
            duration: 3000,
          });
          
          // Load real journal entries when connected and user ID is available
          if (userId) {
            loadRealEntries();
          }
        }
      } catch (error) {
        console.error('API connection test failed:', error);
        setApiStatus('error');
        toast({
          title: "Connection Issue",
          description: "Unable to connect to PulseCheck. You can still use the app offline.",
          variant: "destructive",
          duration: 5000,
        });
      }
    };

    testApiConnection();
  }, [userId]); // Add userId as dependency

  // Add effect to reload entries when returning to this page
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && apiStatus === 'connected' && userId) {
        // Reload entries when page becomes visible and we're connected
        loadRealEntries();
      }
    };

    // Also reload when the page gains focus
    const handleFocus = () => {
      if (apiStatus === 'connected' && userId) {
        loadRealEntries();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [apiStatus, userId]); // Dependencies on apiStatus and userId

  const loadRealEntries = async () => {
    if (!userId) {
      console.log('No user ID available, skipping entry load');
      return;
    }
    
    setIsLoadingEntries(true);
    try {
      // Load journal entries
      let realEntries = await apiService.getJournalEntries();
      
      // Transform the entries to match the expected format
      const transformedEntries = realEntries.map(entry => ({
        id: entry.id,
        content: entry.content,
        mood: entry.mood_level,
        timestamp: entry.created_at,
        // AI response will be added later when we implement that feature
      }));
      setEntries(transformedEntries);
      
      if (realEntries.length === 0) {
        toast({
          title: "No entries yet",
          description: "Start your wellness journey by creating your first entry!",
          duration: 3000,
        });
      }
    } catch (error) {
      console.error('Failed to load real entries:', error);
      console.error('Error details:', error.response?.data || error.message);
      toast({
        title: "Loading failed",
        description: "Unable to load your entries. Please try refreshing.",
        variant: "destructive",
        duration: 3000,
      });
      // Don't set mock data - let empty state show instead
    } finally {
      setIsLoadingEntries(false);
    }
  };

  const handlePulseClick = (entryId: string) => {
    navigate(`/pulse/${entryId}`);
  };

  const handleEntryDeleted = (deletedEntryId: string) => {
    // Remove the deleted entry from the local state
    setEntries(prevEntries => prevEntries.filter(entry => entry.id !== deletedEntryId));
  };

  const handleNewEntry = () => {
    navigate("/journal"); // Fix: Changed from "/new-entry" to "/journal"
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Simulate refresh delay for better UX
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Test API connection again
      const isConnected = await apiService.testConnection();
      setApiStatus(isConnected ? 'connected' : 'error');
      
      if (isConnected) {
        toast({
          title: "Refreshed",
          description: "Connection restored successfully.",
          duration: 2000,
        });
      }
    } catch (error) {
      console.error('Refresh failed:', error);
      setApiStatus('error');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleLoadEntries = async () => {
    await loadRealEntries();
  };

  const getStatusMessage = () => {
    switch (apiStatus) {
      case 'loading':
        return 'Testing connection...';
      case 'connected':
        return 'Backend connected';
      case 'error':
        return 'Backend disconnected';
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-6">
      {/* Header - Mobile Optimized */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl xl:max-w-4xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Brain className="w-5 h-5 md:w-6 md:h-6 text-primary" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-lg md:text-xl lg:text-2xl font-semibold">PulseCheck</h1>
                  {premiumEnabled && (
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-700 border-yellow-300 text-xs">
                      <Crown className="w-3 h-3 mr-1" />
                      Premium
                    </Badge>
                  )}
                </div>
                <p className="text-sm md:text-base text-muted-foreground">
                  Your reflection space
                </p>
              </div>
            </div>

            <Button 
              onClick={handleNewEntry} 
              size="lg"
              className="gap-2 transition-all duration-200 hover:scale-105 active:scale-95 min-h-[44px] px-4 md:px-6"
            >
              <Plus className="w-4 h-4 md:w-5 md:h-5" />
              <span className="hidden sm:inline">Reflect</span>
              <span className="sm:hidden">New</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content - Responsive Layout */}
      <main className="w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl xl:max-w-4xl mx-auto px-4 sm:px-6 py-6">
        {/* Welcome Message - Mobile Optimized */}
        <div className="text-center mb-6 lg:mb-8">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-2 md:px-4 md:py-2 rounded-lg text-sm md:text-base font-medium mb-3 md:mb-4 animate-fade-in">
            <Sparkles className="w-4 h-4 md:w-5 md:h-5" />
            Welcome back
          </div>
          <p className="text-muted-foreground text-sm md:text-base lg:text-lg max-w-sm md:max-w-md mx-auto leading-relaxed">
            Take a moment to check in with yourself. How are you feeling today?
          </p>
        </div>

        {/* Smart Follow-Up Prompts - Better Mobile Layout */}
        {entries.length > 0 && (
          <div className="mb-6 lg:mb-8">
            <FollowUpPrompts
              userId={userId}
              recentEntries={entries.map(entry => ({
                id: entry.id,
                content: entry.content,
                mood_level: entry.mood,
                stress_level: entry.stress || 5,
                created_at: entry.timestamp,
                tags: entry.tags || []
              }))}
              onPromptSelect={(prompt) => {
                navigate(`/journal?prompt=${encodeURIComponent(prompt.prompt)}`);
              }}
            />
          </div>
        )}

        {/* Quick Action - Touch-Friendly */}
        <div className="mb-6 lg:mb-8">
          <Button
            onClick={handleNewEntry}
            variant="outline"
            size="lg"
            className="w-full min-h-[56px] md:min-h-[64px] border-2 border-dashed hover:bg-muted/50 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] group"
          >
            <div className="flex items-center gap-3 md:gap-4">
              <Plus className="w-5 h-5 md:w-6 md:h-6 transition-transform group-hover:rotate-90 duration-200" />
              <span className="text-sm md:text-base lg:text-lg">What's on your mind today?</span>
            </div>
          </Button>
        </div>

        {/* Journal Feed - Responsive Grid */}
        <div className="space-y-6 lg:space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-2 text-sm md:text-base text-calm-600">
              <Heart className="w-4 h-4 md:w-5 md:h-5" />
              <span>Your recent reflections</span>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Debug Info - Responsive */}
              <div className="text-xs md:text-sm text-muted-foreground">
                Status: {apiStatus} | User: {userId ? 'Yes' : 'No'}
              </div>
              
              {apiStatus === 'connected' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLoadEntries}
                  disabled={isLoadingEntries}
                  className="h-9 md:h-10 px-3 md:px-4 text-xs md:text-sm"
                >
                  {isLoadingEntries ? 'Loading...' : 'Refresh'}
                </Button>
              )}
            </div>
          </div>

          {/* Manual Load Button - Mobile Friendly */}
          {apiStatus === 'connected' && entries.length === 0 && !isLoadingEntries && (
            <div className="text-center py-6 md:py-8">
              <Button
                onClick={handleLoadEntries}
                variant="outline"
                size="lg"
                className="gap-2 min-h-[44px]"
              >
                <Heart className="w-4 h-4 md:w-5 md:h-5" />
                Load My Entries
              </Button>
              <p className="text-xs md:text-sm text-muted-foreground mt-3 md:mt-4">
                Debug: API connected, user ID: {userId}, entries: {entries.length}
              </p>
            </div>
          )}

          {/* Content Area - Responsive Layout */}
          {isLoadingEntries ? (
            <div className="space-y-4 md:space-y-6">
              {[1, 2, 3].map((i) => (
                <LoadingCard key={i} lines={4} />
              ))}
            </div>
          ) : entries.length > 0 ? (
            <div className="space-y-4 md:space-y-6 lg:space-y-8">
              {entries.map((entry, index) => (
                <div
                  key={entry.id}
                  className="animate-fade-in"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <JournalCard
                    entry={entry}
                    onPulseClick={handlePulseClick}
                    onEntryDeleted={handleEntryDeleted}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 md:py-12">
              <EmptyState
                icon={<Heart className="w-8 h-8 md:w-10 md:h-10 lg:w-12 lg:h-12 text-pulse-500" />}
                title="Start your reflection journey"
                description="Your first journal entry is just a click away. Take a moment to check in with yourself."
                action={{
                  label: "Write your first reflection",
                  onClick: handleNewEntry,
                }}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Index;
