import { useState } from "react";
import {
  User,
  Brain,
  Settings,
  Bell,
  Shield,
  HelpCircle,
  ChevronRight,
  Edit3,
  Save,
  X,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    name: "Alex Chen",
    role: "Senior Software Engineer",
    company: "TechCorp",
    workStyle:
      "I work best in focused blocks and tend to overthink problems. I value work-life balance but sometimes struggle with setting boundaries.",
    triggers: "Heavy meeting days, unclear requirements, tight deadlines",
    goals:
      "Better stress management, improved work-life balance, more confident decision making",
  });

  const [aiSettings, setAiSettings] = useState({
    responseDelay: true,
    personalizedResponses: true,
    moodTracking: true,
    weeklyInsights: true,
    encouragingTone: true,
  });

  const handleSave = () => {
    // In real app, save to backend
    setIsEditing(false);
  };

  const handleCancel = () => {
    // Reset changes
    setIsEditing(false);
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <User className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">Profile</h1>
                <p className="text-sm text-muted-foreground">
                  Personalize your experience
                </p>
              </div>
            </div>
            {!isEditing ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="gap-2"
              >
                <Edit3 className="w-4 h-4" />
                Edit
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  <X className="w-4 h-4" />
                </Button>
                <Button size="sm" onClick={handleSave} className="gap-2">
                  <Save className="w-4 h-4" />
                  Save
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Profile Info */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <User className="w-4 h-4" />
              About You
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={profile.name}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, name: e.target.value }))
                }
                disabled={!isEditing}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Input
                  id="role"
                  value={profile.role}
                  onChange={(e) =>
                    setProfile((prev) => ({ ...prev, role: e.target.value }))
                  }
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  value={profile.company}
                  onChange={(e) =>
                    setProfile((prev) => ({ ...prev, company: e.target.value }))
                  }
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="workStyle">Work Style & Preferences</Label>
              <Textarea
                id="workStyle"
                value={profile.workStyle}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, workStyle: e.target.value }))
                }
                disabled={!isEditing}
                placeholder="Tell Pulse about how you work best, your preferences, and what helps you be productive..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="triggers">Stress Triggers</Label>
              <Textarea
                id="triggers"
                value={profile.triggers}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, triggers: e.target.value }))
                }
                disabled={!isEditing}
                placeholder="What situations or work conditions tend to stress you out?"
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="goals">Goals & Aspirations</Label>
              <Textarea
                id="goals"
                value={profile.goals}
                onChange={(e) =>
                  setProfile((prev) => ({ ...prev, goals: e.target.value }))
                }
                disabled={!isEditing}
                placeholder="What do you hope to achieve through reflection and journaling?"
                rows={2}
              />
            </div>
          </CardContent>
        </Card>

        {/* AI Settings */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Brain className="w-4 h-4" />
              Pulse AI Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Delayed Responses</div>
                <div className="text-xs text-muted-foreground">
                  Pulse waits 3-6 hours before responding for reflection
                </div>
              </div>
              <Switch
                checked={aiSettings.responseDelay}
                onCheckedChange={(checked) =>
                  setAiSettings((prev) => ({ ...prev, responseDelay: checked }))
                }
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">
                  Personalized Responses
                </div>
                <div className="text-xs text-muted-foreground">
                  Use your profile info for more relevant insights
                </div>
              </div>
              <Switch
                checked={aiSettings.personalizedResponses}
                onCheckedChange={(checked) =>
                  setAiSettings((prev) => ({
                    ...prev,
                    personalizedResponses: checked,
                  }))
                }
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Mood Pattern Analysis</div>
                <div className="text-xs text-muted-foreground">
                  Track mood trends and provide insights
                </div>
              </div>
              <Switch
                checked={aiSettings.moodTracking}
                onCheckedChange={(checked) =>
                  setAiSettings((prev) => ({ ...prev, moodTracking: checked }))
                }
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Weekly Insights</div>
                <div className="text-xs text-muted-foreground">
                  Receive weekly reflection summaries
                </div>
              </div>
              <Switch
                checked={aiSettings.weeklyInsights}
                onCheckedChange={(checked) =>
                  setAiSettings((prev) => ({
                    ...prev,
                    weeklyInsights: checked,
                  }))
                }
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Encouraging Tone</div>
                <div className="text-xs text-muted-foreground">
                  Emphasize support and growth mindset
                </div>
              </div>
              <Switch
                checked={aiSettings.encouragingTone}
                onCheckedChange={(checked) =>
                  setAiSettings((prev) => ({
                    ...prev,
                    encouragingTone: checked,
                  }))
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Settings Menu */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Settings
          </h2>

          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                <button className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <Bell className="w-4 h-4" />
                    <span className="text-sm font-medium">Notifications</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>

                <button className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <Shield className="w-4 h-4" />
                    <span className="text-sm font-medium">
                      Privacy & Security
                    </span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>

                <button className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <HelpCircle className="w-4 h-4" />
                    <span className="text-sm font-medium">Help & Support</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Note */}
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-4 text-center">
            <div className="text-sm text-primary/80">
              🔒 Your personal information is encrypted and never shared. Pulse
              uses this data only to provide better, more personalized support.
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Profile;
