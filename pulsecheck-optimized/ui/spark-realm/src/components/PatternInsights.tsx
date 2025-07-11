import React from 'react';
import { UserPatternSummary } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { TrendingUp, TrendingDown, Minus, Brain, MessageCircle, Heart, Zap } from 'lucide-react';

interface PatternInsightsProps {
  patterns: UserPatternSummary;
  isLoading?: boolean;
}

const PatternInsights: React.FC<PatternInsightsProps> = ({
  patterns,
  isLoading = false
}) => {
  const getTrendIcon = (value: number, baseline: number = 5) => {
    if (value > baseline + 1) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (value < baseline - 1) return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  const getWritingStyleColor = (style: string) => {
    switch (style) {
      case 'analytical':
        return 'bg-blue-100 text-blue-800';
      case 'emotional':
        return 'bg-pink-100 text-pink-800';
      case 'concise':
        return 'bg-green-100 text-green-800';
      case 'detailed':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatMoodValue = (value: number) => {
    return Math.round(value * 10) / 10;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Your Patterns</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>Your Patterns</span>
            </div>
            <Badge variant="outline" className={getConfidenceColor(patterns.pattern_confidence)}>
              {Math.round(patterns.pattern_confidence * 100)}% confidence
            </Badge>
          </CardTitle>
          <CardDescription>
            Based on {patterns.entries_analyzed} journal entries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Writing Style */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Writing Style</h4>
              <Badge className={getWritingStyleColor(patterns.writing_style)}>
                {patterns.writing_style}
              </Badge>
            </div>

            {/* Common Topics */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Common Topics</h4>
              <div className="flex flex-wrap gap-1">
                {patterns.common_topics.slice(0, 3).map((topic, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {topic}
                  </Badge>
                ))}
                {patterns.common_topics.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{patterns.common_topics.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mood Trends */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Heart className="h-5 w-5" />
            <span>Mood Trends</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Mood */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Overall Mood</span>
                <div className="flex items-center space-x-2">
                  {getTrendIcon(patterns.mood_trends.mood)}
                  <span className="text-sm text-gray-600">
                    {formatMoodValue(patterns.mood_trends.mood)}/10
                  </span>
                </div>
              </div>
              <Progress value={patterns.mood_trends.mood * 10} className="h-2" />
            </div>

            {/* Energy */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Energy Level</span>
                <div className="flex items-center space-x-2">
                  {getTrendIcon(patterns.mood_trends.energy)}
                  <span className="text-sm text-gray-600">
                    {formatMoodValue(patterns.mood_trends.energy)}/10
                  </span>
                </div>
              </div>
              <Progress value={patterns.mood_trends.energy * 10} className="h-2" />
            </div>

            {/* Stress */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Stress Level</span>
                <div className="flex items-center space-x-2">
                  {getTrendIcon(patterns.mood_trends.stress, 5)}
                  <span className="text-sm text-gray-600">
                    {formatMoodValue(patterns.mood_trends.stress)}/10
                  </span>
                </div>
              </div>
              <Progress 
                value={patterns.mood_trends.stress * 10} 
                className="h-2"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Interaction Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageCircle className="h-5 w-5" />
            <span>How You Like to Interact</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <span className="text-sm">Questions</span>
              <div className={`h-2 w-2 rounded-full ${
                patterns.interaction_preferences.prefers_questions 
                  ? 'bg-green-500' 
                  : 'bg-gray-300'
              }`} />
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <span className="text-sm">Validation</span>
              <div className={`h-2 w-2 rounded-full ${
                patterns.interaction_preferences.prefers_validation 
                  ? 'bg-green-500' 
                  : 'bg-gray-300'
              }`} />
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <span className="text-sm">Advice</span>
              <div className={`h-2 w-2 rounded-full ${
                patterns.interaction_preferences.prefers_advice 
                  ? 'bg-green-500' 
                  : 'bg-gray-300'
              }`} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Response Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Response Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <span className="text-sm font-medium text-gray-700">Length</span>
              <Badge variant="outline">
                {patterns.response_preferences.length}
              </Badge>
            </div>
            <div className="space-y-1">
              <span className="text-sm font-medium text-gray-700">Style</span>
              <Badge variant="outline">
                {patterns.response_preferences.style}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Last Updated */}
      <div className="text-xs text-gray-500 text-center">
        Last updated: {new Date(patterns.last_updated).toLocaleString()}
      </div>
    </div>
  );
};

export default PatternInsights; 