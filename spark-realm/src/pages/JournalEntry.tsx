import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, useParams } from "react-router-dom";
import { ArrowLeft, Send, Lightbulb, Heart, Settings, Mic, MicOff, Image, X, Camera, Save, ChevronUp, ChevronDown, Target } from "lucide-react";
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
  
  // New UI states for photo-editing-like interface
  const [showMoodPanel, setShowMoodPanel] = useState(false);

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
        navigate('/?newEntry=true');
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
    <div className="min-h-screen bg-background flex flex-col">
      {/* Minimal Header - Like photo editing software */}
      <header className="h-12 bg-background/95 backdrop-blur-md border-b flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBack}
            className="gap-1 h-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div className="text-sm font-medium">
            {isViewMode ? "Reflection" : "New Entry"}
          </div>
        </div>
        
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{wordCount} words</span>
          {content.trim().length >= 10 ? (
            <span className="text-green-600 font-medium">✓ Ready</span>
          ) : (
            <span>{content.trim().length}/10 min</span>
          )}
        </div>
      </header>

      {/* Main Writing Canvas - Maximized like photo editing main canvas */}
      <div className="flex-1 flex relative">
        {/* Full-screen Writing Area */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-6">
            <div className="max-w-4xl mx-auto h-full">
              {/* Writing Area with Floating Controls */}
              <div className="relative h-full">
                <Textarea
                  id="journal-content"
                  placeholder="What's on your mind today?

Nothing is off-limits. Write freely about your thoughts, feelings, experiences, dreams, or anything that matters to you right now. This is your private space to explore your inner world.

Take your time - there's no rush, no judgment, just space for your authentic self..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full h-full min-h-[calc(100vh-200px)] border-0 bg-transparent text-foreground placeholder:text-muted-foreground/60 resize-none focus:ring-0 focus:outline-none text-lg leading-relaxed p-0 font-normal"
                  style={{ fontSize: "18px", lineHeight: "1.6" }}
                />
                
                {/* Floating Tool Buttons - Like photo editing tool palette */}
                <div className="absolute top-4 right-4 flex flex-col gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleVoiceInput}
                    disabled={isRecording}
                    className="h-10 w-10 p-0 rounded-full bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-background/90"
                    title={isRecording ? "Recording..." : "Voice Input"}
                  >
                    {isRecording ? (
                      <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse" />
                    ) : (
                      <Mic className="w-4 h-4" />
                    )}
                  </Button>
                  
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-10 w-10 p-0 rounded-full bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-background/90"
                    title="Add Image"
                  >
                    <Camera className="w-4 h-4" />
                  </Button>
                  
                  {!isViewMode && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowFocusAreas(!showFocusAreas)}
                      className="h-10 w-10 p-0 rounded-full bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-background/90"
                      title="Focus Areas"
                    >
                      <Target className="w-4 h-4" />
                    </Button>
                  )}
                </div>
                
                {/* Minimal Writing Encouragement */}
                {content.length > 0 && content.length < 50 && (
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground/60 animate-fade-in">
                    💭 Keep going...
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Expandable Side Panels - Like photo editing tool panels */}
        {/* Focus Areas Panel */}
        {showFocusAreas && !isViewMode && (
          <div className="w-80 border-l bg-background/50 backdrop-blur-sm p-4 animate-slide-in-right">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-sm">Focus Areas</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFocusAreas(false)}
                className="h-8 w-8 p-0"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="grid grid-cols-1 gap-2 max-h-80 overflow-y-auto">
              {FOCUS_AREAS.map((area) => (
                <Button
                  key={area.id}
                  variant={selectedFocusAreas.includes(area.id) ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleFocusAreaToggle(area.id)}
                  className="justify-start gap-2 h-auto py-2 px-3 text-left"
                >
                  <span className="text-sm">{area.emoji}</span>
                  <span className="text-xs">{area.label}</span>
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Action Bar - Like photo editing software bottom panel */}
      <div className="h-16 border-t bg-background/95 backdrop-blur-md flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleBack} size="sm">
            Cancel
          </Button>
          
          {/* Mood Quick Access - Expandable */}
          {!isViewMode && (
            <Button
              variant="ghost"
              size="sm"
              className="gap-2"
              onClick={() => setShowMoodPanel(!showMoodPanel)}
            >
              <Heart className="w-4 h-4" />
              Mood: {mood}/10
            </Button>
          )}
          
          {content.length > 50 && (
            <span className="text-xs text-muted-foreground flex items-center gap-2">
              <Save className={`w-3 h-3 ${autoSaving ? 'animate-spin' : ''}`} />
              {autoSaving ? 'Auto-saving...' : lastSaved ? `Saved ${lastSaved.toLocaleTimeString()}` : 'Draft ready'}
            </span>
          )}
        </div>
        
        <Button
          onClick={handleSubmit}
          disabled={isSubmitting || content.trim().length < 10}
          size="lg"
          className="gap-2 min-w-[120px]"
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Entry
            </>
          )}
        </Button>
      </div>

      {/* Floating Mood Panel - Expandable like photo editing properties panel */}
      {showMoodPanel && !isViewMode && (
        <div className="absolute bottom-20 left-6 w-80 bg-background border rounded-lg shadow-lg p-4 animate-slide-in-up backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-sm">Quick Mood Check</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowMoodPanel(false)}
              className="h-8 w-8 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium">Mood</label>
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
                <label className="text-xs font-medium">Energy</label>
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
                <label className="text-xs font-medium">Stress</label>
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
      )}

      {/* Voice Input Overlay */}
      {showVoiceInput && (
        <div className="absolute inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-background border rounded-lg shadow-xl p-6 max-w-md mx-4">
            <div className="flex items-center gap-3 text-foreground mb-4">
              <Mic className="w-6 h-6 animate-pulse text-red-500" />
              <div>
                <p className="font-medium">
                  {isRecording ? "Listening... Speak clearly" : "Voice input completed"}
                </p>
                <p className="text-sm text-muted-foreground">
                  Your voice will be transcribed and added to your journal
                </p>
              </div>
            </div>
            <Button 
              onClick={() => setShowVoiceInput(false)} 
              variant="outline" 
              className="w-full"
            >
              Close
            </Button>
          </div>
        </div>
      )}

      {/* Minimum character warning - floating */}
      {content.trim().length > 0 && content.trim().length < 10 && (
        <div className="absolute bottom-20 right-6 bg-red-50 border border-red-200 text-red-700 text-xs px-3 py-2 rounded-lg shadow-sm animate-fade-in">
          Please write at least 10 characters ({content.trim().length}/10)
        </div>
      )}
    </div>
  );
};

export default JournalEntry;
