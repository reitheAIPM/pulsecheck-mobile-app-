import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  User,
  Brain,
  Settings,
  Bell,
  Shield,
  HelpCircle,
  ChevronRight,
  Edit3,
  Save,
  X,
  Sparkles,
  RefreshCw,
  Crown,
  Trash2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import AITeamManager from "@/components/PersonaSelector";
import PatternInsights from "@/components/PatternInsights";
import JournalHistory from "@/components/JournalHistory";
import { apiService, UserPatternSummary, PersonaRecommendation } from "@/services/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { StatusIndicator } from "@/components/ui/loading-states";

const Profile = () => {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    name: "Alex Chen",
    role: "Senior Software Engineer",
    company: "TechCorp",
    workStyle:
      "I work best in focused blocks and tend to overthink problems. I value work-life balance but sometimes struggle with setting boundaries.",
    triggers: "Heavy meeting days, unclear requirements, tight deadlines",
    goals:
      "Better stress management, improved work-life balance, more confident decision making",
  });

  const [aiSettings, setAiSettings] = useState({
    responseDelay: true,
    personalizedResponses: true,
    moodTracking: true,
    weeklyInsights: true,
    encouragingTone: true,
  });

  const [userPatterns, setUserPatterns] = useState<UserPatternSummary | null>(null);
  const [personas, setPersonas] = useState<PersonaRecommendation[]>([]);
  const [selectedPersona, setSelectedPersona] = useState("pulse");
  const [loadingPatterns, setLoadingPatterns] = useState(false);
  const [loadingPersonas, setLoadingPersonas] = useState(false);
  const [refreshingPatterns, setRefreshingPatterns] = useState(false);
  const [adaptiveAIEnabled, setAdaptiveAIEnabled] = useState(true);
  const [patternAnalysisEnabled, setPatternAnalysisEnabled] = useState(true);
  const [premiumEnabled, setPremiumEnabled] = useState(false);
  const [premiumToggleLoading, setPremiumToggleLoading] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);
  const [loadingSubscription, setLoadingSubscription] = useState(true);

  // State for reset journal functionality
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);
  const [isResettingJournal, setIsResettingJournal] = useState(false);
  const [resetError, setResetError] = useState<string | null>(null);
  const [resetSuccess, setResetSuccess] = useState<string | null>(null);
  
  // Debug section state
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');
  const [originalProfile, setOriginalProfile] = useState({
    name: "Alex Chen",
    role: "Senior Software Engineer",
    company: "TechCorp",
    workStyle:
      "I work best in focused blocks and tend to overthink problems. I value work-life balance but sometimes struggle with setting boundaries.",
    triggers: "Heavy meeting days, unclear requirements, tight deadlines",
    goals:
      "Better stress management, improved work-life balance, more confident decision making",
  });

  // Mock user ID - in a real app, this would come from authentication
  const userId = "user_123";

  // Mock user data
  const userData = {
    name: "Alex Chen",
    email: "alex@example.com",
    memberSince: "December 2024",
    totalEntries: 24,
    currentStreak: 7,
    isPremium: false
  };

  useEffect(() => {
    loadUserPatterns();
    loadPersonas();
    loadSubscriptionStatus();
    testApiConnection();
  }, []);

  const testApiConnection = async () => {
    try {
      const isConnected = await apiService.testConnection();
      setApiStatus(isConnected ? 'connected' : 'error');
    } catch (error) {
      console.error('API connection test failed:', error);
      setApiStatus('error');
    }
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

  const loadUserPatterns = async () => {
    setLoadingPatterns(true);
    try {
      const patterns = await apiService.getUserPatterns(userId);
      setUserPatterns(patterns);
    } catch (error) {
      console.error('Failed to load user patterns:', error);
      // Use mock data for demonstration
      setUserPatterns({
        writing_style: "analytical",
        common_topics: ["work", "stress", "productivity", "goals"],
        mood_trends: {
          mood: 6.2,
          energy: 5.8,
          stress: 6.5
        },
        interaction_preferences: {
          prefers_questions: true,
          prefers_validation: true,
          prefers_advice: false
        },
        response_preferences: {
          length: "medium",
          style: "supportive"
        },
        pattern_confidence: 0.75,
        entries_analyzed: 24,
        last_updated: new Date().toISOString()
      });
    } finally {
      setLoadingPatterns(false);
    }
  };

  const loadPersonas = async () => {
    setLoadingPersonas(true);
    try {
      const availablePersonas = await apiService.getAvailablePersonas(userId);
      setPersonas(availablePersonas);
      
      // Set default persona to the first recommended one, or fallback to "pulse"
      const recommendedPersona = availablePersonas.find(p => p.recommended);
      if (recommendedPersona) {
        setSelectedPersona(recommendedPersona.persona_id);
      }
    } catch (error) {
      console.error('Failed to load personas:', error);
      // Use fallback personas
      setPersonas([
        {
          persona_id: "pulse",
          persona_name: "Pulse",
          description: "Your emotionally intelligent wellness companion",
          recommended: true,
          available: true,
          requires_premium: false,
          times_used: 15,
          recommendation_reason: "Perfect for emotional support and wellness insights"
        },
        {
          persona_id: "sage",
          persona_name: "Sage",
          description: "Wise mentor for strategic life guidance",
          recommended: false,
          available: premiumEnabled,
          requires_premium: true,
          times_used: premiumEnabled ? 3 : 0,
          recommendation_reason: "Great for long-term planning and wisdom"
        },
        {
          persona_id: "spark",
          persona_name: "Spark",
          description: "Energetic motivator for creativity and action",
          recommended: false,
          available: premiumEnabled,
          requires_premium: true,
          times_used: premiumEnabled ? 1 : 0,
          recommendation_reason: "Perfect for boosting motivation and creative thinking"
        },
        {
          persona_id: "anchor",
          persona_name: "Anchor",
          description: "Steady presence for stability and grounding",
          recommended: false,
          available: premiumEnabled,
          requires_premium: true,
          times_used: premiumEnabled ? 2 : 0,
          recommendation_reason: "Ideal for finding balance and inner stability"
        }
      ]);
    } finally {
      setLoadingPersonas(false);
    }
  };

  const loadSubscriptionStatus = async () => {
    setLoadingSubscription(true);
    try {
      const status = await apiService.getSubscriptionStatus(userId);
      setSubscriptionStatus(status);
      setPremiumEnabled(status.beta_premium_enabled);
    } catch (error) {
      console.error('Failed to load subscription status:', error);
      // Use fallback status
      setSubscriptionStatus({
        tier: 'free',
        is_premium_active: false,
        is_beta_tester: true, // Default to beta tester for development
        beta_premium_enabled: false,
        available_personas: ['pulse'],
        ai_requests_today: 0,
        daily_limit: 10,
        beta_mode: true,
        premium_features: {
          advanced_personas: false,
          pattern_insights: false,
          unlimited_history: false,
          priority_support: false
        }
      });
    } finally {
      setLoadingSubscription(false);
    }
  };

  const refreshPatterns = async () => {
    setRefreshingPatterns(true);
    try {
      await apiService.refreshUserPatterns(userId);
      await loadUserPatterns();
    } catch (error) {
      console.error('Failed to refresh patterns:', error);
    } finally {
      setRefreshingPatterns(false);
    }
  };

  const handlePremiumToggle = async (enabled: boolean) => {
    setPremiumToggleLoading(true);
    try {
      const result = await apiService.toggleBetaPremium({
        user_id: userId,
        enabled: enabled
      });
      
      if (result.success) {
        setPremiumEnabled(enabled);
        setSubscriptionStatus(result.subscription_status);
        console.log(result.message);
        
        // Reload personas with new premium status
        await loadPersonas();
      } else {
        console.error('Failed to toggle premium:', result.error);
      }
    } catch (error) {
      console.error('Failed to toggle premium:', error);
      // Fallback to mock behavior for development
      setPremiumEnabled(enabled);
      console.log(`Premium features ${enabled ? 'enabled' : 'disabled'} (Free during beta)`);
    } finally {
      setPremiumToggleLoading(false);
    }
  };

  const handleSave = () => {
    // In real app, save to backend
    setIsEditing(false);
  };

  const handleCancel = () => {
    setProfile(originalProfile);
    setIsEditing(false);
  };

  const handleResetJournal = async () => {
    setIsResettingJournal(true);
    setResetError(null);
    setResetSuccess(null);

    try {
      // Call the reset journal API with confirmation
      const result = await apiService.resetJournal(userId);
      
      if (result.deleted_count >= 0) {
        setResetSuccess(result.message);
        // Clear any cached journal data
        localStorage.removeItem('lastAIResponse');
        localStorage.removeItem('journalEntries');
        
        // Refresh user patterns since journal is reset
        await loadUserPatterns();
        
        setIsResetDialogOpen(false);
      } else {
        setResetError('Failed to reset journal. Please try again.');
      }
    } catch (error: any) {
      console.error('Error resetting journal:', error);
      
      // Handle specific error messages
      if (error.response?.data?.detail) {
        setResetError(error.response.data.detail);
      } else if (error.message) {
        setResetError(error.message);
      } else {
        setResetError('Failed to reset journal. Please try again.');
      }
    } finally {
      setIsResettingJournal(false);
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <User className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">Profile</h1>
                <p className="text-sm text-muted-foreground">
                  Your wellness journey settings
                </p>
              </div>
            </div>
            {!isEditing ? (
              <>
                {premiumEnabled && (
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-700 border-yellow-300">
                    <Crown className="w-3 h-3 mr-1" />
                    Premium Active
                  </Badge>
                )}
              </>
            ) : (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  <X className="w-4 h-4" />
                </Button>
                <Button size="sm" onClick={handleSave} className="gap-2">
                  <Save className="w-4 h-4" />
                  Save
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* User Info */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">{userData.name}</h2>
                  <p className="text-sm text-muted-foreground">{userData.email}</p>
                </div>
              </div>
              {userData.isPremium && (
                <Badge variant="secondary" className="gap-1">
                  <Crown className="w-3 h-3" />
                  Premium
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">{userData.totalEntries}</div>
                <div className="text-xs text-muted-foreground">Entries</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">{userData.currentStreak}</div>
                <div className="text-xs text-muted-foreground">Day Streak</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {userPatterns ? Math.round(userPatterns.pattern_confidence * 100) : 75}%
                </div>
                <div className="text-xs text-muted-foreground">AI Match</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Profile Info */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <User className="w-4 h-4" />
                About You
              </CardTitle>
              {!isEditing && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                  className="gap-2"
                >
                  <Edit3 className="w-4 h-4" />
                  Edit
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={profile.name}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, name: e.target.value }))
                }
                disabled={!isEditing}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Input
                  id="role"
                  value={profile.role}
                  onChange={(e) =>
                    setProfile((prev) => ({ ...prev, role: e.target.value }))
                  }
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  value={profile.company}
                  onChange={(e) =>
                    setProfile((prev) => ({ ...prev, company: e.target.value }))
                  }
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="workStyle">Work Style & Preferences</Label>
              <Textarea
                id="workStyle"
                value={profile.workStyle}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, workStyle: e.target.value }))
                }
                disabled={!isEditing}
                placeholder="Tell Pulse about how you work best, your preferences, and what helps you be productive..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="triggers">Stress Triggers</Label>
              <Textarea
                id="triggers"
                value={profile.triggers}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, triggers: e.target.value }))
                }
                disabled={!isEditing}
                placeholder="What situations or work conditions tend to stress you out?"
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="goals">Goals & Aspirations</Label>
              <Textarea
                id="goals"
                value={profile.goals}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, goals: e.target.value }))
                }
                disabled={!isEditing}
                placeholder="What do you hope to achieve through reflection and journaling?"
                rows={2}
              />
            </div>
          </CardContent>
        </Card>

        {/* AI Settings */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              AI Companion Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Adaptive AI</div>
                <div className="text-xs text-muted-foreground">
                  Personalize responses based on your patterns
                </div>
              </div>
              <Switch
                checked={adaptiveAIEnabled}
                onCheckedChange={setAdaptiveAIEnabled}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Pattern Analysis</div>
                <div className="text-xs text-muted-foreground">
                  Learn from your writing style and preferences
                </div>
              </div>
              <Switch
                checked={patternAnalysisEnabled}
                onCheckedChange={setPatternAnalysisEnabled}
              />
            </div>
          </CardContent>
        </Card>

        {/* Persona Selection */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              AI Personas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <AITeamManager
              userId={userId}
              premiumEnabled={premiumEnabled}
              onPremiumToggle={handlePremiumToggle}
              personas={personas}
              isLoading={loadingPersonas || premiumToggleLoading}
            />
          </CardContent>
        </Card>

        {/* Pattern Insights */}
        {userPatterns && (
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Your Patterns
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={refreshPatterns}
                  disabled={refreshingPatterns}
                  className="gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${refreshingPatterns ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <PatternInsights patterns={userPatterns} isLoading={loadingPatterns} />
            </CardContent>
          </Card>
        )}

        {/* Account Info */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Member since</span>
              <span className="text-muted-foreground">{userData.memberSince}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Plan</span>
              <span className="text-muted-foreground">
                {userData.isPremium ? 'Premium' : 'Free'}
              </span>
            </div>
            {!userData.isPremium && (
              <div className="pt-2 border-t">
                <Button variant="outline" className="w-full gap-2">
                  <Crown className="w-4 h-4" />
                  Upgrade to Premium
                </Button>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  Unlock all AI personas and advanced insights
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Data & Privacy */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Data & Privacy</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm text-muted-foreground">
              Your journal entries are encrypted and stored securely. We never share your personal data and only access it for technical support when you explicitly request help.
            </div>
            <div className="flex flex-col gap-2">
              <Button variant="outline" size="sm">
                Export Data
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate("/privacy")}
              >
                Privacy Policy
              </Button>
              
              {/* Reset Journal Button with Confirmation Dialog */}
              <AlertDialog open={isResetDialogOpen} onOpenChange={setIsResetDialogOpen}>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" size="sm" className="gap-2">
                    <Trash2 className="w-4 h-4" />
                    Reset Journal
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Reset Your Journal?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete all your journal entries and clear your AI patterns. 
                      This action cannot be undone. Are you sure you want to continue?
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel disabled={isResettingJournal}>
                      Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction 
                      onClick={handleResetJournal}
                      disabled={isResettingJournal}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      {isResettingJournal ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Resetting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4 mr-2" />
                          Yes, Reset Journal
                        </>
                      )}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
            
            {/* Reset Journal Status Messages */}
            {resetSuccess && (
              <Alert className="mt-4 border-green-200 bg-green-50">
                <AlertTitle className="text-green-800">Success!</AlertTitle>
                <AlertDescription className="text-green-700">
                  {resetSuccess}
                </AlertDescription>
              </Alert>
            )}
            
            {resetError && (
              <Alert className="mt-4 border-red-200 bg-red-50">
                <AlertTitle className="text-red-800">Error</AlertTitle>
                <AlertDescription className="text-red-700">
                  {resetError}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Settings Menu */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Settings
          </h2>

          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                <button className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <Bell className="w-4 h-4" />
                    <span className="text-sm font-medium">Notifications</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>

                <button 
                  className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
                  onClick={() => navigate("/privacy")}
                >
                  <div className="flex items-center gap-3">
                    <Shield className="w-4 h-4" />
                    <span className="text-sm font-medium">
                      Privacy & Security
                    </span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>

                <button className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <HelpCircle className="w-4 h-4" />
                    <span className="text-sm font-medium">Help & Support</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Note */}
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-4 text-center">
            <div className="text-sm text-primary/80">
              🔒 Your data is securely encrypted and stored. Pulse uses your journal entries to provide personalized AI insights and never shares your information with third parties.
            </div>
          </CardContent>
        </Card>

        {/* Beta Testing Section */}
        {subscriptionStatus?.is_beta_tester && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Crown className="w-4 h-4" />
                Beta Testing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Beta Status */}
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-blue-300">
                    Beta Tester
                  </Badge>
                  <span className="text-sm font-medium">Premium Features</span>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={premiumEnabled}
                    onCheckedChange={handlePremiumToggle}
                    disabled={premiumToggleLoading}
                  />
                  {premiumToggleLoading && (
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  )}
                </div>
              </div>

              {/* Usage Analytics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-muted/30 rounded-lg">
                  <div className="text-lg font-bold text-primary">
                    {subscriptionStatus?.ai_requests_today || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">AI Requests Today</div>
                </div>
                <div className="text-center p-3 bg-muted/30 rounded-lg">
                  <div className="text-lg font-bold text-green-600">
                    {subscriptionStatus?.daily_limit || 50}
                  </div>
                  <div className="text-xs text-muted-foreground">Daily Limit</div>
                </div>
              </div>

              {/* Available Features */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Available Features</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${subscriptionStatus?.premium_features?.advanced_personas ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span>Advanced Personas</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${subscriptionStatus?.premium_features?.pattern_insights ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span>Pattern Insights</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${subscriptionStatus?.premium_features?.unlimited_history ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span>Unlimited History</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${subscriptionStatus?.premium_features?.priority_support ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span>Priority Support</span>
                  </div>
                </div>
              </div>

              {/* Beta Mode Notice */}
              {subscriptionStatus?.beta_mode && (
                <Alert>
                  <Crown className="h-4 w-4" />
                  <AlertTitle>Free Premium During Beta</AlertTitle>
                  <AlertDescription>
                    All premium features are free for beta testers. Help us improve PulseCheck!
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* Persona Management */}

        {/* Debug Section */}
        <Card className="border-dashed border-muted-foreground/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">For Debug</CardTitle>
          </CardHeader>
          <CardContent>
            <StatusIndicator
              status={apiStatus === 'loading' ? 'loading' : apiStatus === 'connected' ? 'success' : 'error'}
              message={getStatusMessage()}
              onRetry={apiStatus === 'error' ? testApiConnection : undefined}
              className="mb-2"
            />
            <div className="text-xs text-muted-foreground space-y-1">
              <div>Environment: <span className="font-mono">Development</span></div>
              <div>Version: <span className="font-mono">v1.0.0-beta</span></div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Profile;
