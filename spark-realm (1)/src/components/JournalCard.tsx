import { useState } from "react";
import { Heart, MessageCircle, Clock, Brain, Share2, MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

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
  const [isExpanded, setIsExpanded] = useState(false);

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

  const getMoodColor = (mood: number) => {
    if (mood <= 2) return "text-red-500 bg-red-50";
    if (mood <= 4) return "text-orange-500 bg-orange-50";
    if (mood <= 6) return "text-yellow-500 bg-yellow-50";
    if (mood <= 8) return "text-green-500 bg-green-50";
    return "text-blue-500 bg-blue-50";
  };

  const truncateContent = (content: string, maxLength: number = 280) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + "...";
  };

  const handleLike = () => {
    setLiked(!liked);
    // Add haptic feedback for mobile
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: "My Reflection",
        text: entry.content.substring(0, 100) + "...",
        url: window.location.href,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(entry.content);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(entry.content);
  };

  return (
    <Card className="w-full bg-card border hover:border-primary/20 transition-all duration-300 hover:shadow-md group">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-pulse-400 to-pulse-500 animate-pulse"></div>
            <span className="text-sm font-medium text-calm-700">
              Your reflection
            </span>
            <span className="text-sm text-calm-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatTimestamp(entry.timestamp)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg transition-transform hover:scale-110">{getMoodEmoji(entry.mood)}</span>
            <span className={cn(
              "text-xs px-2 py-1 rounded-full font-medium transition-colors",
              getMoodColor(entry.mood)
            )}>
              {entry.mood}/10
            </span>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreHorizontal className="w-4 h-4" />
                  <span className="sr-only">More options</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleCopy}>
                  Copy text
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleShare}>
                  Share
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Content */}
        <div className="mb-4">
          <p className="text-calm-800 leading-relaxed whitespace-pre-wrap cursor-pointer" 
             onClick={() => setIsExpanded(!isExpanded)}>
            {isExpanded ? entry.content : truncateContent(entry.content)}
          </p>
          {entry.content.length > 280 && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-sm text-pulse-600 hover:text-pulse-700 font-medium mt-2 transition-colors"
            >
              {isExpanded ? "Show less" : "Read more"}
            </button>
          )}
        </div>

        {/* AI Response */}
        {entry.aiResponse && (
          <div className="border-l-2 border-primary/30 pl-4 mb-4 bg-muted/30 -ml-1 py-3 rounded-r-md transition-all duration-200 hover:bg-muted/50">
            <div className="flex items-start gap-3">
              <Avatar className="w-6 h-6 ring-2 ring-pulse-200 transition-transform hover:scale-110">
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
                    <span className="text-sm animate-bounce">{entry.aiResponse.emoji}</span>
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
              onClick={handleLike}
              className={cn(
                "gap-2 text-calm-600 hover:text-pulse-600 transition-all duration-200 hover:scale-105 active:scale-95",
                liked && "text-pulse-600",
              )}
              aria-label={liked ? "Unlike reflection" : "Like reflection"}
            >
              <Heart className={cn("w-4 h-4 transition-all duration-200", liked && "fill-current scale-110")} />
              <span className="text-sm">{liked ? "Liked" : "Reflect"}</span>
            </Button>

            {entry.aiResponse && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onPulseClick?.(entry.id)}
                className="gap-2 text-calm-600 hover:text-pulse-600 transition-all duration-200 hover:scale-105 active:scale-95"
                aria-label="Reply to Pulse"
              >
                <MessageCircle className="w-4 h-4" />
                <span className="text-sm">Reply to Pulse</span>
              </Button>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={handleShare}
              className="gap-2 text-calm-600 hover:text-pulse-600 transition-all duration-200 hover:scale-105 active:scale-95 opacity-0 group-hover:opacity-100"
              aria-label="Share reflection"
            >
              <Share2 className="w-4 h-4" />
              <span className="text-sm">Share</span>
            </Button>
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
