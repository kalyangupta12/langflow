import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, CheckCircle2, Edit } from "lucide-react";
import type { ZordPlan, ZordStage } from "../index";

interface ZordPlanSectionProps {
  plan: ZordPlan;
  onImplement: () => void;
  onModify: () => void;
  stage: ZordStage;
}

export default function ZordPlanSection({
  plan,
  onImplement,
  onModify,
  stage,
}: ZordPlanSectionProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-primary" />
            {plan.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Steps */}
          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-muted-foreground">
              Workflow Steps:
            </h3>
            {plan.steps.map((step, index) => (
              <div key={step.id} className="flex items-start gap-3">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">
                  {index + 1}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="text-sm">{step.description}</div>
                  {step.component && (
                    <Badge variant="secondary" className="text-xs">
                      {step.component}
                    </Badge>
                  )}
                </div>
                {index < plan.steps.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                )}
              </div>
            ))}
          </div>

          {/* Data Flow */}
          <div className="space-y-2">
            <h3 className="font-semibold text-sm text-muted-foreground">
              Data Flow:
            </h3>
            <div className="rounded-lg bg-muted/50 p-4 font-mono text-sm">
              {plan.dataFlow}
            </div>
          </div>

          {/* Action Buttons */}
          {stage === "PLANNING" && (
            <div className="flex gap-3 pt-4">
              <Button onClick={onImplement} className="flex-1" size="lg">
                ✅ Implement this Plan
              </Button>
              <Button
                onClick={onModify}
                variant="outline"
                className="flex-1"
                size="lg"
              >
                <Edit className="mr-2 h-4 w-4" />
                Modify Plan
              </Button>
            </div>
          )}

          {stage === "GENERATING" && (
            <div className="pt-4">
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                Generating your workflow JSON...
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
