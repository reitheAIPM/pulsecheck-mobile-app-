import React, { useState, useEffect } from 'react';
import { PersonaInfo, apiService } from '../services/api';
import { authService } from '../services/authService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Sparkles, BookOpen, Zap, Anchor, Crown, Users, Settings } from 'lucide-react';

// Local persona type for component
type PersonaRecommendation = PersonaInfo & {
  recommended: boolean;
  available: boolean;
  requires_premium: boolean;
  times_used: number;
  recommendation_reason: string;
  persona_id?: string; // For backward compatibility
  persona_name?: string; // For backward compatibility
};

interface AITeamManagerProps {
  userId: string;
  premiumEnabled: boolean;
  onPremiumToggle: (enabled: boolean) => void;
  personas: PersonaRecommendation[];
  isLoading?: boolean;
  onSettingsChange?: (settings: any) => void;
}

const AITeamManager: React.FC<AITeamManagerProps> = ({
  userId,
  premiumEnabled,
  onPremiumToggle,
  personas,
  isLoading = false,
  onSettingsChange
}) => {
  const [aiInteractionLevel, setAiInteractionLevel] = useState('balanced'); // quiet, balanced, active
  const [showSettings, setShowSettings] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [loadingPreferences, setLoadingPreferences] = useState(true);

  // Load saved AI interaction preferences on component mount
  useEffect(() => {
    const loadSavedPreferences = async () => {
      try {
        setLoadingPreferences(true);
        // Don't pass userId - let API service resolve it internally to match saving logic
        const preferences = await apiService.getUserAIPreferences();
        if (preferences && preferences.response_frequency) {
          setAiInteractionLevel(preferences.response_frequency);
        }
      } catch (error) {
        console.log('No saved AI preferences found, using default:', error);
        // Keep default 'balanced' value
      } finally {
        setLoadingPreferences(false);
      }
    };

    loadSavedPreferences();
  }, []);

  const handleInteractionLevelChange = async (level: string) => {
    try {
      setSavingSettings(true);
      setAiInteractionLevel(level);
      
      // Save to backend via API call
      if (onSettingsChange) {
        await onSettingsChange({ response_frequency: level });
      }
      
      // Save to backend - require proper authentication without development fallback
      const result = await apiService.getCurrentUser();
      if (!result?.id) {
        throw new Error('Authentication required to save AI interaction level. Please sign in.');
      }
      
      const resolvedUserId = result.id;
      await apiService.updateUserPreference(resolvedUserId, 'response_frequency', level);
      
      console.log(`AI interaction level saved successfully: ${level}`);
      
    } catch (error) {
      console.error('Failed to save AI interaction level:', error);
      // Revert on error
      setAiInteractionLevel(aiInteractionLevel);
      
      // Show user-friendly error message
      if (error instanceof Error && error.message.includes('Authentication required')) {
        // Optionally show a toast or alert to the user
        alert('Please sign in to save your AI interaction preferences.');
      }
    } finally {
      setSavingSettings(false);
    }
  };

  const getPersonaIcon = (personaId: string) => {
    switch (personaId) {
      case 'pulse':
        return <Sparkles className="h-5 w-5" />;
      case 'sage':
        return <BookOpen className="h-5 w-5" />;
      case 'spark':
        return <Zap className="h-5 w-5" />;
      case 'anchor':
        return <Anchor className="h-5 w-5" />;
      default:
        return <Sparkles className="h-5 w-5" />;
    }
  };

  const getPersonaColor = (personaId: string) => {
    switch (personaId) {
      case 'pulse':
        return 'bg-blue-500/10 border-blue-500/20 text-blue-700';
      case 'sage':
        return 'bg-purple-500/10 border-purple-500/20 text-purple-700';
      case 'spark':
        return 'bg-orange-500/10 border-orange-500/20 text-orange-700';
      case 'anchor':
        return 'bg-green-500/10 border-green-500/20 text-green-700';
      default:
        return 'bg-gray-500/10 border-gray-500/20 text-gray-700';
    }
  };

  const activePersonas = personas.filter(p => 
    !p.requires_premium || premiumEnabled
  );

  const premiumPersonas = personas.filter(p => p.requires_premium);

  if (isLoading || loadingPreferences) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <Card className="h-24">
            <CardContent className="p-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Premium Toggle - Prominent */}
      <Card className={`border-2 transition-all ${premiumEnabled ? 'border-yellow-300 bg-yellow-50/50' : 'border-dashed border-yellow-200 bg-yellow-50/20'}`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${premiumEnabled ? 'bg-yellow-200' : 'bg-yellow-100'}`}>
                <Crown className={`h-5 w-5 ${premiumEnabled ? 'text-yellow-700' : 'text-yellow-600'}`} />
              </div>
              <div>
                <h3 className="font-semibold text-sm">Premium AI Team</h3>
                <p className="text-xs text-gray-600">
                  {premiumEnabled ? 'All 4 AI companions active' : 'Enable Sage, Spark & Anchor (Free during beta)'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={premiumEnabled}
                onCheckedChange={onPremiumToggle}
                disabled={isLoading}
                className="data-[state=checked]:bg-yellow-500"
              />
            </div>
          </div>
          {premiumEnabled && (
            <div className="mt-3 pt-3 border-t border-yellow-200">
              <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-700">
                ✨ Premium Team Active - Free during beta testing
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Team Status */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-500" />
              <CardTitle className="text-base">Your AI Wellness Team</CardTitle>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              className="h-8 w-8 p-0"
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription className="text-sm">
            Your AI companions work together, responding naturally to your journal entries like friends on social media
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-3">
          {/* Active AI Team */}
          <div className="space-y-2">
            {activePersonas.map(persona => {
              const isActive = !persona.requires_premium || premiumEnabled;
              
              return (
                <div
                  key={persona.id || persona.persona_id}
                  className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isActive 
                      ? `${getPersonaColor(persona.id || persona.persona_id)} border-current` 
                      : 'bg-gray-50 border-gray-200 opacity-60'
                  }`}
                >
                  <div className={`p-2 rounded-lg ${isActive ? 'bg-white/50' : 'bg-gray-100'}`}>
                    {getPersonaIcon(persona.id || persona.persona_id)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-sm">{persona.name || persona.persona_name}</h4>
                      {isActive && (
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                          Active
                        </Badge>
                      )}
                      {persona.recommended && (
                        <Badge variant="default" className="text-xs bg-blue-500">
                          Recommended
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-600">{persona.description}</p>
                    {persona.times_used > 0 && (
                      <p className="text-xs text-gray-500 mt-1">
                        Interacted {persona.times_used} times
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Inactive Premium AIs */}
          {!premiumEnabled && premiumPersonas.length > 0 && (
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2">Unlock with Premium:</p>
              <div className="grid grid-cols-3 gap-2">
                {premiumPersonas.map(persona => (
                  <div key={persona.id || persona.persona_id} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                    <div className="p-1 bg-gray-100 rounded">
                      {getPersonaIcon(persona.id || persona.persona_id)}
                    </div>
                    <span className="text-xs text-gray-600">{persona.name || persona.persona_name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Interaction Settings */}
      {showSettings && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">AI Interaction Settings</CardTitle>
            <CardDescription className="text-sm">
              Control how often your AI team responds to your entries
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <label className="text-sm font-medium">Response Frequency</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: 'quiet', label: 'Quiet', desc: 'Occasional responses' },
                  { id: 'balanced', label: 'Balanced', desc: 'Natural interaction' },
                  { id: 'active', label: 'Active', desc: 'Frequent engagement' }
                ].map(level => (
                  <Button
                    key={level.id}
                    variant={aiInteractionLevel === level.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleInteractionLevelChange(level.id)}
                    className="flex flex-col h-auto min-h-[60px] p-3 text-center justify-center"
                  >
                    <span className="text-sm font-medium leading-tight">{level.label}</span>
                    <span className="text-xs opacity-70 leading-tight mt-1 whitespace-normal">{level.desc}</span>
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Status Summary */}
      <div className="text-center">
        <p className="text-xs text-gray-500">
          {activePersonas.length} AI companion{activePersonas.length !== 1 ? 's' : ''} ready to support you naturally
        </p>
        <p className="text-xs text-gray-400 mt-1">
          They'll respond to your entries like friends, not every time but when it feels right
        </p>
      </div>
    </div>
  );
};

export default AITeamManager; 