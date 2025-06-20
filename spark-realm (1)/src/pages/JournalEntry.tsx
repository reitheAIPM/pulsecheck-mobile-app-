import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Send, Lightbulb, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MoodTracker } from "@/components/MoodTracker";

const promptsOfTheDay = [
  "What's one thing that challenged you today, and how did you handle it?",
  "Describe a moment today when you felt most like yourself.",
  "If you could change one thing about your workday, what would it be?",
  "What's something you're grateful for right now?",
  "How are you feeling about the balance between work and personal time?",
  "What would you tell a friend who was experiencing what you're experiencing right now?",
];

const JournalEntry = () => {
  const navigate = useNavigate();
  const [content, setContent] = useState("");
  const [mood, setMood] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentPrompt] = useState(
    promptsOfTheDay[Math.floor(Math.random() * promptsOfTheDay.length)],
  );

  const handleSubmit = async () => {
    if (!content.trim()) return;

    setIsSubmitting(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // In a real app, this would save to backend
    console.log({ content, mood, timestamp: new Date().toISOString() });

    setIsSubmitting(false);
    navigate("/");
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
            <div>
              <h1 className="text-lg font-semibold">New Reflection</h1>
              <p className="text-sm text-muted-foreground">
                Take your time, this is your space
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* Prompt of the Day */}
          <Card className="bg-muted/50">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-primary text-base">
                <Lightbulb className="w-4 h-4" />
                Reflection prompt
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-calm-700 leading-relaxed italic">
                "{currentPrompt}"
              </p>
              <p className="text-xs text-calm-500 mt-2">
                Optional - feel free to write about anything on your mind
              </p>
            </CardContent>
          </Card>

          {/* Mood Tracker */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-calm-700 text-base">
                <Heart className="w-4 h-4" />
                How are you feeling?
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <MoodTracker value={mood} onChange={setMood} />
            </CardContent>
          </Card>

          {/* Journal Entry */}
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="journal-content"
                    className="text-sm font-medium text-calm-700"
                  >
                    Your reflection
                  </label>
                  <span className="text-xs text-calm-500">
                    {wordCount} words
                  </span>
                </div>

                <Textarea
                  id="journal-content"
                  placeholder="What's on your mind? Write freely about your thoughts, feelings, or experiences..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="min-h-[200px] border-0 bg-transparent text-calm-800 placeholder:text-calm-400 resize-none focus:ring-0 focus:outline-none text-base leading-relaxed"
                  style={{ fontSize: "16px" }} // Prevent zoom on iOS
                />
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-calm-500">
              Your reflection will be private and secure
            </div>

            <Button
              onClick={handleSubmit}
              disabled={!content.trim() || isSubmitting}
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
        </div>

        {/* Tips */}
        <div className="mt-8 p-4 bg-calm-50/50 rounded-xl">
          <h3 className="text-sm font-medium text-calm-700 mb-2">
            Tips for reflection
          </h3>
          <ul className="text-sm text-calm-600 space-y-1">
            <li>• Write without judgment - this is your safe space</li>
            <li>• Focus on how you're feeling, not just what happened</li>
            <li>• Be honest with yourself - it's okay to struggle</li>
            <li>• Pulse will check in with thoughtful responses later</li>
          </ul>
        </div>
      </main>
    </div>
  );
};

export default JournalEntry;
