import { useLocation, useNavigate } from "react-router-dom";
import { Home, BarChart3, User, Plus, History } from "lucide-react";
import { cn } from "@/lib/utils";

export function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { id: "home", label: "Home", icon: Home, path: "/" },
    { id: "history", label: "History", icon: History, path: "/history" },
    { id: "new", label: "New", icon: Plus, path: "/journal", isAction: true },
    { id: "insights", label: "Insights", icon: BarChart3, path: "/insights" },
    { id: "profile", label: "Me", icon: User, path: "/profile" },
  ];

  const handleTabClick = (tab: (typeof tabs)[0]) => {
    // For home navigation, preserve scroll position if user was already on home
    if (tab.path === "/" && location.pathname === "/") {
      // User is already on home, scroll to top instead of reloading
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      navigate(tab.path);
    }
  };

  // Don't show on journal entry screen to avoid distraction
  if (location.pathname === "/journal" || location.pathname.startsWith("/journal/")) {
    return null;
  }

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-md border-t border-border z-50">
      <div className="max-w-lg mx-auto px-4">
        <div className="flex items-center justify-around py-2">
          {tabs.map((tab) => {
            const isActive = location.pathname === tab.path;
            const Icon = tab.icon;

            return (
              <button
                key={tab.id}
                onClick={() => handleTabClick(tab)}
                className={cn(
                  "flex flex-col items-center gap-1 py-2 px-3 min-w-[60px] transition-colors duration-200",
                  tab.isAction
                    ? "bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
                    : isActive
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon className={cn("w-5 h-5", tab.isAction && "w-4 h-4")} />
                <span className="text-xs font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
