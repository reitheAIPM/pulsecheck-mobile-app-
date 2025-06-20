import { useState } from "react";
import { Heart, MessageCircle, Clock, Brain } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

interface JournalEntry {
  id: string;
  content: string;
  mood: number;
  timestamp: string;
  aiResponse?: {
    emoji?: string;
    comments: string[];
    timestamp: string;
  };
}

interface JournalCardProps {
  entry: JournalEntry;
  onPulseClick?: (entryId: string) => void;
}

export function JournalCard({ entry, onPulseClick }: JournalCardProps) {
  const [liked, setLiked] = useState(false);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return "just now";
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return "yesterday";
    return `${diffDays}d ago`;
  };

  const getMoodEmoji = (mood: number) => {
    if (mood <= 2) return "😔";
    if (mood <= 4) return "😐";
    if (mood <= 6) return "🙂";
    if (mood <= 8) return "😊";
    return "😄";
  };

  const truncateContent = (content: string, maxLength: number = 280) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + "...";
  };

  return (
    <Card className="w-full bg-card border hover:border-primary/20 transition-colors duration-200">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-pulse-400 to-pulse-500"></div>
            <span className="text-sm font-medium text-calm-700">
              Your reflection
            </span>
            <span className="text-sm text-calm-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatTimestamp(entry.timestamp)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">{getMoodEmoji(entry.mood)}</span>
            <span className="text-xs text-calm-500 bg-calm-100 px-2 py-1 rounded-full">
              {entry.mood}/10
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="mb-4">
          <p className="text-calm-800 leading-relaxed whitespace-pre-wrap">
            {truncateContent(entry.content)}
          </p>
        </div>

        {/* AI Response */}
        {entry.aiResponse && (
          <div className="border-l-2 border-primary/30 pl-4 mb-4 bg-muted/30 -ml-1 py-3 rounded-r-md">
            <div className="flex items-start gap-3">
              <Avatar className="w-6 h-6 ring-2 ring-pulse-200">
                <AvatarFallback className="bg-gradient-to-br from-pulse-400 to-pulse-500 text-white text-xs">
                  <Brain className="w-3 h-3" />
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-pulse-700">
                    Pulse
                  </span>
                  <span className="text-xs text-calm-500">
                    {formatTimestamp(entry.aiResponse.timestamp)}
                  </span>
                  {entry.aiResponse.emoji && (
                    <span className="text-sm">{entry.aiResponse.emoji}</span>
                  )}
                </div>
                <div className="space-y-1">
                  {entry.aiResponse.comments.map((comment, index) => (
                    <p
                      key={index}
                      className="text-sm text-calm-700 leading-relaxed"
                    >
                      {comment}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLiked(!liked)}
              className={cn(
                "gap-2 text-calm-600 hover:text-pulse-600 transition-colors",
                liked && "text-pulse-600",
              )}
            >
              <Heart className={cn("w-4 h-4", liked && "fill-current")} />
              <span className="text-sm">Reflect</span>
            </Button>

            {entry.aiResponse && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onPulseClick?.(entry.id)}
                className="gap-2 text-calm-600 hover:text-pulse-600 transition-colors"
              >
                <MessageCircle className="w-4 h-4" />
                <span className="text-sm">Reply to Pulse</span>
              </Button>
            )}
          </div>

          {!entry.aiResponse && (
            <div className="flex items-center gap-2 text-xs text-calm-500">
              <div className="w-2 h-2 rounded-full bg-calm-300 animate-pulse"></div>
              <span>Pulse is reflecting...</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
