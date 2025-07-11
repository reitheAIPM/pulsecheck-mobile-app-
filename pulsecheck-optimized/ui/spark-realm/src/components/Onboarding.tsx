import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Sparkles, Heart, Brain, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface OnboardingProps {
  user: {
    id: string;
    email: string;
    name: string;
  };
  onComplete: () => void;
}

interface OnboardingData {
  techRole: string;
  company: string;
  interests: string[];
  goals: string[];
}

const techRoles = [
  'Software Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'DevOps Engineer',
  'Data Scientist',
  'Product Manager',
  'Designer',
  'Engineering Manager',
  'CTO/Tech Lead',
  'Student',
  'Other'
];

const wellnessGoals = [
  { id: 'stress', label: 'Manage Stress', icon: '🧘' },
  { id: 'reflection', label: 'Daily Reflection', icon: '💭' },
  { id: 'mood', label: 'Track Mood', icon: '😊' },
  { id: 'productivity', label: 'Boost Productivity', icon: '🚀' },
  { id: 'balance', label: 'Work-Life Balance', icon: '⚖️' },
  { id: 'mindfulness', label: 'Mindfulness', icon: '🌸' },
  { id: 'sleep', label: 'Better Sleep', icon: '😴' },
  { id: 'energy', label: 'More Energy', icon: '⚡' }
];

export default function Onboarding({ user, onComplete }: OnboardingProps) {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingData>({
    techRole: '',
    company: '',
    interests: [],
    goals: []
  });

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Complete onboarding
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    // Save onboarding data (could call API here)
    console.log('Onboarding completed:', data);
    onComplete();
  };

  const toggleGoal = (goalId: string) => {
    setData(prev => ({
      ...prev,
      goals: prev.goals.includes(goalId)
        ? prev.goals.filter(g => g !== goalId)
        : [...prev.goals, goalId]
    }));
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-400 to-blue-500 rounded-full flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Welcome to PulseCheck!</h2>
              <p className="text-gray-600 mt-2">
                Let's personalize your wellness journey in just a few steps.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What's your role in tech?
                </label>
                <select
                  value={data.techRole}
                  onChange={(e) => setData(prev => ({ ...prev, techRole: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select your role</option>
                  {techRoles.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company (optional)
                </label>
                <Input
                  placeholder="Where do you work?"
                  value={data.company}
                  onChange={(e) => setData(prev => ({ ...prev, company: e.target.value }))}
                />
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                <Target className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">What are your goals?</h2>
              <p className="text-gray-600 mt-2">
                Select what you'd like to focus on with PulseCheck.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {wellnessGoals.map(goal => (
                <div
                  key={goal.id}
                  onClick={() => toggleGoal(goal.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    data.goals.includes(goal.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-2xl mb-2">{goal.icon}</div>
                    <div className="text-sm font-medium">{goal.label}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center">
                <Heart className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">You're all set!</h2>
              <p className="text-gray-600 mt-2">
                Ready to start your wellness journey with AI-powered insights.
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Your PulseCheck Profile:</h3>
              <div className="space-y-2 text-sm">
                <div><strong>Name:</strong> {user.name}</div>
                <div><strong>Email:</strong> {user.email}</div>
                {data.techRole && <div><strong>Role:</strong> {data.techRole}</div>}
                {data.company && <div><strong>Company:</strong> {data.company}</div>}
                {data.goals.length > 0 && (
                  <div>
                    <strong>Goals:</strong>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {data.goals.map(goalId => {
                        const goal = wellnessGoals.find(g => g.id === goalId);
                        return (
                          <Badge key={goalId} variant="secondary" className="text-xs">
                            {goal?.icon} {goal?.label}
                          </Badge>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
              <div className="flex items-start gap-3">
                <Brain className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-900">AI-Powered Insights</h4>
                  <p className="text-sm text-yellow-800 mt-1">
                    Your AI companion will provide personalized insights based on your entries, helping you identify patterns and improve your wellbeing.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              {[1, 2, 3].map(i => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i <= step ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-500">Step {step} of 3</span>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {renderStep()}

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleSkip}
              className="flex-1"
            >
              Skip for now
            </Button>
            <Button
              onClick={handleNext}
              className="flex-1 gap-2"
            >
              {step === 3 ? 'Get Started' : 'Next'}
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 