import {
  TrendingUp,
  Calendar,
  Brain,
  Heart,
  Target,
  Award,
  BarChart3,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const Insights = () => {
  // Mock data - in real app this would come from API
  const stats = {
    totalEntries: 24,
    currentStreak: 7,
    avgMood: 6.2,
    aiResponseRate: 85,
    weeklyGoal: 5,
    weeklyProgress: 4,
  };

  const moodTrend = [
    { day: "Mon", mood: 7 },
    { day: "Tue", mood: 5 },
    { day: "Wed", mood: 6 },
    { day: "Thu", mood: 8 },
    { day: "Fri", mood: 4 },
    { day: "Sat", mood: 7 },
    { day: "Sun", mood: 6 },
  ];

  const insights = [
    {
      title: "Mood Pattern",
      description: "Your mood tends to be higher on weekends",
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      title: "Best Reflection Time",
      description: "You write most thoughtfully in the evenings",
      icon: Calendar,
      color: "text-blue-600",
    },
    {
      title: "AI Engagement",
      description: "Pulse responses help improve your mood by 15%",
      icon: Brain,
      color: "text-purple-600",
    },
  ];

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Insights</h1>
              <p className="text-sm text-muted-foreground">
                Your reflection journey
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="border-0 bg-gradient-to-br from-primary/5 to-primary/10">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-primary">
                {stats.totalEntries}
              </div>
              <div className="text-sm text-muted-foreground">
                Total reflections
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 bg-gradient-to-br from-orange-500/5 to-orange-500/10">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">
                {stats.currentStreak}
              </div>
              <div className="text-sm text-muted-foreground">Day streak</div>
            </CardContent>
          </Card>
        </div>

        {/* Weekly Goal Progress */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Target className="w-4 h-4" />
              Weekly Goal
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Progress this week</span>
              <span className="font-medium">
                {stats.weeklyProgress}/{stats.weeklyGoal} entries
              </span>
            </div>
            <Progress
              value={(stats.weeklyProgress / stats.weeklyGoal) * 100}
              className="h-2"
            />
            <p className="text-xs text-muted-foreground">
              {stats.weeklyGoal - stats.weeklyProgress > 0
                ? `${stats.weeklyGoal - stats.weeklyProgress} more to reach your goal`
                : "Goal achieved! 🎉"}
            </p>
          </CardContent>
        </Card>

        {/* Mood Trend */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Heart className="w-4 h-4" />
              Mood This Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between h-20 mb-2">
              {moodTrend.map((day, index) => (
                <div key={day.day} className="flex flex-col items-center gap-2">
                  <div
                    className="w-6 bg-primary/20 rounded-sm"
                    style={{ height: `${(day.mood / 10) * 60}px` }}
                  />
                  <span className="text-xs text-muted-foreground">
                    {day.day}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Average: {stats.avgMood}/10</span>
              <span>This week</span>
            </div>
          </CardContent>
        </Card>

        {/* AI Insights */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI Insights
          </h2>

          {insights.map((insight, index) => (
            <Card key={index} className="border-l-4 border-l-primary/30">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <insight.icon className={`w-5 h-5 mt-0.5 ${insight.color}`} />
                  <div>
                    <h3 className="font-medium text-sm">{insight.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {insight.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Achievements */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Award className="w-4 h-4" />
              Recent Achievements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-primary/5 rounded-lg">
              <div className="text-2xl">🔥</div>
              <div>
                <div className="font-medium text-sm">Week Warrior</div>
                <div className="text-xs text-muted-foreground">
                  7 days in a row
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg opacity-60">
              <div className="text-2xl">📚</div>
              <div>
                <div className="font-medium text-sm">Deep Thinker</div>
                <div className="text-xs text-muted-foreground">
                  Write 500+ words (2 more needed)
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Insights;
