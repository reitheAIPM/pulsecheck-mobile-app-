import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate, useSearchParams, useParams } from "react-router-dom";
import { ArrowLeft, Send, Lightbulb, Heart, Settings, Mic, MicOff, Image, X, Camera, Save, ChevronUp, ChevronDown, Target, Type, Bold, Italic, Underline, AlignLeft, AlignCenter, AlignRight, List, ListOrdered, Highlighter, Hash, Quote } from "lucide-react";
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
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";

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
  { id: "work_stress", label: "Work Stress", emoji: "💼", description: "Challenges and pressure at work, deadlines, or job-related stress." },
  { id: "anxiety", label: "Anxiety", emoji: "😰", description: "Feelings of worry, nervousness, or unease about things in your life." },
  { id: "relationships", label: "Relationships", emoji: "❤️", description: "Thoughts or feelings about friends, family, or romantic partners." },
  { id: "health", label: "Health & Wellness", emoji: "🏃‍♀️", description: "Physical or mental health, self-care, or wellness routines." },
  { id: "creativity", label: "Creativity", emoji: "🎨", description: "Creative projects, inspiration, or artistic expression." },
  { id: "motivation", label: "Motivation", emoji: "💪", description: "Drive, ambition, or struggles with motivation and energy." },
  { id: "sleep", label: "Sleep", emoji: "😴", description: "Sleep quality, rest, or feeling tired or refreshed." },
  { id: "purpose", label: "Life Purpose", emoji: "🌟", description: "Questions or thoughts about meaning, direction, or purpose in life." },
  { id: "loneliness", label: "Loneliness", emoji: "🤗", description: "Feeling alone, isolated, or disconnected from others." },
  { id: "grief", label: "Grief & Loss", emoji: "🕊️", description: "Coping with loss, sadness, or grief." },
  { id: "planning", label: "Planning & Goals", emoji: "📋", description: "Setting goals, making plans, or organizing your life." },
  { id: "reflection", label: "General Reflection", emoji: "💭", description: "General thoughts, self-reflection, or anything on your mind." }
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

  // New state for rich text editing
  const [showFormattingToolbar, setShowFormattingToolbar] = useState(false);
  const [showTopicsPanel, setShowTopicsPanel] = useState(false);
  const [fontSize, setFontSize] = useState(18);
  const [textColor, setTextColor] = useState('#000000');
  const [highlightColor, setHighlightColor] = useState('#ffff00');
  const [fontFamily, setFontFamily] = useState('system-ui');
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [isUnderlined, setIsUnderlined] = useState(false);
  const [textAlign, setTextAlign] = useState('left');
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Get current user ID from authenticated session
  const [userId, setUserId] = useState<string>("");

  // Add state to track last selected focus area for info display
  const [lastSelectedFocusArea, setLastSelectedFocusArea] = useState<string | null>(null);

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

  // Update toggleFocusArea to set last selected
  const toggleFocusArea = (areaId: string) => {
    setSelectedFocusAreas(prev => {
      if (prev.includes(areaId)) {
        // If removing, clear lastSelected if it was this one
        if (lastSelectedFocusArea === areaId) {
          setLastSelectedFocusArea(null);
        }
        return prev.filter(id => id !== areaId);
      } else {
        setLastSelectedFocusArea(areaId);
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

  // Rich text formatting functions
  const applyBold = () => {
    setIsBold(!isBold);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const applyItalic = () => {
    setIsItalic(!isItalic);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const applyUnderline = () => {
    setIsUnderlined(!isUnderlined);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const insertBulletPoint = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const beforeCursor = content.substring(0, start);
    const afterCursor = content.substring(end);
    
    // Check if we're at the start of a line
    const lastNewlineIndex = beforeCursor.lastIndexOf('\n');
    const currentLineStart = lastNewlineIndex === -1 ? 0 : lastNewlineIndex + 1;
    const currentLine = beforeCursor.substring(currentLineStart);
    
    let newContent;
    let newCursorPos;
    
    if (currentLine.trim() === '') {
      // Empty line, add bullet
      newContent = beforeCursor + '• ' + afterCursor;
      newCursorPos = start + 2;
    } else {
      // Add bullet on new line
      newContent = beforeCursor + '\n• ' + afterCursor;
      newCursorPos = start + 3;
    }
    
    setContent(newContent);
    
    // Set cursor position after state update
    setTimeout(() => {
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    }, 0);
  };

  const insertNumberedList = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const beforeCursor = content.substring(0, start);
    const afterCursor = content.substring(end);
    
    const lastNewlineIndex = beforeCursor.lastIndexOf('\n');
    const currentLineStart = lastNewlineIndex === -1 ? 0 : lastNewlineIndex + 1;
    const currentLine = beforeCursor.substring(currentLineStart);
    
    let newContent;
    let newCursorPos;
    
    if (currentLine.trim() === '') {
      newContent = beforeCursor + '1. ' + afterCursor;
      newCursorPos = start + 3;
    } else {
      newContent = beforeCursor + '\n1. ' + afterCursor;
      newCursorPos = start + 4;
    }
    
    setContent(newContent);
    
    setTimeout(() => {
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    }, 0);
  };

  const insertHeading = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const beforeCursor = content.substring(0, start);
    const afterCursor = content.substring(end);
    
    const lastNewlineIndex = beforeCursor.lastIndexOf('\n');
    const currentLineStart = lastNewlineIndex === -1 ? 0 : lastNewlineIndex + 1;
    const currentLine = beforeCursor.substring(currentLineStart);
    
    let newContent;
    let newCursorPos;
    
    if (currentLine.trim() === '') {
      newContent = beforeCursor + '# ' + afterCursor;
      newCursorPos = start + 2;
    } else {
      newContent = beforeCursor + '\n# ' + afterCursor;
      newCursorPos = start + 3;
    }
    
    setContent(newContent);
    
    setTimeout(() => {
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    }, 0);
  };

  const insertQuote = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const beforeCursor = content.substring(0, start);
    const afterCursor = content.substring(end);
    
    const lastNewlineIndex = beforeCursor.lastIndexOf('\n');
    const currentLineStart = lastNewlineIndex === -1 ? 0 : lastNewlineIndex + 1;
    const currentLine = beforeCursor.substring(currentLineStart);
    
    let newContent;
    let newCursorPos;
    
    if (currentLine.trim() === '') {
      newContent = beforeCursor + '> ' + afterCursor;
      newCursorPos = start + 2;
    } else {
      newContent = beforeCursor + '\n> ' + afterCursor;
      newCursorPos = start + 3;
    }
    
    setContent(newContent);
    
    setTimeout(() => {
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    }, 0);
  };

  // Handle topics inline
  const handleTopicsToggle = () => {
    setShowTopicsPanel(!showTopicsPanel);
    if (!showTopicsPanel && content.trim().length > 20) {
      detectTopics();
    }
  };

  const getTextStyle = () => ({
    fontSize: `${fontSize}px`,
    fontFamily: fontFamily,
    color: textColor,
    fontWeight: isBold ? 'bold' : 'normal',
    fontStyle: isItalic ? 'italic' : 'normal',
    textDecoration: isUnderlined ? 'underline' : 'none',
    textAlign: textAlign as any,
    lineHeight: '1.6'
  });

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
        <div className="flex-1 flex flex-col w-full">
          {/* Rich Text Formatting Toolbar - More compact */}
          {showFormattingToolbar && !isViewMode && (
            <div className="border-b bg-background/50 backdrop-blur-sm py-1 animate-slide-in-up">
              <div className="w-full flex items-center gap-1 flex-wrap justify-center px-4 sm:px-8 md:px-12 lg:px-16 xl:px-20">
                {/* Font Family */}
                <select 
                  value={fontFamily} 
                  onChange={(e) => setFontFamily(e.target.value)}
                  className="px-1 py-0.5 text-xs border rounded bg-background"
                >
                  <option value="system-ui">System</option>
                  <option value="serif">Serif</option>
                  <option value="monospace">Mono</option>
                  <option value="cursive">Script</option>
                  <option value="fantasy">Display</option>
                </select>

                {/* Font Size */}
                <input
                  type="range"
                  min="12"
                  max="32"
                  value={fontSize}
                  onChange={(e) => setFontSize(Number(e.target.value))}
                  className="w-16 h-5"
                />
                <span className="text-xs w-6">{fontSize}</span>

                <div className="w-px h-5 bg-border mx-1" />

                {/* Text Formatting */}
                <Button
                  variant={isBold ? "default" : "ghost"}
                  size="sm"
                  onClick={applyBold}
                  className="h-6 w-6 p-0"
                >
                  <Bold className="w-3 h-3" />
                </Button>
                <Button
                  variant={isItalic ? "default" : "ghost"}
                  size="sm"
                  onClick={applyItalic}
                  className="h-6 w-6 p-0"
                >
                  <Italic className="w-3 h-3" />
                </Button>
                <Button
                  variant={isUnderlined ? "default" : "ghost"}
                  size="sm"
                  onClick={applyUnderline}
                  className="h-6 w-6 p-0"
                >
                  <Underline className="w-3 h-3" />
                </Button>

                <div className="w-px h-5 bg-border mx-1" />

                {/* Text Color */}
                <div className="flex items-center gap-1">
                  <input
                    type="color"
                    value={textColor}
                    onChange={(e) => setTextColor(e.target.value)}
                    className="w-6 h-6 border rounded cursor-pointer"
                    title="Text Color"
                  />
                  <input
                    type="color"
                    value={highlightColor}
                    onChange={(e) => setHighlightColor(e.target.value)}
                    className="w-6 h-6 border rounded cursor-pointer"
                    title="Highlight Color"
                  />
                </div>

                <div className="w-px h-5 bg-border mx-1" />

                {/* Lists & Structure */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={insertBulletPoint}
                  className="h-6 w-6 p-0"
                  title="Bullet Point"
                >
                  <List className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={insertNumberedList}
                  className="h-6 w-6 p-0"
                  title="Numbered List"
                >
                  <ListOrdered className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={insertHeading}
                  className="h-6 w-6 p-0"
                  title="Heading"
                >
                  <Hash className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={insertQuote}
                  className="h-6 w-6 p-0"
                  title="Quote"
                >
                  <Quote className="w-3 h-3" />
                </Button>

                <div className="ml-auto">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowFormattingToolbar(false)}
                    className="h-6 w-6 p-0"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </div>
          )}

          <div className="flex-1 px-2 sm:px-4 md:px-6 lg:px-8 xl:px-12">
            <div className="w-full h-full">
              {/* Writing Area with Floating Controls */}
              <div className="relative h-full">
                <Textarea
                  ref={textareaRef}
                  id="journal-content"
                  placeholder="What's on your mind today?\n\nNothing is off-limits. Write freely about your thoughts, feelings, experiences, dreams, or anything that matters to you right now. This is your private space to explore your inner world.\n\nTake your time - there's no rush, no judgment, just space for your authentic self..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full h-full min-h-[400px] max-h-[500px] border-0 bg-transparent text-foreground placeholder:text-muted-foreground/60 resize-none focus:ring-0 focus:outline-none text-lg leading-relaxed p-6 font-normal rounded-lg border border-border/20"
                  style={getTextStyle()}
                />
                
                {/* Clean writing area - tools moved to bottom */}
                
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
      </div>

      {/* Bottom Tool Bar - Outside the writing area, more compact */}
      <div className="border-t bg-background/95 backdrop-blur-md py-2 px-2 sm:px-4 md:px-6 lg:px-8 xl:px-12">
        <div className="w-full">
          {/* Creative Tools Row - More compact layout */}
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="flex items-center gap-1 flex-wrap justify-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFormattingToolbar(!showFormattingToolbar)}
                className="gap-1 px-2 h-8"
                title="Formatting Tools"
              >
                <Type className="w-3 h-3" />
                <span className="text-xs">Format</span>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleVoiceInput}
                disabled={isRecording}
                className="gap-1 px-2 h-8"
                title={isRecording ? "Recording..." : "Voice Input"}
              >
                {isRecording ? (
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                ) : (
                  <Mic className="w-3 h-3" />
                )}
                <span className="text-xs">Voice</span>
              </Button>
              
              <Button 
                variant="ghost" 
                size="sm" 
                className="gap-1 px-2 h-8"
                title="Add Image"
              >
                <Camera className="w-3 h-3" />
                <span className="text-xs">Photo</span>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFocusAreas(!showFocusAreas)}
                className="gap-1 px-2 h-8"
                title="Focus Areas"
              >
                <Target className="w-3 h-3" />
                <span className="text-xs">Focus</span>
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleTopicsToggle}
                className="gap-1 px-2 h-8"
                title="Topics"
              >
                <Hash className="w-3 h-3" />
                <span className="text-xs">Topics</span>
              </Button>

              {/* Mood Quick Access */}
              {!isViewMode && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="gap-1 px-2 h-8"
                  onClick={() => setShowMoodPanel(!showMoodPanel)}
                >
                  <Heart className="w-3 h-3" />
                  <span className="text-xs">Mood: {mood}/10</span>
                </Button>
              )}
              
              {content.length > 50 && (
                <span className="text-xs text-muted-foreground flex items-center gap-1 px-2">
                  <Save className={`w-3 h-3 ${autoSaving ? 'animate-spin' : ''}`} />
                  {autoSaving ? 'Saving...' : lastSaved ? `Saved ${lastSaved.toLocaleTimeString()}` : 'Draft'}
                </span>
              )}
            </div>
          </div>

          {/* Action Buttons Row - More compact */}
          <div className="flex items-center justify-between">
            <Button variant="outline" onClick={handleBack} size="sm" className="h-8 text-xs">
              Cancel
            </Button>
            
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || content.trim().length < 10}
              size="sm"
              className="gap-1 min-w-[100px] h-8"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span className="text-xs">Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-3 h-3" />
                  <span className="text-xs">Save Entry</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Inline Panels - More compact and better positioned */}
      {/* Focus Areas Panel - Inline above toolbar */}
      {showFocusAreas && !isViewMode && (
        <div className="border-t bg-background/50 backdrop-blur-sm animate-slide-in-up">
          <div className="px-4 sm:px-8 md:px-12 lg:px-16 xl:px-20 py-2">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-medium text-xs">Focus Areas</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFocusAreas(false)}
                className="h-5 w-5 p-0"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
            <TooltipProvider>
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-1">
              {FOCUS_AREAS.map((area) => (
                <Tooltip key={area.id}>
                  <TooltipTrigger asChild>
                    <Button
                      variant={selectedFocusAreas.includes(area.id) ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleFocusArea(area.id)}
                      className="justify-center items-center gap-0.5 h-6 py-0 px-1 text-center"
                    >
                      <span className="text-xs">{area.emoji}</span>
                      <span className="text-[10px] truncate">{area.label}</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs text-xs">
                    {area.description}
                  </TooltipContent>
                </Tooltip>
              ))}
            </div>
            </TooltipProvider>
            {/* Persistent info box for selected focus area(s) */}
            {(selectedFocusAreas.length > 0) && (
              <div className="mt-2 p-2 rounded bg-muted/40 border text-xs max-w-2xl">
                {selectedFocusAreas.map(id => {
                  const area = FOCUS_AREAS.find(a => a.id === id);
                  return area ? (
                    <div key={id} className="mb-1 last:mb-0">
                      <span className="font-semibold mr-1">{area.emoji} {area.label}:</span>
                      <span>{area.description}</span>
                    </div>
                  ) : null;
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Topics Panel - Inline above toolbar, more compact */}
      {showTopicsPanel && !isViewMode && (
        <div className="border-t bg-background/50 backdrop-blur-sm animate-slide-in-up">
          <div className="px-4 sm:px-8 md:px-12 lg:px-16 xl:px-20 py-2">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-medium text-xs">Detected Topics</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowTopicsPanel(false)}
                className="h-5 w-5 p-0"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
            
            {detectedTopics.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {detectedTopics.map((topic, index) => (
                  <Badge key={index} variant="secondary" className="text-[10px] py-0 px-1">
                    {topic.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            ) : content.trim().length > 20 ? (
              <div className="text-xs text-muted-foreground text-center py-1">
                <div className="animate-pulse">Analyzing your entry...</div>
              </div>
            ) : (
              <div className="text-xs text-muted-foreground text-center py-1">
                Write more to detect topics
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mood Panel - Inline above toolbar, more compact */}
      {showMoodPanel && !isViewMode && (
        <div className="border-t bg-background/50 backdrop-blur-sm animate-slide-in-up">
          <div className="px-4 sm:px-8 md:px-12 lg:px-16 xl:px-20 py-2">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-medium text-xs">Quick Mood Check</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowMoodPanel(false)}
                className="h-5 w-5 p-0"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
            
            <div className="grid grid-cols-3 gap-2">
              <div className="space-y-0.5">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-medium">Mood</label>
                  <span className="text-[10px] text-muted-foreground">{mood}/10</span>
                </div>
                <Slider
                  value={[mood]}
                  onValueChange={(value) => setMood(value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full h-4"
                />
              </div>
              
              <div className="space-y-0.5">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-medium">Energy</label>
                  <span className="text-[10px] text-muted-foreground">{energy}/10</span>
                </div>
                <Slider
                  value={[energy]}
                  onValueChange={(value) => setEnergy(value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full h-4"
                />
              </div>
              
              <div className="space-y-0.5">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-medium">Stress</label>
                  <span className="text-[10px] text-muted-foreground">{stress}/10</span>
                </div>
                <Slider
                  value={[stress]}
                  onValueChange={(value) => setStress(value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full h-4"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Voice Input Overlay - More compact */}
      {showVoiceInput && (
        <div className="absolute inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-background border rounded-lg shadow-xl p-4 max-w-xs mx-4">
            <div className="flex items-center gap-2 text-foreground mb-3">
              <Mic className="w-5 h-5 animate-pulse text-red-500" />
              <div>
                <p className="font-medium text-sm">
                  {isRecording ? "Listening..." : "Voice input completed"}
                </p>
                <p className="text-xs text-muted-foreground">
                  Your voice will be transcribed
                </p>
              </div>
            </div>
            <Button 
              onClick={() => setShowVoiceInput(false)} 
              variant="outline" 
              className="w-full h-8 text-xs"
            >
              Close
            </Button>
          </div>
        </div>
      )}

      {/* Minimum character warning - floating */}
      {content.trim().length > 0 && content.trim().length < 10 && (
        <div className="absolute bottom-20 right-6 bg-red-50 border border-red-200 text-red-700 text-xs px-2 py-1 rounded-lg shadow-sm animate-fade-in">
          Please write at least 10 characters ({content.trim().length}/10)
        </div>
      )}
    </div>
  );
};

export default JournalEntry;
