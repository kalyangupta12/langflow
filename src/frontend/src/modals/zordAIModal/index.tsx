import { useState, useRef, useEffect } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { Loader2, Send, Sparkles, Download, Plus, Check } from "lucide-react";
import { toast } from "sonner";
import * as ZordAPI from "@/controllers/API/zord";

export type ZordMessageType = 
  | "text" 
  | "mcq" 
  | "plan" 
  | "json" 
  | "loading" 
  | "error";

export interface ZordMessage {
  id: string;
  role: "user" | "assistant";
  type: ZordMessageType;
  content: string | any;
  timestamp: Date;
}

export interface ZordMCQ {
  id: string;
  question: string;
  options: { id: string; label: string; value: string }[];
}

interface ZordAIModalProps {
  open: boolean;
  onClose: () => void;
}

export default function ZordAIModal({ open, onClose }: ZordAIModalProps) {
  const [messages, setMessages] = useState<ZordMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      type: "text",
      content: "👋 Welcome to **Zord AI**! I'm your Langflow workflow architect.\n\nDescribe what you want to build, and I'll guide you through creating the perfect workflow. I'll ask a few questions to clarify details, then generate a complete workflow that you can directly add to your account!",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentMCQs, setCurrentMCQs] = useState<ZordMCQ[]>([]);
  const [mcqAnswers, setMCQAnswers] = useState<Record<string, string>>({});
  const [generatedJSON, setGeneratedJSON] = useState<any>(null);
  const [currentPlan, setCurrentPlan] = useState<ZordAPI.ZordPlan | null>(null);
  const [userPrompt, setUserPrompt] = useState<string>("");
  const [conversationHistory, setConversationHistory] = useState<Array<{ role: string; content: string }>>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollRef.current) {
      const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages]);

  const addMessage = (role: "user" | "assistant", type: ZordMessageType, content: any) => {
    const newMessage: ZordMessage = {
      id: `${role}-${Date.now()}`,
      role,
      type,
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const addLoadingMessage = () => {
    addMessage("assistant", "loading", "");
  };

  const removeLoadingMessage = () => {
    setMessages((prev) => prev.filter((msg) => msg.type !== "loading"));
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setUserPrompt(userMessage);
    addMessage("user", "text", userMessage);

    // Add to conversation history
    const newHistory = [...conversationHistory, { role: "user", content: userMessage }];
    setConversationHistory(newHistory);

    setIsLoading(true);
    addLoadingMessage();

    try {
      const response = await ZordAPI.analyzeIntent({
        prompt: userMessage,
        conversation_history: newHistory,
      });

      removeLoadingMessage();
      setCurrentMCQs(response.mcqs);
      addMessage("assistant", "text", response.message || "Great! I have a few questions to finalize the technical details:");
      addMessage("assistant", "mcq", response.mcqs);

      // Add AI response to history
      setConversationHistory([...newHistory, { role: "assistant", content: response.message }]);
    } catch (error) {
      removeLoadingMessage();
      const errorMessage = error instanceof Error ? error.message : "An error occurred";
      addMessage("assistant", "error", `Sorry, I encountered an error: ${errorMessage}`);
      toast.error("Failed to process your request");
    } finally {
      setIsLoading(false);
    }
  };

  const handleMCQAnswer = (mcqId: string, answer: string) => {
    setMCQAnswers((prev) => ({ ...prev, [mcqId]: answer }));
  };

  const handleMCQSubmit = async () => {
    if (Object.keys(mcqAnswers).length !== currentMCQs.length) {
      toast.error("Please answer all questions");
      return;
    }

    setIsLoading(true);
    addLoadingMessage();

    try {
      const planResponse = await ZordAPI.generatePlan({
        prompt: userPrompt,
        answers: mcqAnswers,
        conversation_history: conversationHistory,
      });

      removeLoadingMessage();
      setCurrentPlan(planResponse.plan);

      // Convert data_flow to dataFlow for UI compatibility
      const planForUI = {
        ...planResponse.plan,
        dataFlow: planResponse.plan.data_flow,
      };

      addMessage("assistant", "text", planResponse.message || "Perfect! Here's your workflow plan:");
      addMessage("assistant", "plan", planForUI);

      // Add to conversation history
      setConversationHistory([...conversationHistory, { role: "assistant", content: planResponse.message }]);

      // Auto-generate JSON after plan
      setTimeout(async () => {
        setIsLoading(true);
        addLoadingMessage();

        try {
          const jsonResponse = await ZordAPI.generateJSON({
            plan: planResponse.plan,
            conversation_history: conversationHistory,
          });

          removeLoadingMessage();
          setGeneratedJSON(jsonResponse.json);
          addMessage("assistant", "text", jsonResponse.message || "🎉 Your workflow is ready!");
          addMessage("assistant", "json", jsonResponse.json);

          // Add to conversation history
          setConversationHistory([...conversationHistory, { role: "assistant", content: jsonResponse.message }]);
        } catch (error) {
          removeLoadingMessage();
          const errorMessage = error instanceof Error ? error.message : "An error occurred";
          toast.error(`Failed to generate workflow JSON: ${errorMessage}`);
        } finally {
          setIsLoading(false);
        }
      }, 500);
    } catch (error) {
      removeLoadingMessage();
      const errorMessage = error instanceof Error ? error.message : "An error occurred";
      toast.error(`Failed to generate plan: ${errorMessage}`);
    } finally {
      setIsLoading(false);
      setCurrentMCQs([]);
      setMCQAnswers({});
    }
  };

  const handleDownloadJSON = () => {
    if (!generatedJSON) return;

    const blob = new Blob([JSON.stringify(generatedJSON, null, 2)], {
      type: "application/json",
    });
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

  const handleCreateFlow = async () => {
    if (!generatedJSON) return;

    setIsLoading(true);
    const loadingToast = toast.loading("Creating flow in your account...");

    try {
      const response = await ZordAPI.createFlow({
        flow_json: generatedJSON,
      });

      toast.dismiss(loadingToast);
      toast.success(response.message || "Flow created successfully!", {
        description: `Flow "${response.name}" has been added to your account`,
      });

      setTimeout(() => {
        onClose();
        // Optionally refresh the flows list or navigate to the new flow
        window.location.reload();
      }, 1500);
    } catch (error) {
      toast.dismiss(loadingToast);
      const errorMessage = error instanceof Error ? error.message : "An error occurred";
      toast.error("Failed to create flow", {
        description: errorMessage + ". Please try downloading and importing manually",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderMarkdown = (text: string) => {
    // Simple markdown rendering
    return text
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return <strong key={i}>{line.slice(2, -2)}</strong>;
        }
        return <p key={i} className="mb-2 last:mb-0">{line}</p>;
      });
  };

  const renderMessage = (message: ZordMessage) => {
    switch (message.type) {
      case "loading":
        return (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        );

      case "text":
        return (
          <div className="text-sm leading-relaxed">
            {renderMarkdown(message.content as string)}
          </div>
        );

      case "mcq":
        const mcqs = message.content as ZordMCQ[];
        return (
          <div className="space-y-4 mt-2">
            {mcqs.map((mcq) => (
              <Card key={mcq.id} className="p-4">
                <p className="font-medium mb-3">{mcq.question}</p>
                <div className="space-y-2">
                  {mcq.options.map((option) => (
                    <button
                      key={option.id}
                      onClick={() => handleMCQAnswer(mcq.id, option.value)}
                      className={`w-full text-left px-4 py-2 rounded-lg border transition-all ${
                        mcqAnswers[mcq.id] === option.value
                          ? "border-primary bg-primary/10 font-medium"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <span className="font-mono text-sm mr-2">{option.label}.</span>
                      {option.value}
                    </button>
                  ))}
                </div>
              </Card>
            ))}
            {mcqs.length > 0 && (
              <Button
                onClick={handleMCQSubmit}
                disabled={Object.keys(mcqAnswers).length !== mcqs.length}
                className="w-full"
              >
                Continue
              </Button>
            )}
          </div>
        );

      case "plan":
        const plan = message.content;
        return (
          <Card className="p-4 border-blue-500/20 bg-blue-500/5">
            <h3 className="font-semibold text-lg mb-3">{plan.title}</h3>
            <div className="space-y-3 mb-4">
              {plan.steps.map((step: any) => (
                <div key={step.id} className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-medium">
                    {step.id}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">{step.description}</p>
                    {step.component && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Components: {step.component}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="pt-3 border-t">
              <p className="text-xs text-muted-foreground">Data Flow:</p>
              <p className="text-sm font-mono mt-1">{plan.dataFlow}</p>
            </div>
          </Card>
        );

      case "json":
        return (
          <Card className="p-4 border-green-500/20 bg-green-500/5">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-5 w-5 text-green-500" />
              <h3 className="font-semibold">Workflow Ready</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              I've created a workflow scaffold for you! The plan has been added to the workflow description. 
              Click "Create Flow" to add it to your account, then add components based on the plan.
            </p>
            <div className="flex gap-2">
              <Button onClick={handleCreateFlow} className="flex-1 gap-2">
                <Plus className="h-4 w-4" />
                Create Flow
              </Button>
              <Button onClick={handleDownloadJSON} variant="outline" className="flex-1 gap-2">
                <Download className="h-4 w-4" />
                Download JSON
              </Button>
            </div>
          </Card>
        );

      case "error":
        return (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-lg">
            {message.content as string}
          </div>
        );

      default:
        return null;
    }
  };
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] p-0 flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold">Zord AI</h2>
            <p className="text-sm text-muted-foreground">
              Your Intelligent Workflow Architect
            </p>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-6" ref={scrollRef}>
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <Sparkles className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={`flex-1 max-w-[80%] ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground rounded-2xl px-4 py-3"
                      : ""
                  }`}
                >
                  {renderMessage(message)}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your workflow idea..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !input.trim()} size="icon">
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
}
