import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Heart, Sparkles, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { JournalCard } from "@/components/JournalCard";

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
  const [entries, setEntries] = useState(mockEntries);

  const handlePulseClick = (entryId: string) => {
    navigate(`/pulse/${entryId}`);
  };

  const handleNewEntry = () => {
    navigate("/new-entry");
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">PulseCheck</h1>
                <p className="text-sm text-muted-foreground">
                  Your reflection space
                </p>
              </div>
            </div>

            <Button onClick={handleNewEntry} className="gap-2">
              <Plus className="w-4 h-4" />
              Reflect
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Welcome Message */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-1.5 rounded-md text-sm font-medium mb-3">
            <Sparkles className="w-4 h-4" />
            Welcome back
          </div>
          <p className="text-muted-foreground max-w-sm mx-auto">
            Take a moment to check in with yourself. How are you feeling today?
          </p>
        </div>

        {/* Quick Action */}
        <div className="mb-6">
          <Button
            onClick={handleNewEntry}
            variant="outline"
            className="w-full h-14 border-2 border-dashed hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Plus className="w-5 h-5" />
              <span>What's on your mind today?</span>
            </div>
          </Button>
        </div>

        {/* Journal Feed */}
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-sm text-calm-600 mb-4">
            <Heart className="w-4 h-4" />
            <span>Your recent reflections</span>
          </div>

          {entries.length > 0 ? (
            entries.map((entry) => (
              <JournalCard
                key={entry.id}
                entry={entry}
                onPulseClick={handlePulseClick}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-full bg-pulse-100 flex items-center justify-center mx-auto mb-4">
                <Heart className="w-8 h-8 text-pulse-500" />
              </div>
              <h3 className="text-lg font-medium text-calm-800 mb-2">
                Start your reflection journey
              </h3>
              <p className="text-calm-600 mb-6 max-w-sm mx-auto">
                Your first journal entry is just a click away. Take a moment to
                check in with yourself.
              </p>
              <Button
                onClick={handleNewEntry}
                className="gap-2 bg-gradient-to-r from-pulse-500 to-pulse-600 hover:from-pulse-600 hover:to-pulse-700 text-white rounded-xl"
              >
                <Plus className="w-4 h-4" />
                Write your first reflection
              </Button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center py-8 text-sm text-calm-500">
          <p>Your reflections are private and secure</p>
        </div>
      </main>
    </div>
  );
};

export default Index;
