import { ArrowLeft, Shield, Database, Eye, Lock, Server, Users, Calendar, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const Privacy = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(-1)}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <div>
              <h1 className="text-lg font-semibold">Privacy & Security</h1>
              <p className="text-sm text-muted-foreground">
                Transparent about how we protect your data
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 py-6">
        <div className="space-y-8">
          {/* Introduction */}
          <Card className="border-primary/20">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Shield className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold mb-2">Our Privacy Promise</h2>
                  <p className="text-muted-foreground">
                    We believe in radical transparency about data privacy. This page explains exactly 
                    what we do with your information, what we can access, and our plans to make privacy even stronger.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* What We Collect */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                What We Collect
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4">
                <div className="p-4 rounded-lg border bg-muted/30">
                  <h4 className="font-medium mb-2">📝 Journal Entries</h4>
                  <p className="text-sm text-muted-foreground">
                    Your written reflections, mood ratings (1-10), energy levels, and stress levels.
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <h4 className="font-medium mb-2">👤 Account Information</h4>
                  <p className="text-sm text-muted-foreground">
                    Email address, encrypted password, and basic preferences (timezone, notification settings).
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <h4 className="font-medium mb-2">🤖 AI Interaction Data</h4>
                  <p className="text-sm text-muted-foreground">
                    Your conversations with Pulse, selected personas, and response ratings to improve AI quality.
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <h4 className="font-medium mb-2">📊 Usage Analytics</h4>
                  <p className="text-sm text-muted-foreground">
                    When you use the app, which features you interact with, and basic performance metrics (no personal content).
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* How It's Protected */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5" />
                How Your Data Is Protected
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">🔐 Encryption in Transit</h4>
                    <p className="text-sm text-muted-foreground">All data travels between your device and our servers using HTTPS/TLS encryption.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">🏦 Encryption at Rest</h4>
                    <p className="text-sm text-muted-foreground">Your data is encrypted in our database using industry-standard AES-256 encryption via Supabase.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">🔑 Secure Authentication</h4>
                    <p className="text-sm text-muted-foreground">Your password is hashed using bcrypt and we use JWT tokens for secure session management.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">🛡️ Access Controls</h4>
                    <p className="text-sm text-muted-foreground">Database-level security ensures you can only access your own data, with Row Level Security policies.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Who Can Access Your Data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Who Can Access Your Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg border-2 border-primary/20 bg-primary/5">
                <h4 className="font-medium text-primary mb-2">✅ What We Can Access (And Why)</h4>
                <div className="space-y-2 text-sm">
                  <p><strong>Journal Content:</strong> We can read your entries to provide AI insights and technical support when you request help.</p>
                  <p><strong>Usage Patterns:</strong> We analyze interaction patterns to improve the AI and app performance.</p>
                  <p><strong>Account Data:</strong> We can access your email and preferences for account management and notifications.</p>
                </div>
              </div>
              
              <div className="p-4 rounded-lg border-2 border-red-200 bg-red-50">
                <h4 className="font-medium text-red-800 mb-2">❌ What We Never Do</h4>
                <div className="space-y-1 text-sm text-red-700">
                  <p>• Share your personal data with third parties for marketing</p>
                  <p>• Sell your information to advertisers or data brokers</p>
                  <p>• Access your data for purposes other than providing the service</p>
                  <p>• Store your data outside of secure, encrypted databases</p>
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-muted/30">
                <h4 className="font-medium mb-2">🤖 AI Processing</h4>
                <p className="text-sm text-muted-foreground">
                  Your journal entries are sent to OpenAI's API to generate personalized insights. OpenAI processes this data according to their privacy policy and doesn't train models on your data.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Data Infrastructure */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="w-5 h-5" />
                Where Your Data Lives
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4">
                <div className="p-4 rounded-lg border bg-muted/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="secondary">Supabase</Badge>
                    <span className="text-sm font-medium">Database & Authentication</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    SOC 2 Type II certified, GDPR compliant, US-based servers with encryption at rest.
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="secondary">Railway</Badge>
                    <span className="text-sm font-medium">Backend API</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Secure cloud infrastructure with automatic security updates and monitoring.
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-muted/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="secondary">Vercel</Badge>
                    <span className="text-sm font-medium">Web Application</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Global CDN with HTTPS by default and enterprise-grade security.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Your Rights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Your Data Rights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3">
                <div className="p-3 rounded border bg-muted/20">
                  <h4 className="font-medium text-sm">📥 Export Your Data</h4>
                  <p className="text-xs text-muted-foreground">Download all your journal entries and data in a portable format.</p>
                </div>
                <div className="p-3 rounded border bg-muted/20">
                  <h4 className="font-medium text-sm">🗑️ Delete Your Data</h4>
                  <p className="text-xs text-muted-foreground">Permanently remove all your information from our systems at any time.</p>
                </div>
                <div className="p-3 rounded border bg-muted/20">
                  <h4 className="font-medium text-sm">✏️ Correct Your Data</h4>
                  <p className="text-xs text-muted-foreground">Update or correct any personal information we have about you.</p>
                </div>
                <div className="p-3 rounded border bg-muted/20">
                  <h4 className="font-medium text-sm">🔍 Access Your Data</h4>
                  <p className="text-xs text-muted-foreground">See exactly what personal data we have stored about you.</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Future Privacy Enhancements */}
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-800">
                <Calendar className="w-5 h-5" />
                Privacy Roadmap
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-blue-700 mb-4">
                We're committed to continuously improving your privacy. Here's what's planned:
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 rounded bg-white/50 border border-blue-200">
                  <Badge variant="secondary" className="bg-green-100 text-green-700">Q2 2025</Badge>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm text-blue-800">Client-Side Encryption</h4>
                    <p className="text-xs text-blue-600">Encrypt journal entries on your device before sending to our servers.</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 rounded bg-white/50 border border-blue-200">
                  <Badge variant="secondary" className="bg-blue-100 text-blue-700">Q3 2025</Badge>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm text-blue-800">End-to-End Encryption</h4>
                    <p className="text-xs text-blue-600">Full E2E encryption where only you hold the decryption keys.</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 rounded bg-white/50 border border-blue-200">
                  <Badge variant="secondary" className="bg-purple-100 text-purple-700">Q4 2025</Badge>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm text-blue-800">Local-First Storage</h4>
                    <p className="text-xs text-blue-600">Keep your data primarily on your device with encrypted cloud sync.</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 p-3 rounded bg-white/50 border border-blue-200">
                <p className="text-xs text-blue-600">
                  <strong>Note:</strong> These enhancements will be optional features that you can enable while maintaining full AI functionality. We'll never compromise the quality of your wellness insights for privacy.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Contact */}
          <Card>
            <CardContent className="p-6 text-center">
              <h3 className="font-semibold mb-2">Questions About Privacy?</h3>
              <p className="text-sm text-muted-foreground mb-4">
                We're happy to discuss our privacy practices or help with any data requests.
              </p>
              <Button variant="outline" className="gap-2">
                Contact Us About Privacy
                <ArrowRight className="w-4 h-4" />
              </Button>
            </CardContent>
          </Card>

          {/* Last Updated */}
          <div className="text-center text-xs text-muted-foreground">
            Last updated: January 2025 • PulseCheck Privacy Policy v1.0
          </div>
        </div>
      </main>
    </div>
  );
};

export default Privacy; 