import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Brain,
  Heart,
  RefreshCw,
  MessageCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const PulseResponse = () => {
  const navigate = useNavigate();
  const { entryId } = useParams();

  const handleBack = () => {
    navigate("/");
  };

  const handleNewReflection = () => {
    navigate("/new-entry");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pulse-50 via-background to-calm-50">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-pulse-200/30">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBack}
              className="gap-2 text-calm-600 hover:text-calm-800"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to feed
            </Button>
            <div>
              <h1 className="text-lg font-semibold text-calm-800">
                Pulse Response
              </h1>
              <p className="text-sm text-calm-600">
                AI reflection on entry #{entryId}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 py-6">
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pulse-400 to-pulse-600 flex items-center justify-center mx-auto mb-4">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-xl font-semibold text-calm-800 mb-2">
            Pulse Response Screen
          </h2>
          <p className="text-calm-600 mb-6 max-w-md mx-auto">
            This screen will show detailed AI responses to your journal entries
            with threading and interaction options.
          </p>
          <div className="space-y-3">
            <Button
              onClick={handleNewReflection}
              className="gap-2 bg-gradient-to-r from-pulse-500 to-pulse-600 hover:from-pulse-600 hover:to-pulse-700 text-white rounded-xl"
            >
              <MessageCircle className="w-4 h-4" />
              Continue reflecting
            </Button>
            <br />
            <Button
              variant="outline"
              onClick={handleBack}
              className="gap-2 border-pulse-200 text-calm-700"
            >
              <Heart className="w-4 h-4" />
              Back to journal feed
            </Button>
          </div>
        </div>

        {/* Placeholder Content */}
        <Card className="bg-pulse-50/30 border-pulse-200/50 rounded-2xl">
          <CardContent className="p-6">
            <div className="text-center space-y-4">
              <RefreshCw className="w-8 h-8 text-pulse-500 mx-auto" />
              <h3 className="text-lg font-medium text-calm-800">Coming Soon</h3>
              <p className="text-calm-600">
                The detailed Pulse response interface will include threaded
                conversations, reaction buttons, and encouragement to continue
                journaling.
              </p>
              <div className="text-sm text-calm-500 space-y-1 text-left max-w-md mx-auto">
                <p>Features to include:</p>
                <ul className="list-disc list-inside space-y-1 text-calm-600">
                  <li>Threaded AI conversation view</li>
                  <li>Reaction buttons (👍 👎 🔁 🧠)</li>
                  <li>Reply to AI responses</li>
                  <li>Timestamp showing delayed feedback feel</li>
                  <li>Gentle encouragement to continue journaling</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default PulseResponse;
