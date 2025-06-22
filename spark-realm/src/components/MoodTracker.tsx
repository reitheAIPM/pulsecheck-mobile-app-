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
    if (mood <= 2)
      return { emoji: "😔", label: "Struggling", color: "text-red-500" };
    if (mood <= 4)
      return { emoji: "😐", label: "Tough day", color: "text-orange-500" };
    if (mood <= 6)
      return { emoji: "🙂", label: "Okay", color: "text-yellow-500" };
    if (mood <= 8)
      return { emoji: "😊", label: "Good", color: "text-green-500" };
    return { emoji: "😄", label: "Amazing", color: "text-emerald-500" };
  };

  const moodData = getMoodData(localValue[0]);

  return (
    <div className={cn("space-y-4", className)}>
      <div className="text-center">
        <div className="text-4xl mb-2">{moodData.emoji}</div>
        <div className={cn("text-lg font-medium", moodData.color)}>
          {moodData.label}
        </div>
        <div className="text-sm text-calm-600 mt-1">{localValue[0]}/10</div>
      </div>

      <div className="px-4">
        <Slider
          value={localValue}
          onValueChange={handleValueChange}
          max={10}
          min={1}
          step={1}
          className="w-full"
        />
      </div>

      <div className="flex justify-between text-xs text-calm-500 px-4">
        <span>1</span>
        <span className="text-calm-600 font-medium">How are you feeling?</span>
        <span>10</span>
      </div>
    </div>
  );
}
