import { useState } from "react";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ZordMCQ } from "../index";

interface ZordMCQSectionProps {
  mcqs: ZordMCQ[];
  onComplete: (answers: Record<string, string>) => void;
}

export default function ZordMCQSection({ mcqs, onComplete }: ZordMCQSectionProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const handleAnswerChange = (mcqId: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [mcqId]: value }));
  };

  const isComplete = Object.keys(answers).length === mcqs.length;

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <CardTitle className="text-lg">Technical Clarifications</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {mcqs.map((mcq, index) => (
          <div key={mcq.id} className="space-y-3">
            <div className="font-medium">
              {index + 1}. {mcq.question}
            </div>
            <RadioGroup
              value={answers[mcq.id] || ""}
              onValueChange={(value) => handleAnswerChange(mcq.id, value)}
            >
              {mcq.options.map((option) => (
                <div key={option.id} className="flex items-center space-x-2">
                  <RadioGroupItem value={option.value} id={`${mcq.id}-${option.id}`} />
                  <Label
                    htmlFor={`${mcq.id}-${option.id}`}
                    className="cursor-pointer"
                  >
                    [{option.label}] {option.value}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        ))}

        <Button
          onClick={() => onComplete(answers)}
          disabled={!isComplete}
          className="w-full"
        >
          Generate Plan →
        </Button>
      </CardContent>
    </Card>
  );
}
