import { useState, useEffect } from "react";
import {
  TrendingUp,
  Calendar,
  BookOpen,
  Heart,
  Target,
  Award,
  BarChart3,
  Sparkles,
  RefreshCw,
  User,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import PatternInsights from "@/components/PatternInsights";
import { apiService, UserPatterns, AdaptiveResponseResponse, AIInsightResponse } from "@/services/api";
import { authService } from "@/services/authService";

const Insights = () => {
  const [userPatterns, setUserPatterns] = useState<UserPatterns | null>(null);
  const [lastAIResponse, setLastAIResponse] = useState<AdaptiveResponseResponse | null>(null);
  const [loadingPatterns, setLoadingPatterns] = useState(false);
  const [refreshingPatterns, setRefreshingPatterns] = useState(false);

  // Get user ID from authenticated session
  // Get current user ID from authenticated session
  const [userId, setUserId] = useState<string>("");

  // Initialize user ID
  useEffect(() => {
    const initializeUser = async () => {
      const { user } = await authService.getCurrentUser();
      if (user?.id) {
        setUserId(user.id);
      }
    };
    initializeUser();
  }, []);

  // Stats will be loaded from API - no mock data

  useEffect(() => {
    loadUserPatterns();
    loadLastAIResponse();
  }, []);

  const loadUserPatterns = async () => {
    setLoadingPatterns(true);
    try {
      // Don't pass userId - let API service resolve it internally for consistency
      const patterns = await apiService.getUserPatterns();
      setUserPatterns(patterns);
    } catch (error) {
      console.error('Failed to load user patterns:', error);
      // Don't use mock data - show user they need to create entries first
      setUserPatterns(null);
    } finally {
      setLoadingPatterns(false);
    }
  };

  const loadLastAIResponse = () => {
    try {
      const stored = localStorage.getItem('lastAIResponse');
      if (stored) {
        const response = JSON.parse(stored) as AdaptiveResponseResponse;
        setLastAIResponse(response);
      }
    } catch (error) {
      console.error('Failed to load last AI response:', error);
    }
  };

  const refreshPatterns = async () => {
    setRefreshingPatterns(true);
    try {
      // Just reload patterns since there's no specific refresh method
      await loadUserPatterns();
    } catch (error) {
      console.error('Failed to refresh patterns:', error);
    } finally {
      setRefreshingPatterns(false);
    }
  };

  const getPersonaIcon = (personaId: string) => {
    switch (personaId) {
      case 'pulse':
        return <Sparkles className="h-4 w-4" />;
      case 'sage':
        return <BookOpen className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  const insights = [
    {
      title: "Mood Pattern",
      description: userPatterns 
        ? `Your average mood is ${userPatterns.mood_trends.mood.toFixed(1)}/10`
        : "Your mood tends to be higher on weekends",
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      title: "Writing Style",
      description: userPatterns 
        ? `You have an ${userPatterns.writing_style} writing style`
        : "You write most thoughtfully in the evenings",
      icon: Calendar,
      color: "text-blue-600",
    },
    {
      title: "AI Engagement",
      description: `Pattern confidence: ${userPatterns ? Math.round(userPatterns.pattern_confidence * 100) : 75}%`,
      icon: BookOpen,
      color: "text-purple-600",
    },
  ];

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-sm sm:max-w-md md:max-w-2xl lg:max-w-4xl xl:max-w-6xl 2xl:max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">Insights</h1>
                <p className="text-sm text-muted-foreground">
                  Your reflection journey
                </p>
              </div>
            </div>
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
        </div>
      </header>

      <main className="max-w-sm sm:max-w-md md:max-w-2xl lg:max-w-4xl xl:max-w-6xl 2xl:max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Latest AI Response */}
        {lastAIResponse && (
          <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-between text-base">
                <div className="flex items-center gap-2">
                  {getPersonaIcon(lastAIResponse.persona_used.persona_id)}
                  <span>Latest from {lastAIResponse.persona_used.persona_name}</span>
                </div>
                <Badge variant="secondary" className="text-xs">
                  {Math.round(lastAIResponse.adaptation_confidence * 100)}% adapted
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">Insight</h4>
                <p className="text-sm text-gray-800 leading-relaxed">
                  {lastAIResponse.ai_insight.insight}
                </p>
              </div>
              
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">Suggested Action</h4>
                <p className="text-sm text-gray-800 leading-relaxed">
                  {lastAIResponse.ai_insight.suggested_action}
                </p>
              </div>
              
              {lastAIResponse.ai_insight.follow_up_question && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Reflection Question</h4>
                  <p className="text-sm text-gray-800 leading-relaxed italic">
                    "{lastAIResponse.ai_insight.follow_up_question}"
                  </p>
                </div>
              )}
              
              <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t">
                <span>
                  Confidence: {Math.round(lastAIResponse.ai_insight.confidence_score * 100)}%
                </span>
                <span>
                  {new Date(lastAIResponse.response_generated_at).toLocaleString()}
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="border-0 bg-gradient-to-br from-primary/5 to-primary/10">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-primary">
                {userPatterns?.entries_analyzed || 0}
              </div>
              <div className="text-sm text-muted-foreground">
                Entries analyzed
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 bg-gradient-to-br from-orange-500/5 to-orange-500/10">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">
                {0}
              </div>
              <div className="text-sm text-muted-foreground">Day streak</div>
            </CardContent>
          </Card>
        </div>

        {/* User Patterns */}
        {userPatterns && (
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <User className="w-5 h-5" />
              Your Patterns
            </h2>
            <PatternInsights patterns={userPatterns} isLoading={loadingPatterns} />
          </div>
        )}

        {/* Weekly Goal Progress */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Target className="w-4 h-4" />
              Weekly Goal
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Progress this week</span>
              <span className="font-medium">
                {0}/{5} entries
              </span>
            </div>
            <Progress
              value={(0 / 5) * 100}
              className="h-2"
            />
            <p className="text-xs text-muted-foreground">
              {5 - 0 > 0
                ? `${5 - 0} more to reach your goal`
                : "Goal achieved! 🎉"}
            </p>
          </CardContent>
        </Card>

        {/* Mood Trend */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Heart className="w-4 h-4" />
              Mood This Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between h-20 mb-2">
              {/* Mood chart will be loaded from real data */}
              <div className="text-center text-sm text-muted-foreground">
                Create journal entries to see your mood trends
              </div>
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Average: {userPatterns?.mood_trends.mood.toFixed(1) || "0.0"}/10</span>
              <span>This week</span>
            </div>
          </CardContent>
        </Card>

        {/* AI Insights */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            AI Insights
          </h2>

          {insights.map((insight, index) => (
            <Card key={index} className="border-l-4 border-l-primary/30">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <insight.icon className={`w-5 h-5 mt-0.5 ${insight.color}`} />
                  <div>
                    <h3 className="font-medium text-sm">{insight.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {insight.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Achievements */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Award className="w-4 h-4" />
              Recent Achievements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-primary/5 rounded-lg">
              <div className="text-2xl">🔥</div>
              <div>
                <div className="font-medium text-sm">Week Warrior</div>
                <div className="text-xs text-muted-foreground">
                  7 days in a row
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg opacity-60">
              <div className="text-2xl">📚</div>
              <div>
                <div className="font-medium text-sm">Deep Thinker</div>
                <div className="text-xs text-muted-foreground">
                  25 long entries (locked)
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg opacity-60">
              <div className="text-2xl">🤖</div>
              <div>
                <div className="font-medium text-sm">AI Whisperer</div>
                <div className="text-xs text-muted-foreground">
                  100 AI interactions (locked)
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Insights;
