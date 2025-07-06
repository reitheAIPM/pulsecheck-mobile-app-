import React, { useState, useEffect } from 'react';
import { Calendar, Heart, MessageCircle, MoreHorizontal, Trash2, Copy, Sparkles, Send, User, BookOpen, Shield, Zap } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { formatDistanceToNow } from 'date-fns';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { apiService, UserReply } from '@/services/api';
import { toast } from '@/hooks/use-toast';
import { authService } from '@/services/authService';

interface JournalCardProps {
  id: string;
  content: string;
  mood: number;
  timestamp: string;
  tags?: string[];
  aiResponse?: {
    comments: Array<string | {
      text: string;
      persona: string;
      timestamp: string;
      confidence?: number;
    }>;
    timestamp: string;
    emoji?: string;
    personas_responded?: string[];
  };
  currentUser?: {
    id: string;
    email: string;
    user_metadata?: {
      full_name?: string;
      name?: string;
    };
  };
  onDelete?: (id: string) => void;
  onPulseClick?: (id: string) => void;
}

export const JournalCard: React.FC<JournalCardProps> = ({
  id,
  content,
  mood,
  timestamp,
  tags = [],
  aiResponse,
  currentUser,
  onDelete,
  onPulseClick
}) => {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [liked, setLiked] = useState(false);
  const [showFullContent, setShowFullContent] = useState(false);
  const [aiResponseHelpful, setAiResponseHelpful] = useState(false);
  const [showReplyInput, setShowReplyInput] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [userReplies, setUserReplies] = useState<UserReply[]>([]);
  const [isLoadingReplies, setIsLoadingReplies] = useState(false);

  // Fetch user replies when component mounts or when aiResponse changes
  useEffect(() => {
    if (aiResponse && aiResponse.comments && aiResponse.comments.length > 0) {
      fetchUserReplies();
    }
  }, [id, aiResponse]);

  const fetchUserReplies = async () => {
    setIsLoadingReplies(true);
    try {
      const replies = await apiService.getUserReplies(id);
      setUserReplies(replies);
    } catch (error) {
      console.error('Failed to fetch user replies:', error);
    } finally {
      setIsLoadingReplies(false);
    }
  };

  const getMoodColor = (mood: number) => {
    if (mood >= 8) return 'bg-green-100 text-green-800 border-green-200';
    if (mood >= 6) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (mood >= 4) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const getMoodEmoji = (mood: number) => {
    if (mood >= 8) return '😊';
    if (mood >= 6) return '🙂';
    if (mood >= 4) return '😐';
    return '😔';
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await apiService.deleteJournalEntry(id);
      if (onDelete) {
        onDelete(id);
      }
    } catch (error) {
      console.error('Failed to delete entry:', error);
    } finally {
      setIsDeleting(false);
      setDeleteDialogOpen(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (error) {
      console.error('Failed to copy content:', error);
    }
  };

  const handleHelpfulClick = async () => {
    if (isSubmittingFeedback) return;
    
    setIsSubmittingFeedback(true);
    try {
      await apiService.submitAIFeedback(id, 'helpful', !aiResponseHelpful);
      setAiResponseHelpful(!aiResponseHelpful);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const handleReplySubmit = async () => {
    if (!replyText.trim() || isSubmittingFeedback) return;
    
    setIsSubmittingFeedback(true);
    try {
      await apiService.submitAIReply(id, replyText.trim());
      setReplyText("");
      setShowReplyInput(false);
      // Refresh the replies to show the new one
      await fetchUserReplies();
    } catch (error) {
      console.error('Failed to submit reply:', error);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const shouldTruncateContent = content.length > 800;
  const displayContent = shouldTruncateContent && !showFullContent
    ? content.substring(0, 800) + '...'
    : content;

  return (
    <>
      <Card className="w-full max-w-none hover:shadow-md transition-all duration-200 border-l-4 border-l-primary/20">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-lg">{getMoodEmoji(mood)}</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">You</span>
                  <Badge variant="outline" className={`text-xs ${getMoodColor(mood)}`}>
                    Mood {mood}/10
                  </Badge>
                </div>
                <span className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
                </span>
              </div>
            </div>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleCopy}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy text
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => setDeleteDialogOpen(true)}
                  className="text-red-600 focus:text-red-600"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-4">
            {/* Journal Content */}
            <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {displayContent}
              {shouldTruncateContent && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowFullContent(!showFullContent)}
                  className="p-0 h-auto text-primary hover:text-primary/80 ml-2"
                >
                  {showFullContent ? 'Show less' : 'Show more'}
                </Button>
              )}
            </div>

            {/* Tags */}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Interaction Buttons */}
            <div className="flex items-center gap-6 pt-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setLiked(!liked)}
                className={`gap-2 h-8 px-3 ${liked ? 'text-red-500 hover:text-red-600' : 'text-gray-500 hover:text-red-500'}`}
              >
                <Heart className={`h-4 w-4 ${liked ? 'fill-current' : ''}`} />
                <span className="text-xs">{liked ? 'Liked' : 'Like'}</span>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onPulseClick?.(id)}
                className="gap-2 h-8 px-3 text-gray-500 hover:text-primary"
              >
                <MessageCircle className="h-4 w-4" />
                <span className="text-xs">Pulse</span>
              </Button>
            </div>

            {/* AI Response - Social Media Style */}
            {aiResponse && aiResponse.comments && aiResponse.comments.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                {aiResponse.comments.map((comment, index) => {
                  // Extract persona and message from the new structure
                  const isStringComment = typeof comment === 'string';
                  const persona = isStringComment ? 'pulse' : (comment.persona || 'pulse');
                  const aiMessage = isStringComment ? comment : (comment.text || '');
                  const timestamp = isStringComment ? aiResponse.timestamp : (comment.timestamp || aiResponse.timestamp);
                  
                  // Define persona-specific styling
                  const personaStyles = {
                    pulse: { icon: 'bg-blue-100', iconColor: 'text-blue-600', nameColor: 'text-blue-600' },
                    sage: { icon: 'bg-purple-100', iconColor: 'text-purple-600', nameColor: 'text-purple-600' },
                    spark: { icon: 'bg-orange-100', iconColor: 'text-orange-600', nameColor: 'text-orange-600' },
                    anchor: { icon: 'bg-green-100', iconColor: 'text-green-600', nameColor: 'text-green-600' }
                  };
                  
                  const style = personaStyles[persona] || personaStyles.pulse;
                  const personaName = persona.charAt(0).toUpperCase() + persona.slice(1) + ' AI';
                  
                  return (
                    <div key={index} className="flex items-start gap-3">
                      {/* AI Avatar */}
                      <div className={`w-8 h-8 rounded-full ${style.icon} flex items-center justify-center flex-shrink-0`}>
                        {persona === 'pulse' && <Sparkles className={`h-4 w-4 ${style.iconColor}`} />}
                        {persona === 'sage' && <BookOpen className={`h-4 w-4 ${style.iconColor}`} />}
                        {persona === 'spark' && <Zap className={`h-4 w-4 ${style.iconColor}`} />}
                        {persona === 'anchor' && <Shield className={`h-4 w-4 ${style.iconColor}`} />}
                      </div>
                      
                      {/* AI Response Content */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`font-medium text-sm ${style.nameColor}`}>{personaName}</span>
                          <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                            AI Assistant
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
                          </span>
                        </div>
                        
                        <div className="text-sm text-gray-700 leading-relaxed mb-2">
                          {aiMessage}
                        </div>
                        
                        {/* AI Response Actions */}
                        <div className="flex items-center gap-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleHelpfulClick}
                            disabled={isSubmittingFeedback}
                            className={`gap-2 h-7 px-2 text-xs transition-colors ${
                              aiResponseHelpful 
                                ? 'text-blue-600 bg-blue-50' 
                                : 'text-gray-500 hover:text-blue-600'
                            }`}
                          >
                            <Heart className={`h-3 w-3 ${aiResponseHelpful ? 'fill-current' : ''}`} />
                            {aiResponseHelpful ? 'Helpful!' : 'Helpful'}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowReplyInput(!showReplyInput)}
                            className="gap-2 h-7 px-2 text-xs text-gray-500 hover:text-blue-600"
                          >
                            <MessageCircle className="h-3 w-3" />
                            Reply
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {/* Reply Input - Show for last AI response */}
                {showReplyInput && (
                  <div className="mt-3 space-y-2 ml-11">
                    <div className="flex gap-2">
                      <textarea
                        placeholder="Write a reply to the AI..."
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        className="flex-1 text-sm min-h-[80px] p-3 border border-gray-300 rounded-md resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleReplySubmit();
                          }
                        }}
                      />
                      <Button
                        size="sm"
                        onClick={handleReplySubmit}
                        disabled={!replyText.trim() || isSubmittingFeedback}
                        className="px-3 self-start"
                      >
                        <Send className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Press Enter to send, Shift+Enter for new line
                    </div>
                  </div>
                )}
                
                {/* User Replies Thread */}
                {userReplies.length > 0 && (
                  <div className="mt-3 space-y-2 ml-11">
                    {userReplies.map((reply) => (
                      <div key={reply.id} className="flex items-start gap-2">
                        {/* Avatar */}
                        <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                          {reply.is_ai_response ? (
                            <Sparkles className="h-3 w-3 text-blue-600" />
                          ) : (
                            <span className="text-xs font-medium text-gray-600">
                              {currentUser?.user_metadata?.full_name?.charAt(0) || 
                               currentUser?.user_metadata?.name?.charAt(0) || 'U'}
                            </span>
                          )}
                        </div>
                        
                        {/* Reply Content */}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {reply.is_ai_response ? (
                              <>
                                <span className="font-medium text-xs text-blue-600">
                                  {reply.ai_persona === 'pulse' ? 'Pulse AI' : 
                                   reply.ai_persona === 'sage' ? 'Sage AI' :
                                   reply.ai_persona === 'spark' ? 'Spark AI' :
                                   reply.ai_persona === 'anchor' ? 'Anchor AI' : 'AI'}
                                </span>
                                <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                                  {reply.ai_persona?.charAt(0).toUpperCase() + reply.ai_persona?.slice(1) || 'AI'}
                                </Badge>
                              </>
                            ) : (
                              <span className="font-medium text-xs text-gray-600">You</span>
                            )}
                            <span className="text-xs text-muted-foreground">
                              {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
                            </span>
                          </div>
                          
                          <div className={`text-sm leading-relaxed ${
                            reply.is_ai_response ? 'text-blue-700' : 'text-gray-700'
                          }`}>
                            {reply.reply_text}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Journal Entry?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this journal entry. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};
