import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Copy, CheckCircle2, RotateCcw } from "lucide-react";
import { toast } from "sonner"
// import useAlertStore from "@/stores/alertStore";

interface ZordJSONOutputProps {
  json: string;
  onReset: () => void;
}

export default function ZordJSONOutput({ json, onReset }: ZordJSONOutputProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
      toast.success("Copied!", {
        description: "JSON copied to clipboard",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error("Failed to copy", {
        description: "Please try again",
      });
    }
  };

  const handleDownload = () => {
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `langflow-workflow-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success("Downloaded!", {
      description: "Workflow JSON has been downloaded",
    });
  };

  return (
    <div className="space-y-4">
      <Card className="border-green-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="h-5 w-5" />
            Workflow Generated Successfully
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* JSON Preview */}
          <div className="relative">
            <pre className="max-h-[400px] overflow-auto rounded-lg bg-muted p-4 text-xs">
              <code>{json}</code>
            </pre>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleDownload} className="flex-1" variant="default">
              <Download className="mr-2 h-4 w-4" />
              Download JSON
            </Button>
            <Button
              onClick={handleCopy}
              className="flex-1"
              variant="outline"
              disabled={copied}
            >
              {copied ? (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copy to Clipboard
                </>
              )}
            </Button>
          </div>

          {/* Instructions */}
          <div className="rounded-lg bg-blue-50 dark:bg-blue-950/20 p-4 space-y-2">
            <h4 className="font-semibold text-sm">How to use this workflow:</h4>
            <ol className="text-sm space-y-1 list-decimal list-inside text-muted-foreground">
              <li>Download or copy the JSON file</li>
              <li>Go to your Langflow dashboard</li>
              <li>Click "Create Workflow" → "Import from JSON"</li>
              <li>Upload or paste the JSON</li>
              <li>Configure your API keys and test the workflow</li>
            </ol>
          </div>

          {/* Reset Button */}
          <Button onClick={onReset} variant="ghost" className="w-full">
            <RotateCcw className="mr-2 h-4 w-4" />
            Create Another Workflow
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
