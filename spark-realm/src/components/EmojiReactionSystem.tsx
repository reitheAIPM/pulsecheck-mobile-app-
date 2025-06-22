import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface EmojiReaction {
  emoji: string;
  label: string;
  context: string;
  trigger_topics: string[];
  follow_up_prompt?: string;
}

interface EmojiReactionSystemProps {
  journalContent: string;
  detectedTopics: string[];
  onReactionSelect: (reaction: EmojiReaction) => void;
  className?: string;
}

// Contextual emoji reactions based on detected topics and sentiment
const EMOJI_REACTIONS: EmojiReaction[] = [
  {
    emoji: "💭",
    label: "Thoughtful",
    context: "For reflective, contemplative entries",
    trigger_topics: ["reflection", "planning", "purpose", "grief"],
    follow_up_prompt: "What insights are emerging from this reflection?"
  },
  {
    emoji: "💪",
    label: "Strength",
    context: "For motivational, resilience-focused entries",
    trigger_topics: ["motivation", "work_stress", "challenges", "goals"],
    follow_up_prompt: "What's one small step you can take to build on this strength?"
  },
  {
    emoji: "🧠",
    label: "Clarity",
    context: "For analytical, problem-solving entries",
    trigger_topics: ["work_stress", "planning", "anxiety", "decisions"],
    follow_up_prompt: "What patterns are you noticing in your thinking?"
  },
  {
    emoji: "❤️",
    label: "Heart",
    context: "For emotional, relationship-focused entries",
    trigger_topics: ["relationships", "loneliness", "love", "connection"],
    follow_up_prompt: "How might you nurture this feeling or connection?"
  },
  {
    emoji: "🌟",
    label: "Inspiration",
    context: "For creative, aspirational entries",
    trigger_topics: ["creativity", "purpose", "dreams", "inspiration"],
    follow_up_prompt: "What would it look like to take this inspiration further?"
  },
  {
    emoji: "🤗",
    label: "Comfort",
    context: "For vulnerable, support-seeking entries",
    trigger_topics: ["anxiety", "loneliness", "grief", "overwhelm"],
    follow_up_prompt: "What kind of support would feel most helpful right now?"
  },
  {
    emoji: "🔥",
    label: "Energy",
    context: "For passionate, energetic entries",
    trigger_topics: ["motivation", "excitement", "goals", "breakthrough"],
    follow_up_prompt: "How can you channel this energy into meaningful action?"
  },
  {
    emoji: "🌱",
    label: "Growth",
    context: "For learning, development-focused entries",
    trigger_topics: ["learning", "growth", "challenges", "progress"],
    follow_up_prompt: "What growth do you notice in yourself from this experience?"
  },
  {
    emoji: "😴",
    label: "Rest",
    context: "For exhaustion, rest-focused entries",
    trigger_topics: ["sleep", "exhaustion", "burnout", "recovery"],
    follow_up_prompt: "What would truly restorative rest look like for you?"
  },
  {
    emoji: "⚡",
    label: "Breakthrough",
    context: "For insight, revelation entries",
    trigger_topics: ["insight", "breakthrough", "clarity", "understanding"],
    follow_up_prompt: "How might this breakthrough change your perspective going forward?"
  }
];

const EmojiReactionSystem: React.FC<EmojiReactionSystemProps> = ({
  journalContent,
  detectedTopics,
  onReactionSelect,
  className = ""
}) => {
  const [selectedReaction, setSelectedReaction] = useState<EmojiReaction | null>(null);
  const [showAllReactions, setShowAllReactions] = useState(false);

  // Get contextually relevant reactions based on detected topics
  const getRelevantReactions = (): EmojiReaction[] => {
    const relevantReactions = EMOJI_REACTIONS.filter(reaction =>
      reaction.trigger_topics.some(topic => detectedTopics.includes(topic))
    );

    // If no specific matches, return a default set
    if (relevantReactions.length === 0) {
      return [
        EMOJI_REACTIONS.find(r => r.emoji === "💭")!,
        EMOJI_REACTIONS.find(r => r.emoji === "💪")!,
        EMOJI_REACTIONS.find(r => r.emoji === "❤️")!
      ];
    }

    // Return top 3-4 most relevant reactions
    return relevantReactions.slice(0, 4);
  };

  // Analyze content sentiment for additional context
  const analyzeSentiment = (): string => {
    const content = journalContent.toLowerCase();
    
    const positiveWords = ["happy", "excited", "grateful", "accomplished", "proud", "energized"];
    const negativeWords = ["sad", "anxious", "overwhelmed", "frustrated", "tired", "stressed"];
    const neutralWords = ["thinking", "reflecting", "considering", "planning", "wondering"];

    const positiveCount = positiveWords.filter(word => content.includes(word)).length;
    const negativeCount = negativeWords.filter(word => content.includes(word)).length;
    const neutralCount = neutralWords.filter(word => content.includes(word)).length;

    if (positiveCount > negativeCount && positiveCount > neutralCount) return "positive";
    if (negativeCount > positiveCount && negativeCount > neutralCount) return "negative";
    return "neutral";
  };

  const handleReactionSelect = (reaction: EmojiReaction) => {
    setSelectedReaction(reaction);
    onReactionSelect(reaction);
  };

  const relevantReactions = showAllReactions ? EMOJI_REACTIONS : getRelevantReactions();
  const sentiment = analyzeSentiment();

  return (
    <Card className={`bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 ${className}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-700">
                How does this entry feel to you?
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                Choose an emoji that captures the essence of your reflection
              </p>
            </div>
            {detectedTopics.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {detectedTopics.slice(0, 2).map(topic => (
                  <Badge key={topic} variant="secondary" className="text-xs">
                    {topic.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Emoji Reactions Grid */}
          <div className="grid grid-cols-4 gap-2">
            {relevantReactions.map((reaction) => (
              <Button
                key={reaction.emoji}
                variant={selectedReaction?.emoji === reaction.emoji ? "default" : "outline"}
                size="sm"
                onClick={() => handleReactionSelect(reaction)}
                className={`flex flex-col h-auto p-3 transition-all ${
                  selectedReaction?.emoji === reaction.emoji 
                    ? "bg-blue-500 text-white scale-105" 
                    : "hover:scale-102 hover:bg-blue-50"
                }`}
              >
                <span className="text-lg mb-1">{reaction.emoji}</span>
                <span className="text-xs font-medium">{reaction.label}</span>
              </Button>
            ))}
          </div>

          {/* Show More/Less Toggle */}
          <div className="flex justify-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAllReactions(!showAllReactions)}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              {showAllReactions ? "Show fewer options" : "See all reactions"}
            </Button>
          </div>

          {/* Selected Reaction Follow-up */}
          {selectedReaction && selectedReaction.follow_up_prompt && (
            <div className="mt-4 p-3 bg-white/70 rounded-lg border border-blue-200">
              <div className="flex items-start gap-2">
                <span className="text-lg">{selectedReaction.emoji}</span>
                <div>
                  <p className="text-sm text-gray-700 font-medium">
                    {selectedReaction.label} reflection
                  </p>
                  <p className="text-sm text-gray-600 mt-1 italic">
                    "{selectedReaction.follow_up_prompt}"
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Contextual Insight */}
          <div className="text-center">
            <p className="text-xs text-gray-500">
              Detected sentiment: <span className="capitalize font-medium">{sentiment}</span>
              {detectedTopics.length > 0 && (
                <span> • Topics: {detectedTopics.slice(0, 3).join(", ")}</span>
              )}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EmojiReactionSystem; 