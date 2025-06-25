import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, useParams } from "react-router-dom";
import { ArrowLeft, Send, Lightbulb, Heart, Settings, Mic, MicOff, Image, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import PersonaSelector from "@/components/PersonaSelector";
import EmojiReactionSystem from "@/components/EmojiReactionSystem";
import { apiService, PersonaInfo } from "@/services/api";
import { getCurrentUserId } from "@/utils/userSession";

// Local type for personas with additional UI properties
type PersonaRecommendation = PersonaInfo & {
  recommended: boolean;
  available: boolean;
  requires_premium: boolean;
  times_used: number;
  recommendation_reason: string;
};

// Universal journal prompt for multi-theme approach
const UNIVERSAL_PROMPT = "What's on your mind today? Nothing is off-limits.";

// Focus areas for multi-theme journaling
const FOCUS_AREAS = [
  { id: "work_stress", label: "Work Stress", emoji: "💼" },
  { id: "anxiety", label: "Anxiety", emoji: "😰" },
  { id: "relationships", label: "Relationships", emoji: "❤️" },
  { id: "health", label: "Health & Wellness", emoji: "🏃‍♀️" },
  { id: "creativity", label: "Creativity", emoji: "🎨" },
  { id: "motivation", label: "Motivation", emoji: "💪" },
  { id: "sleep", label: "Sleep", emoji: "😴" },
  { id: "purpose", label: "Life Purpose", emoji: "🌟" },
  { id: "loneliness", label: "Loneliness", emoji: "🤗" },
  { id: "grief", label: "Grief & Loss", emoji: "🕊️" },
  { id: "planning", label: "Planning & Goals", emoji: "📋" },
  { id: "reflection", label: "General Reflection", emoji: "💭" }
];

const JournalEntry = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { id } = useParams();
  const [content, setContent] = useState("");
  const [mood, setMood] = useState(5);
  const [energy, setEnergy] = useState(5);
  const [stress, setStress] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPersonaSelector, setShowPersonaSelector] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState("pulse");
  const [personas, setPersonas] = useState<PersonaRecommendation[]>([]);
  const [loadingPersonas, setLoadingPersonas] = useState(false);
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<string[]>([]);
  const [showFocusAreas, setShowFocusAreas] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showVoiceInput, setShowVoiceInput] = useState(false);
  const [premiumEnabled, setPremiumEnabled] = useState(false);
  const [detectedTopics, setDetectedTopics] = useState<string[]>([]);
  const [selectedEmoji, setSelectedEmoji] = useState<any>(null);
  const [showEmojiReactions, setShowEmojiReactions] = useState(false);
  
  // Image upload states
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [imagePreviewUrls, setImagePreviewUrls] = useState<string[]>([]);
  
  // View mode states
  const [isViewMode, setIsViewMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [existingEntry, setExistingEntry] = useState<any>(null);

  // Get dynamic user ID from browser session
  const userId = getCurrentUserId();

  useEffect(() => {
    loadPersonas();
    
    // Check if we're viewing an existing entry
    if (id) {
      setIsViewMode(true);
      loadExistingEntry(id);
    } else {
      // Initialize content from URL prompt parameter for new entries
      const promptFromUrl = searchParams.get('prompt');
      if (promptFromUrl) {
        setContent(promptFromUrl);
      }
    }
  }, [id, searchParams]);

  const loadExistingEntry = async (entryId: string) => {
    setIsLoading(true);
    try {
      const entry = await apiService.getJournalEntry(entryId);
      setExistingEntry(entry);
      setContent(entry.content);
      setMood(entry.mood_level);
      setEnergy(entry.energy_level);
      setStress(entry.stress_level);
      setSelectedFocusAreas(entry.tags || []);
    } catch (error) {
      console.error('Failed to load journal entry:', error);
      // Fallback to mock data for demo
      const mockEntry = {
        id: entryId,
        content: "This is a sample journal entry for viewing. In a real app, this would be loaded from the backend.",
        mood_level: 7,
        energy_level: 6,
        stress_level: 4,
        tags: ['work', 'reflection'],
        created_at: new Date().toISOString()
      };
      setExistingEntry(mockEntry);
      setContent(mockEntry.content);
      setMood(mockEntry.mood_level);
      setEnergy(mockEntry.energy_level);
      setStress(mockEntry.stress_level);
      setSelectedFocusAreas(mockEntry.tags);
    } finally {
      setIsLoading(false);
    }
  };

  // Detect topics when content changes
  useEffect(() => {
    if (content.length > 50) { // Only detect topics for substantial content
      detectTopics();
    }
  }, [content]);

  const detectTopics = async () => {
    try {
      const topics = await apiService.classifyTopics(content);
      setDetectedTopics(topics);
      setShowEmojiReactions(true);
    } catch (error) {
      console.error('Failed to classify topics:', error);
      // Use fallback topic detection based on keywords
      const fallbackTopics = detectTopicsFallback(content);
      setDetectedTopics(fallbackTopics);
      if (fallbackTopics.length > 0) {
        setShowEmojiReactions(true);
      }
    }
  };

  const detectTopicsFallback = (text: string): string[] => {
    const keywords = {
      work_stress: ['work', 'deadline', 'pressure', 'meeting', 'project', 'boss', 'colleague'],
      anxiety: ['anxious', 'worried', 'nervous', 'overwhelmed', 'panic', 'fear'],
      relationships: ['friend', 'family', 'partner', 'relationship', 'love', 'conflict'],
      motivation: ['goal', 'achieve', 'success', 'progress', 'motivation', 'drive'],
      reflection: ['thinking', 'wondering', 'considering', 'reflection', 'contemplating']
    };

    const lowerText = text.toLowerCase();
    const detectedTopics: string[] = [];

    Object.entries(keywords).forEach(([topic, words]) => {
      if (words.some(word => lowerText.includes(word))) {
        detectedTopics.push(topic);
      }
    });

    return detectedTopics;
  };

  const loadPersonas = async () => {
    setLoadingPersonas(true);
    try {
      const availablePersonas = await apiService.getAvailablePersonas();
      // Convert PersonaInfo to PersonaRecommendation format
      const convertedPersonas: PersonaRecommendation[] = availablePersonas.map(p => ({
        ...p,
        recommended: p.recommended || false,
        available: p.available || true,
        requires_premium: p.requires_premium || false,
        times_used: p.times_used || 0,
        recommendation_reason: p.recommendation_reason || `Great for ${p.description.toLowerCase()}`
      }));
      setPersonas(convertedPersonas);
      
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
          times_used: 0,
          recommendation_reason: "Perfect for emotional support and wellness insights"
        }
      ]);
    } finally {
      setLoadingPersonas(false);
    }
  };

  const handleFocusAreaToggle = (areaId: string) => {
    setSelectedFocusAreas(prev => 
      prev.includes(areaId) 
        ? prev.filter(id => id !== areaId)
        : [...prev, areaId]
    );
  };

  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setShowVoiceInput(true);
      setIsRecording(true);
      
      // Mock voice input for now - in production, implement actual speech recognition
      setTimeout(() => {
        setIsRecording(false);
        setShowVoiceInput(false);
        // For demo purposes, add some sample text
        setContent(prev => prev + " I'm feeling a bit overwhelmed with work today and could use some support.");
      }, 3000);
    } else {
      alert('Voice input is not supported in your browser. Please type your reflection.');
    }
  };

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    // Limit to 5 images total
    const remainingSlots = 5 - selectedImages.length;
    const filesToAdd = files.slice(0, remainingSlots);
    
    // Validate file size (max 5MB per image)
    const validFiles = filesToAdd.filter(file => {
      if (file.size > 5 * 1024 * 1024) {
        alert(`Image "${file.name}" is too large. Please select images under 5MB.`);
        return false;
      }
      return true;
    });

    if (validFiles.length > 0) {
      setSelectedImages(prev => [...prev, ...validFiles]);
      
      // Generate preview URLs
      validFiles.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreviewUrls(prev => [...prev, e.target?.result as string]);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const removeImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
    setImagePreviewUrls(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    // Validate content length (backend requires min 10 characters)
    if (!content.trim()) {
      alert('Please write something before saving your reflection.');
      return;
    }
    
    if (content.trim().length < 10) {
      alert('Please write at least 10 characters to save your reflection.');
      return;
    }

    setIsSubmitting(true);

    try {
      // Create journal entry via API with focus areas
      const journalEntry = await apiService.createJournalEntry({
        content: content.trim(),
        mood_level: mood,
        energy_level: energy,
        stress_level: stress,
        tags: selectedFocusAreas, // Use focus areas as tags
        work_challenges: [],
        gratitude_items: []
      });

      console.log('Journal entry created successfully:', journalEntry);

      // Generate adaptive AI response with focus areas context
      try {
        // Don't pass user_id - let API service resolve it internally for consistency
        const adaptiveResponse = await apiService.generateAdaptiveResponse({
          journal_content: content.trim(),
          persona: selectedPersona,
          force_persona: false,
          include_pattern_analysis: true,
          response_preferences: {
            mood_level: mood,
            energy_level: energy,
            stress_level: stress,
            focus_areas: selectedFocusAreas // Pass focus areas in response_preferences
          }
        });

        console.log('Adaptive AI response generated:', adaptiveResponse);
        
        // Store the response for display on the insights page
        localStorage.setItem('lastAIResponse', JSON.stringify(adaptiveResponse));
        
        // Navigate to insights page to show the AI response
        navigate("/insights");
      } catch (aiError) {
        console.error('Failed to generate AI response:', aiError);
        
        // Create a fallback response so user gets feedback
        const fallbackResponse = {
          message: "Thanks for sharing your thoughts! Your reflection has been saved successfully.",
          insight: "I notice you're reflecting on important aspects of your life. Taking time to journal shows great self-awareness.",
          suggested_action: "Consider setting aside a few minutes each day for this kind of reflection. It's a powerful tool for personal growth.",
          follow_up_question: "What's one small thing you could do today to support your wellbeing?",
          confidence_score: 0.8,
          persona_used: selectedPersona || "pulse",
          generated_at: new Date().toISOString()
        };
        
        // Store fallback response
        localStorage.setItem('lastAIResponse', JSON.stringify(fallbackResponse));
        localStorage.setItem('aiResponseFallback', 'true'); // Mark as fallback
        
        // Still navigate to insights to show fallback response
        navigate("/insights");
      }
    } catch (error) {
      console.error('Failed to create journal entry:', error);
      // Show error to user (you could add a toast notification here)
      alert('Failed to save journal entry. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBack = () => {
    navigate("/");
  };

  const wordCount = content
    .trim()
    .split(/\s+/)
    .filter((word) => word.length > 0).length;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-lg mx-auto px-4 py-4">
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
              <h1 className="text-lg font-semibold">
                {isViewMode ? "Journal Entry" : "New Reflection"}
              </h1>
              <p className="text-sm text-muted-foreground">
                {isViewMode 
                  ? existingEntry 
                    ? new Date(existingEntry.created_at).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })
                    : "Loading entry..."
                  : "Take your time, this is your space"
                }
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowPersonaSelector(!showPersonaSelector)}
              className="gap-2"
            >
              <Settings className="w-4 h-4" />
              AI
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
        <div className="space-y-6">
          {/* Persona Selector */}
          {showPersonaSelector && (
            <Card>
              <CardContent className="p-4">
                <PersonaSelector
                  userId={userId}
                  premiumEnabled={premiumEnabled}
                  onPremiumToggle={setPremiumEnabled}
                  personas={personas}
                  isLoading={loadingPersonas}
                />
              </CardContent>
            </Card>
          )}

          {/* Universal Journal Prompt - Compact */}
          <Card className="bg-muted/30">
            <CardContent className="px-4 py-3">
              <p className="text-sm text-muted-foreground text-center">
                What's on your mind today? Nothing is off-limits.
              </p>
            </CardContent>
          </Card>

          {/* Focus Areas Selection - Compact */}
          <Card className="bg-muted/20">
            <CardContent className="px-4 py-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Focus areas (optional)</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowFocusAreas(!showFocusAreas)}
                  className="text-xs h-6 px-2"
                >
                  {showFocusAreas ? "Hide" : "Show"}
                </Button>
              </div>
              {showFocusAreas ? (
                <div className="grid grid-cols-3 gap-1 text-xs">
                  {FOCUS_AREAS.map((area) => (
                    <div key={area.id} className="flex items-center space-x-1">
                      <Checkbox
                        id={area.id}
                        checked={selectedFocusAreas.includes(area.id)}
                        onCheckedChange={() => handleFocusAreaToggle(area.id)}
                        className="h-3 w-3"
                      />
                      <label
                        htmlFor={area.id}
                        className="text-xs leading-none cursor-pointer"
                      >
                        <span className="mr-1">{area.emoji}</span>
                        {area.label}
                      </label>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-wrap gap-1">
                  {selectedFocusAreas.length > 0 ? (
                    selectedFocusAreas.map(areaId => {
                      const area = FOCUS_AREAS.find(a => a.id === areaId);
                      return (
                        <Badge key={areaId} variant="secondary" className="text-xs h-5">
                          {area?.emoji} {area?.label}
                        </Badge>
                      );
                    })
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      Select areas for personalized support
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Compact Mood Tracker */}
          <Card className="bg-muted/20">
            <CardContent className="px-4 py-3">
              <div className="text-sm text-muted-foreground mb-3 text-center">Quick mood check</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs text-muted-foreground min-w-[60px]">
                    Mood
                  </label>
                  <div className="flex-1 mx-3">
                    <Slider
                      value={[mood]}
                      onValueChange={(value) => setMood(value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="w-full [&_[role=slider]]:h-3 [&_[role=slider]]:w-3"
                    />
                  </div>
                  <span className="text-xs text-muted-foreground min-w-[30px] text-right">
                    {mood}/10
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-xs text-muted-foreground min-w-[60px]">
                    Energy
                  </label>
                  <div className="flex-1 mx-3">
                    <Slider
                      value={[energy]}
                      onValueChange={(value) => setEnergy(value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="w-full [&_[role=slider]]:h-3 [&_[role=slider]]:w-3"
                    />
                  </div>
                  <span className="text-xs text-muted-foreground min-w-[30px] text-right">
                    {energy}/10
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-xs text-muted-foreground min-w-[60px]">
                    Stress
                  </label>
                  <div className="flex-1 mx-3">
                    <Slider
                      value={[stress]}
                      onValueChange={(value) => setStress(value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="w-full [&_[role=slider]]:h-3 [&_[role=slider]]:w-3"
                    />
                  </div>
                  <span className="text-xs text-muted-foreground min-w-[30px] text-right">
                    {stress}/10
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Journal Entry - Prominent */}
          <Card className="border-2 border-primary/20 shadow-lg">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="journal-content"
                    className="text-lg font-medium text-primary"
                  >
                    Your reflection
                  </label>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleVoiceInput}
                      disabled={isRecording}
                      className="gap-1 text-xs"
                    >
                      {isRecording ? (
                        <>
                          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                          Recording...
                        </>
                      ) : (
                        <>
                          <Mic className="w-3 h-3" />
                          Voice
                        </>
                      )}
                    </Button>
                    <span className={`text-xs ${
                      content.trim().length < 10 
                        ? 'text-orange-500' 
                        : 'text-muted-foreground'
                    }`}>
                      {content.trim().length}/10 min • {wordCount} words
                    </span>
                  </div>
                </div>

                <Textarea
                  id="journal-content"
                  placeholder="What's on your mind? Write freely about your thoughts, feelings, or experiences... Nothing is off-limits."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="min-h-[250px] border-0 bg-transparent text-foreground placeholder:text-muted-foreground resize-none focus:ring-0 focus:outline-none text-lg leading-relaxed"
                  style={{ fontSize: "18px" }} // Prevent zoom on iOS and make more prominent
                />

                {/* Voice Input Status */}
                {showVoiceInput && (
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center gap-2 text-blue-700">
                      <Mic className="w-4 h-4" />
                      <span className="text-sm">
                        {isRecording ? "Listening... Speak now" : "Voice input added"}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Emoji Reaction System */}
          {showEmojiReactions && content.length > 50 && (
            <EmojiReactionSystem
              journalContent={content}
              detectedTopics={detectedTopics}
              onReactionSelect={(reaction) => {
                setSelectedEmoji(reaction);
                console.log('Selected emoji reaction:', reaction);
              }}
              className="animate-fade-in"
            />
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-calm-500">
              {personas.find(p => p.persona_id === selectedPersona)?.persona_name || 'Pulse'} will provide insights
            </div>

            <Button
              onClick={handleSubmit}
              disabled={!content.trim() || content.trim().length < 10 || isSubmitting}
              className="gap-2 min-w-[120px]"
            >
              {isSubmitting ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              {isSubmitting ? "Saving..." : "Save reflection"}
            </Button>
          </div>

          {/* Subtle Tips */}
          <div className="mt-6 p-3 bg-muted/30 rounded-lg border border-dashed border-muted-foreground/30">
            <details className="group">
              <summary className="text-xs text-muted-foreground cursor-pointer list-none flex items-center gap-2">
                <span className="group-open:rotate-90 transition-transform">▶</span>
                Tips for reflection
              </summary>
              <ul className="text-xs text-muted-foreground space-y-1 mt-2 ml-4">
                <li>• Write without judgment - this is your safe space</li>
                <li>• Focus on how you're feeling, not just what happened</li>
                <li>• Be honest with yourself - it's okay to struggle</li>
                <li>• Use voice input if typing feels overwhelming</li>
                <li>• {personas.find(p => p.persona_id === selectedPersona)?.persona_name || 'Pulse'} will provide personalized insights</li>
              </ul>
            </details>
          </div>
        </div>
        )}
      </main>
    </div>
  );
};

export default JournalEntry;
