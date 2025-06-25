import { useState, useEffect } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  Brain,
  Heart,
  RefreshCw,
  MessageCircle,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Send,
  Copy,
  Share2,
  Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { apiService, type PulseResponse, type JournalEntry } from "@/services/api";

const PulseResponse = () => {
  const navigate = useNavigate();
  const { entryId } = useParams();
  const [searchParams] = useSearchParams();
  
  // State for data
  const [journalEntry, setJournalEntry] = useState<JournalEntry | null>(null);
  const [aiResponse, setAiResponse] = useState<PulseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingResponse, setIsGeneratingResponse] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // State for interactions
  const [userFeedback, setUserFeedback] = useState<'thumbs_up' | 'thumbs_down' | null>(null);
  const [showReplyInput, setShowReplyInput] = useState(false);
  const [replyContent, setReplyContent] = useState("");
  const [showCelebration, setShowCelebration] = useState(false);

  useEffect(() => {
    if (entryId) {
      loadJournalEntryAndResponse();
    }
    
    // Show celebration if coming from successful save
    if (searchParams.get('showCelebration') === 'true') {
      setShowCelebration(true);
      setTimeout(() => setShowCelebration(false), 3000);
    }
  }, [entryId, searchParams]);

  const loadJournalEntryAndResponse = async () => {
    if (!entryId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Load the journal entry first
      const entry = await apiService.getJournalEntry(entryId);
      setJournalEntry(entry);
      
      // Generate AI response
      setIsGeneratingResponse(true);
      const response = await apiService.getPulseResponse(entryId);
      setAiResponse(response);
      
    } catch (error: any) {
      console.error('Failed to load journal entry or AI response:', error);
      
      // Handle specific error cases
      if (error.response?.status === 429) {
        setError("You've reached your daily AI response limit. Try again tomorrow!");
      } else if (error.response?.status === 404) {
        setError("Journal entry not found. It may have been deleted.");
      } else {
        setError("Failed to generate AI response. Please try again later.");
      }
    } finally {
      setIsLoading(false);
      setIsGeneratingResponse(false);
    }
  };

  const handleFeedback = async (type: 'thumbs_up' | 'thumbs_down') => {
    if (!entryId || userFeedback === type) return;
    
    try {
      await apiService.submitPulseFeedback(entryId, type);
      setUserFeedback(type);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleReply = async () => {
    if (!replyContent.trim() || !entryId) return;
    
    try {
      // For now, just show success message
      alert("Reply saved! Pulse will learn from your feedback.");
      setReplyContent("");
      setShowReplyInput(false);
    } catch (error) {
      console.error('Failed to submit reply:', error);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: "My Pulse Reflection",
        text: "Check out this thoughtful AI response to my journal entry",
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert("Link copied to clipboard!");
    }
  };

  const handleNewReflection = () => {
    navigate("/journal");
  };

  const handleBack = () => {
    navigate("/");
  };

  const getMoodEmoji = (mood: number) => {
    if (mood <= 2) return "😔";
    if (mood <= 4) return "😐";
    if (mood <= 6) return "🙂";
    if (mood <= 8) return "😊";
    return "😄";
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pulse-50 via-background to-calm-50">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 border-4 border-pulse-200 border-t-pulse-500 rounded-full animate-spin mx-auto"></div>
            <p className="text-pulse-600">Loading your reflection...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pulse-50 via-background to-calm-50">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-6 text-center">
              <h2 className="text-lg font-semibold text-red-800 mb-2">Oops!</h2>
              <p className="text-red-600 mb-4">{error}</p>
              <div className="flex gap-3 justify-center">
                <Button onClick={handleBack} variant="outline">
                  Back to Journal
                </Button>
                <Button onClick={loadJournalEntryAndResponse}>
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pulse-50 via-background to-calm-50">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBack}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <div className="flex-1">
              <h1 className="text-lg font-semibold">Pulse Response</h1>
              <p className="text-sm text-muted-foreground">
                {journalEntry ? formatTimestamp(journalEntry.created_at) : 'AI reflection on your journal entry'}
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={handleShare} className="gap-2">
              <Share2 className="w-4 h-4" />
              Share
            </Button>
          </div>
        </div>
      </header>

      {/* Celebration Message */}
      {showCelebration && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
          <Card className="border-green-200 bg-green-50 shadow-lg">
            <CardContent className="p-4 flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-green-600" />
              <div>
                <p className="font-medium text-green-800">Reflection saved!</p>
                <p className="text-sm text-green-600">Pulse is analyzing your entry...</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        
        {/* Your Journal Entry */}
        {journalEntry && (
          <Card className="border-muted">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-gradient-to-r from-calm-400 to-calm-500"></div>
                  <span className="font-medium text-sm">Your Reflection</span>
                  <Badge variant="outline" className="text-xs">
                    {getMoodEmoji(journalEntry.mood_level)} {journalEntry.mood_level}/10
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  {formatTimestamp(journalEntry.created_at)}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground leading-relaxed">{journalEntry.content}</p>
            </CardContent>
          </Card>
        )}

        {/* AI Response */}
        {isGeneratingResponse ? (
          <Card className="border-pulse-200 bg-pulse-50/30">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pulse-400 to-pulse-600 flex items-center justify-center">
                  <Brain className="w-4 h-4 text-white animate-pulse" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-medium text-pulse-800">Pulse is thinking</span>
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-pulse-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-pulse-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-pulse-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                  <p className="text-sm text-pulse-600">Generating your personalized response...</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : aiResponse ? (
          <Card className="border-pulse-200 bg-pulse-50/30">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pulse-400 to-pulse-600 flex items-center justify-center">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <span className="font-medium text-pulse-800">Pulse</span>
                    <p className="text-xs text-pulse-600">Your AI wellness companion</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    {Math.round(aiResponse.confidence_score * 100)}% confidence
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {aiResponse.response_time_ms}ms
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* AI Message */}
              <div className="bg-white/50 rounded-lg p-4 border">
                <p className="text-foreground leading-relaxed mb-3">{aiResponse.message}</p>
                
                {/* Suggested Actions */}
                {aiResponse.suggested_actions.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-pulse-800">Suggested actions:</p>
                    <div className="flex flex-wrap gap-2">
                      {aiResponse.suggested_actions.map((action, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          💡 {action}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Follow-up Question */}
              {aiResponse.follow_up_question && (
                <div className="bg-pulse-100/50 rounded-lg p-4 border border-pulse-200">
                  <p className="text-sm font-medium text-pulse-800 mb-2">Pulse asks:</p>
                  <p className="text-pulse-700 italic">"{aiResponse.follow_up_question}"</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="flex items-center gap-2">
                  <Button
                    variant={userFeedback === 'thumbs_up' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => handleFeedback('thumbs_up')}
                    className="gap-2"
                  >
                    <ThumbsUp className="w-4 h-4" />
                    Helpful
                  </Button>
                  <Button
                    variant={userFeedback === 'thumbs_down' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => handleFeedback('thumbs_down')}
                    className="gap-2"
                  >
                    <ThumbsDown className="w-4 h-4" />
                    Not helpful
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowReplyInput(!showReplyInput)}
                    className="gap-2"
                  >
                    <MessageCircle className="w-4 h-4" />
                    Reply
                  </Button>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigator.clipboard.writeText(aiResponse.message)}
                  className="gap-2"
                >
                  <Copy className="w-4 h-4" />
                  Copy
                </Button>
              </div>

              {/* Reply Input */}
              {showReplyInput && (
                <div className="space-y-3 pt-3 border-t">
                  <Textarea
                    placeholder="Share your thoughts on this response..."
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    className="min-h-[80px]"
                  />
                  <div className="flex gap-2">
                    <Button onClick={handleReply} size="sm" className="gap-2">
                      <Send className="w-4 h-4" />
                      Send Reply
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setShowReplyInput(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ) : null}

        {/* Next Steps */}
        <Card className="bg-gradient-to-r from-pulse-50 to-calm-50 border-pulse-200">
          <CardContent className="p-6 text-center">
            <h3 className="font-semibold text-pulse-800 mb-3">Continue your wellness journey</h3>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                onClick={handleNewReflection}
                className="gap-2 bg-gradient-to-r from-pulse-500 to-pulse-600 hover:from-pulse-600 hover:to-pulse-700"
              >
                <MessageCircle className="w-4 h-4" />
                New reflection
              </Button>
              <Button variant="outline" onClick={handleBack} className="gap-2">
                <Heart className="w-4 h-4" />
                Back to journal
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PulseResponse;
