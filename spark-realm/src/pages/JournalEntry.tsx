import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, useParams } from "react-router-dom";
import { ArrowLeft, Send, Lightbulb, Heart, Settings, Mic, MicOff, Image, X, Camera, Save, ChevronUp, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import PersonaSelector from "@/components/PersonaSelector";
import EmojiReactionSystem from "@/components/EmojiReactionSystem";
import { apiService, PersonaInfo } from "@/services/api";
import { authService } from "@/services/authService";

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

  // Auto-save states
  const [autoSaving, setAutoSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [draftKey, setDraftKey] = useState<string>("");

  // Get current user ID from authenticated session
  const [userId, setUserId] = useState<string>("");

  // Initialize user ID on component mount
  useEffect(() => {
    const initializeUser = async () => {
      const { user } = await authService.getCurrentUser();
      if (user?.id) {
        setUserId(user.id);
      }
    };
    initializeUser();
  }, []);

  // Initialize draft key on component mount
  useEffect(() => {
    const currentDraftKey = `journal_draft_${userId}_${Date.now()}`;
    setDraftKey(currentDraftKey);
    
    // Load existing draft if available
    const savedDraft = localStorage.getItem(`journal_draft_${userId}`);
    if (savedDraft && !id) { // Only load draft if not viewing existing entry
      try {
        const draft = JSON.parse(savedDraft);
        setContent(draft.content || "");
        setMood(draft.mood || 5);
        setEnergy(draft.energy || 5);
        setStress(draft.stress || 5);
        setSelectedFocusAreas(draft.focusAreas || []);
        setLastSaved(new Date(draft.lastSaved));
      } catch (error) {
        console.log("Could not load draft:", error);
      }
    }
  }, [userId, id]);

  // Auto-save functionality
  useEffect(() => {
    if (!content.trim() || content.length < 10) return; // Don't save empty or very short content
    
    const autoSaveTimer = setTimeout(() => {
      setAutoSaving(true);
      
      const draft = {
        content,
        mood,
        energy,
        stress,
        focusAreas: selectedFocusAreas,
        lastSaved: new Date().toISOString()
      };
      
      try {
        localStorage.setItem(`journal_draft_${userId}`, JSON.stringify(draft));
        setLastSaved(new Date());
        
        setTimeout(() => {
          setAutoSaving(false);
        }, 500);
      } catch (error) {
        console.error("Auto-save failed:", error);
        setAutoSaving(false);
      }
    }, 2000); // Auto-save after 2 seconds of no typing
    
    return () => clearTimeout(autoSaveTimer);
  }, [content, mood, energy, stress, selectedFocusAreas, userId]);

  // Clear draft when entry is successfully saved
  const clearDraft = () => {
    localStorage.removeItem(`journal_draft_${userId}`);
    setLastSaved(null);
  };

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
      // Don't use mock data - show error or empty state
      setExistingEntry(null);
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
      // Don't use fallback personas - real data only
      setPersonas([]);
    } finally {
      setLoadingPersonas(false);
    }
  };

  // Helper function to toggle focus areas
  const toggleFocusArea = (areaId: string) => {
    setSelectedFocusAreas(prev => {
      if (prev.includes(areaId)) {
        return prev.filter(id => id !== areaId);
      } else {
        return [...prev, areaId];
      }
    });
  };

  // Handle focus area toggle (alias for backwards compatibility)
  const handleFocusAreaToggle = toggleFocusArea;

  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setShowVoiceInput(true);
      setIsRecording(true);
      
      // Voice input placeholder - requires actual speech recognition implementation
      setTimeout(() => {
        setIsRecording(false);
        setShowVoiceInput(false);
        // Voice input not implemented yet
        alert('Voice input feature coming soon! Please type your reflection for now.');
      }, 1000);
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

      // Clear the draft after successful save
      clearDraft();

      // Navigate to insights page or another appropriate page
      if (searchParams.get('returnTo') === 'insights') {
        navigate('/insights');
      } else {
        navigate(`/pulse-response?entryId=${journalEntry.id}&showCelebration=true`);
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
              <h1 className="text-xl font-semibold">
                {isViewMode ? "Your Reflection" : "New Journal Entry"}
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
                  : "Your space for deep reflection and meaningful thoughts"
                }
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">
                {wordCount} words
              </p>
              <p className="text-xs text-muted-foreground">
                {content.trim().length >= 10 ? '✓ Ready to save' : 'Keep writing...'}
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        
        {/* MAIN WRITING AREA - Now the primary focus */}
        <Card className="border-2 shadow-lg">
          <CardContent className="p-8">
            <div className="space-y-6">
              {/* Writing Prompt & Tools */}
              <div className="flex items-center justify-between border-b pb-4">
                <div className="flex-1">
                  <h2 className="text-2xl font-medium text-primary mb-2">
                    What's on your mind today?
                  </h2>
                  <p className="text-muted-foreground text-lg">
                    Nothing is off-limits. Write freely about your thoughts, feelings, experiences, dreams, or anything that matters to you right now.
                  </p>
                </div>
                <div className="flex items-center gap-3 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleVoiceInput}
                    disabled={isRecording}
                    className="gap-2"
                  >
                    {isRecording ? (
                      <>
                        <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                        Recording...
                      </>
                    ) : (
                      <>
                        <Mic className="w-4 h-4" />
                        Voice Input
                      </>
                    )}
                  </Button>
                  <Button variant="ghost" size="sm" className="gap-2">
                    <Camera className="w-4 h-4" />
                    Add Image
                  </Button>
                </div>
              </div>

              {/* Large, Prominent Text Area */}
              <div className="relative">
                <Textarea
                  id="journal-content"
                  placeholder="Start writing here... Let your thoughts flow freely. This is your private space to explore your inner world, process your experiences, and capture what matters to you. Take your time - there's no rush."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="min-h-[400px] border-0 bg-transparent text-foreground placeholder:text-muted-foreground resize-none focus:ring-0 focus:outline-none text-lg leading-relaxed p-0"
                  style={{ fontSize: "19px", lineHeight: "1.6" }}
                />
                
                {/* Writing Encouragement */}
                {content.length > 0 && content.length < 50 && (
                  <div className="absolute bottom-4 left-0 text-sm text-muted-foreground animate-fade-in">
                    💭 Keep going... share more of what you're thinking
                  </div>
                )}
                
                {content.length >= 50 && content.length < 200 && (
                  <div className="absolute bottom-4 left-0 text-sm text-green-600 animate-fade-in">
                    ✨ Great start! You're building a meaningful reflection
                  </div>
                )}
                
                {content.length >= 200 && (
                  <div className="absolute bottom-4 left-0 text-sm text-blue-600 animate-fade-in">
                    🎯 Excellent depth! This kind of reflection is powerful
                  </div>
                )}
              </div>

              {/* Voice Input Status */}
              {showVoiceInput && (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 animate-fade-in">
                  <div className="flex items-center gap-3 text-blue-700">
                    <Mic className="w-5 h-5 animate-pulse" />
                    <div>
                      <p className="font-medium">
                        {isRecording ? "Listening... Speak clearly" : "Voice input completed"}
                      </p>
                      <p className="text-sm text-blue-600">
                        Your voice will be transcribed and added to your journal
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Writing Stats */}
              <div className="flex items-center justify-between text-sm text-muted-foreground pt-4 border-t">
                <div className="flex items-center gap-6">
                  <span className="flex items-center gap-2">
                    📝 <strong>{wordCount}</strong> words
                  </span>
                  <span className="flex items-center gap-2">
                    📊 <strong>{content.trim().length}</strong> characters
                  </span>
                  <span className="flex items-center gap-2">
                    ⏱️ {Math.ceil(wordCount / 200)} min read
                  </span>
                </div>
                <div className="text-right">
                  {content.trim().length >= 10 ? (
                    <span className="text-green-600 font-medium">Ready to save ✓</span>
                  ) : (
                    <span>Minimum 10 characters ({content.trim().length}/10)</span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Focus Areas - Simplified and Secondary */}
        {!isViewMode && (
          <Card className="border border-muted">
            <CardContent className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm">Focus Areas</p>
                  <p className="text-xs text-muted-foreground">Help personalize your AI companion</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowFocusAreas(!showFocusAreas)}
                  className="gap-2"
                >
                  {showFocusAreas ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  {selectedFocusAreas.length > 0 ? `${selectedFocusAreas.length} selected` : 'Select areas'}
                </Button>
              </div>
              
              {showFocusAreas && (
                <div className="mt-4 space-y-3">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {FOCUS_AREAS.map((area) => (
                      <Button
                        key={area.id}
                        variant={selectedFocusAreas.includes(area.id) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleFocusAreaToggle(area.id)}
                        className="justify-start gap-2 h-auto py-2"
                      >
                        <span>{area.emoji}</span>
                        <span className="text-xs">{area.label}</span>
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Mood Check - Compact and Secondary */}
        {!isViewMode && (
          <Card className="border border-muted">
            <CardContent className="px-6 py-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">Quick Mood Check</p>
                    <p className="text-xs text-muted-foreground">Optional - helps contextualize your entry</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-medium text-muted-foreground">Mood</label>
                      <span className="text-xs text-muted-foreground">{mood}/10</span>
                    </div>
                    <Slider
                      value={[mood]}
                      onValueChange={(value) => setMood(value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-medium text-muted-foreground">Energy</label>
                      <span className="text-xs text-muted-foreground">{energy}/10</span>
                    </div>
                    <Slider
                      value={[energy]}
                      onValueChange={(value) => setEnergy(value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-medium text-muted-foreground">Stress</label>
                      <span className="text-xs text-muted-foreground">{stress}/10</span>
                    </div>
                    <Slider
                      value={[stress]}
                      onValueChange={(value) => setStress(value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Emoji Reactions - Only show after substantial writing */}
        {showEmojiReactions && content.length > 100 && (
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

        {/* Actions - Prominent Save Button */}
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={handleBack}>
              Cancel
            </Button>
            {content.length > 50 && (
              <Button variant="ghost" size="sm" className="gap-2" disabled>
                <Save className={`w-4 h-4 ${autoSaving ? 'animate-spin' : ''}`} />
                {autoSaving ? 'Auto-saving...' : lastSaved ? `Saved ${lastSaved.toLocaleTimeString()}` : 'Draft ready'}
              </Button>
            )}
          </div>
          
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || content.trim().length < 10}
            size="lg"
            className="gap-2 min-w-[140px]"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Reflection
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default JournalEntry;
