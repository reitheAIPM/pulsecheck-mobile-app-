import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Plus, Heart, Sparkles, Brain, Crown, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { JournalCard } from "@/components/JournalCard";
import { StatusIndicator, LoadingCard, EmptyState } from "@/components/ui/loading-states";
import FollowUpPrompts from "@/components/FollowUpPrompts";
import { apiService } from "@/services/api";
import { toast } from "@/hooks/use-toast";
import { authService } from "@/services/authService";

// No mock data - using real journal entries from API

const Index = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [entries, setEntries] = useState([]);
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoadingEntries, setIsLoadingEntries] = useState(false);
  const [premiumEnabled, setPremiumEnabled] = useState(false);
  const [hasNotifications, setHasNotifications] = useState(false);
  const [shouldReloadEntries, setShouldReloadEntries] = useState(false);
  
  // Get authenticated user ID
  const [userId, setUserId] = useState<string | null>(null);
  
  useEffect(() => {
    const getUserId = async () => {
      console.log('🔍 Checking user authentication status...');
      // Get user from Supabase authentication
      const { user, error } = await authService.getCurrentUser();
      
      if (user) {
        console.log('✅ User authenticated:', user.id, user.email);
        setUserId(user.id);
      } else {
        console.log('❌ No authenticated user found:', error);
        setUserId(null);
      }
    };
    getUserId();
  }, []);
  // Check for celebration when component mounts and reload entries
  useEffect(() => {
    if (searchParams.get('newEntry') === 'true') {
      toast({
        title: "🎉 Reflection saved!",
        description: "Your journal entry has been saved successfully. Great job taking time for yourself!",
        duration: 4000,
      });
      
      // Clean up the URL parameter
      setSearchParams({});
      
      // Trigger entry reload
      setShouldReloadEntries(true);
    }
  }, [searchParams, setSearchParams, apiStatus, userId]);

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

  // Effect to handle entry reloading when flag is set
  useEffect(() => {
    if (shouldReloadEntries && apiStatus === 'connected' && userId) {
      const reloadEntries = async () => {
        try {
          console.log('🔄 Reloading entries after new entry creation');
          let realEntries = await apiService.getJournalEntries();
          
          const transformedEntries = realEntries.map(entry => ({
            id: entry.id,
            content: entry.content,
            mood: entry.mood_level,
            timestamp: entry.created_at,
          }));
          setEntries(transformedEntries);
          console.log('✅ Successfully reloaded', realEntries.length, 'journal entries after creation');
        } catch (error) {
          console.error('❌ Failed to reload entries after creation:', error);
        }
      };
      
      reloadEntries();
      setShouldReloadEntries(false); // Reset the flag
    }
  }, [shouldReloadEntries, apiStatus, userId]);

  // Add effect to reload entries when returning to this page (but less aggressively)
  useEffect(() => {
    let lastReloadTime = 0;
    const RELOAD_COOLDOWN = 30000; // 30 seconds cooldown between reloads

    const handleVisibilityChange = () => {
      const now = Date.now();
      // Only reload if page becomes visible, we're connected, have a user, and enough time has passed
      if (document.visibilityState === 'visible' && 
          apiStatus === 'connected' && 
          userId && 
          (now - lastReloadTime) > RELOAD_COOLDOWN) {
        lastReloadTime = now;
        loadRealEntries();
      }
    };

    // Remove aggressive focus reload - only use visibility change
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [apiStatus, userId]); // Dependencies on apiStatus and userId

  const loadRealEntries = async () => {
    if (!userId) {
      console.log('No user ID available, skipping entry load');
      return;
    }
    
    setIsLoadingEntries(true);
    try {
      console.log('🔄 Loading journal entries for user:', userId);
      
      // Ensure we have a valid auth token before making the request
      const token = authService.getAuthToken();
      if (!token) {
        console.warn('⚠️ No auth token available, trying to refresh...');
        const freshToken = await authService.getAuthTokenAsync();
        if (!freshToken) {
          throw new Error('Authentication required. Please sign in again.');
        }
      }
      
      // Load journal entries
      let realEntries = await apiService.getJournalEntries();
      
      console.log('📥 Received journal entries:', realEntries.length, 'entries');
      
      // Load AI responses using our bypass endpoint that works
      let aiResponsesData = null;
      try {
        console.log('🤖 Loading AI responses from bypass endpoint...');
        const response = await fetch(`https://pulsecheck-mobile-app-production.up.railway.app/api/v1/frontend-fix/ai-responses/${userId}`);
        if (response.ok) {
          aiResponsesData = await response.json();
          console.log('✅ AI responses loaded:', aiResponsesData.ai_responses?.length || 0, 'responses');
        }
      } catch (error) {
        console.log('⚠️ Could not load AI responses from bypass endpoint');
      }
      
      // Map AI responses by journal entry ID for quick lookup
      const aiResponsesByEntryId = {};
      if (aiResponsesData && aiResponsesData.ai_responses) {
        aiResponsesData.ai_responses.forEach(aiResp => {
          aiResponsesByEntryId[aiResp.journal_entry_id] = aiResp;
        });
      }
      
      // Transform the entries to match the expected format for the UI
      const transformedEntries = realEntries.map(entry => ({
        id: entry.id,
        content: entry.content,
        mood: entry.mood_level,
        timestamp: entry.created_at,
        // Include AI response if it exists
        aiResponse: aiResponsesByEntryId[entry.id] ? {
          comments: [aiResponsesByEntryId[entry.id].response],
          timestamp: aiResponsesByEntryId[entry.id].created_at,
          emoji: "🤖"
        } : undefined
      }));
      
      setEntries(transformedEntries);
      
      if (realEntries.length === 0) {
        console.log('ℹ️ No journal entries found for user');
        toast({
          title: "No entries yet",
          description: "Start your wellness journey by creating your first entry!",
          duration: 3000,
        });
      } else {
        const entriesWithAICount = transformedEntries.filter(e => e.aiResponse).length;
        console.log('✅ Successfully loaded', realEntries.length, 'journal entries with', entriesWithAICount, 'AI responses');
        
        if (entriesWithAICount > 0) {
          toast({
            title: "AI responses loaded!",
            description: `Found ${entriesWithAICount} AI responses to your journal entries`,
            duration: 4000,
          });
        }
      }
    } catch (error) {
      console.error('❌ Failed to load journal entries:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      // Handle authentication errors specifically
      if (error.response?.status === 401) {
        toast({
          title: "Authentication required",
          description: "Please sign in again to view your entries.",
          variant: "destructive",
          duration: 5000,
        });
        // Clear invalid auth state
        authService.signOut();
        window.location.href = '/auth';
      } else {
        toast({
          title: "Loading failed",
          description: "Unable to load your entries. Please try refreshing.",
          variant: "destructive",
          duration: 3000,
        });
      }
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
