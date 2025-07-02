import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Slider } from "@/components/ui/slider";

interface MoodTrackerProps {
  value: number;
  onChange: (value: number) => void;
  className?: string;
}

export function MoodTracker({ value, onChange, className }: MoodTrackerProps) {
  const [localValue, setLocalValue] = useState([value]);

  useEffect(() => {
    setLocalValue([value]);
  }, [value]);

  const handleValueChange = (newValue: number[]) => {
    setLocalValue(newValue);
    onChange(newValue[0]);
  };

  const getMoodData = (mood: number) => {
    if (mood <= 1)
      return { 
        emoji: "😔", 
        label: "Really struggling", 
        description: "Having a very difficult time",
        color: "text-red-600" 
      };
    if (mood <= 2)
      return { 
        emoji: "😞", 
        label: "Struggling", 
        description: "Feeling down and having a hard time",
        color: "text-red-500" 
      };
    if (mood <= 3)
      return { 
        emoji: "😐", 
        label: "Tough day", 
        description: "Not feeling great, facing challenges",
        color: "text-orange-600" 
      };
    if (mood <= 4)
      return { 
        emoji: "😕", 
        label: "Below average", 
        description: "Feeling a bit off or unmotivated",
        color: "text-orange-500" 
      };
    if (mood <= 5)
      return { 
        emoji: "😐", 
        label: "Neutral", 
        description: "Feeling okay, neither good nor bad",
        color: "text-yellow-600" 
      };
    if (mood <= 6)
      return { 
        emoji: "🙂", 
        label: "Okay", 
        description: "Feeling decent, getting by well",
        color: "text-yellow-500" 
      };
    if (mood <= 7)
      return { 
        emoji: "😊", 
        label: "Good", 
        description: "Feeling positive and content",
        color: "text-green-500" 
      };
    if (mood <= 8)
      return { 
        emoji: "😄", 
        label: "Really good", 
        description: "Feeling happy and energized",
        color: "text-green-600" 
      };
    if (mood <= 9)
      return { 
        emoji: "😁", 
        label: "Excellent", 
        description: "Feeling fantastic and joyful",
        color: "text-emerald-500" 
      };
    return { 
      emoji: "🤩", 
      label: "Amazing", 
      description: "Feeling absolutely incredible!",
      color: "text-emerald-600" 
    };
  };

  const moodData = getMoodData(localValue[0]);

  return (
    <div className={cn("space-y-6", className)}>
      <div className="text-center">
        <div className="text-6xl md:text-7xl lg:text-8xl mb-4">{moodData.emoji}</div>
        <div className={cn("text-xl md:text-2xl font-semibold mb-2", moodData.color)}>
          {moodData.label}
        </div>
        <div className="text-sm md:text-base text-muted-foreground mb-1">
          {moodData.description}
        </div>
        <div className="text-lg md:text-xl font-medium text-primary mt-2">
          {localValue[0]}/10
        </div>
      </div>

      <div className="px-4 md:px-8">
        <Slider
          value={localValue}
          onValueChange={handleValueChange}
          max={10}
          min={1}
          step={1}
          className="w-full h-3 md:h-4"
        />
      </div>

      <div className="flex justify-between items-center text-sm md:text-base text-muted-foreground px-4 md:px-8">
        <div className="text-center">
          <div className="font-medium">1</div>
          <div className="text-xs text-red-500">Worst</div>
        </div>
        <div className="text-center font-medium text-primary">
          How are you feeling today?
        </div>
        <div className="text-center">
          <div className="font-medium">10</div>
          <div className="text-xs text-emerald-500">Best</div>
        </div>
      </div>
    </div>
  );
}
