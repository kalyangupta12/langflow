import { useState } from "react";
import { useParams } from "react-router-dom";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { track } from "@/customization/utils/analytics";
import useAddFlow from "@/hooks/flows/use-add-flow";
import type { Category } from "@/types/templates/types";
import { cn } from "@/utils/utils";
import TemplateContentComponent from "@/modals/templatesModal/components/TemplateContentComponent";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import type { CardData } from "@/types/templates/types";
import memoryChatbot from "@/assets/temp-pat-1.png";
import vectorRag from "@/assets/temp-pat-2.png";
import multiAgent from "@/assets/temp-pat-3.png";
import memoryChatbotHorizontal from "@/assets/temp-pat-m-1.png";
import vectorRagHorizontal from "@/assets/temp-pat-m-2.png";
import multiAgentHorizontal from "@/assets/temp-pat-m-3.png";
import TemplateGetStartedCardComponent from "@/modals/templatesModal/components/TemplateGetStartedCardComponent";
import { ENABLE_KNOWLEDGE_BASES } from "@/customization/feature-flags";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { convertTestName } from "@/components/common/storeCardComponent/utils/convert-test-name";

// Extract GetStarted component outside to prevent unmounting on parent re-renders
function GetStartedComponentInline({
  loading,
  onFlowCreating,
}: {
  loading: boolean;
  onFlowCreating: (loading: boolean) => void;
}) {
  const examples = useFlowsManagerStore((state) => state.examples);

  console.log("📊 GetStartedComponentInline - Total examples:", examples.length);

  const filteredExamples = examples.filter((example) => {
    return !(!ENABLE_KNOWLEDGE_BASES && example.name?.includes("Knowledge"));
  });

  console.log("📊 Filtered examples:", filteredExamples.length);

  const cardData: CardData[] = [
    {
      bgImage: memoryChatbot,
      bgHorizontalImage: memoryChatbotHorizontal,
      icon: "MessagesSquare",
      category: "prompting",
      flow: filteredExamples.find(
        (example) => example.name === "Basic Prompting",
      ),
    },
    {
      bgImage: vectorRag,
      bgHorizontalImage: vectorRagHorizontal,
      icon: "Database",
      category: "RAG",
      flow: filteredExamples.find(
        (example) => example.name === "Vector Store RAG",
      ),
    },
    {
      bgImage: multiAgent,
      bgHorizontalImage: multiAgentHorizontal,
      icon: "Bot",
      category: "Agents",
      flow: filteredExamples.find((example) => example.name === "Simple Agent"),
    },
  ];

  console.log("📊 Card data created:", cardData.map(c => ({ name: c.flow?.name, found: !!c.flow })));

  return (
    <div className="flex flex-1 flex-col gap-6 md:gap-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">Get started</h2>
        <p className="text-base text-muted-foreground">
          Start with templates showcasing Langflow's Prompting, RAG, and Agent use cases.
        </p>
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-6 lg:grid-cols-3">
        {cardData.map((card, index) => (
          <TemplateGetStartedCardComponent
            key={index}
            {...card}
            loading={loading}
            onFlowCreating={onFlowCreating}
          />
        ))}
      </div>
    </div>
  );
}

export default function WorkflowTemplateGallery() {
  const [currentTab, setCurrentTab] = useState("get-started");
  const [loading, setLoading] = useState(false);
  const addFlow = useAddFlow();
  const navigate = useCustomNavigate();
  const { folderId } = useParams();

  const handleFlowCreating = (isCreating: boolean) => {
    setLoading(isCreating);
  };

  const handleCreateBlankFlow = () => {
    if (loading) return;

    handleFlowCreating(true);
    track("New Flow Created", { template: "Blank Flow" });

    addFlow()
      .then((id) => {
        console.log("Blank flow created with ID:", id);
        // Add small delay to ensure flow is added to store before navigation
        setTimeout(() => {
          handleFlowCreating(false);
          navigate(`/flow/${id}`);
        }, 300);
      })
      .catch((error) => {
        console.error("Error creating blank flow:", error);
        handleFlowCreating(false);
      });
  };

  // Define categories and their items (same as modal)
  const categories: Category[] = [
    {
      title: "Templates",
      items: [
        { title: "Get started", icon: "SquarePlay", id: "get-started" },
        { title: "All templates", icon: "LayoutPanelTop", id: "all-templates" },
      ],
    },
    {
      title: "Use Cases",
      items: [
        { title: "Assistants", icon: "BotMessageSquare", id: "assistants" },
        { title: "Classification", icon: "Tags", id: "classification" },
        { title: "Coding", icon: "TerminalIcon", id: "coding" },
        {
          title: "Content Generation",
          icon: "Newspaper",
          id: "content-generation",
        },
        { title: "Q&A", icon: "Database", id: "q-a" },
                { title: "Web Scraping", icon: "CodeXml", id: "web-scraping" },

      ],
    },
    {
      title: "Methodology",
      items: [
        { title: "Prompting", icon: "MessagesSquare", id: "chatbots" },
        { title: "RAG", icon: "Database", id: "rag" },
        { title: "Agents", icon: "Bot", id: "agents" },
      ],
    },
  ];

  return (
    <div className="flex h-full bg-background">
      <SidebarProvider defaultOpen={true}>
        <Sidebar collapsible="none" className="max-w-[240px] border-r border-border bg-muted/30">
          <SidebarContent className="gap-0 p-3">
            <div
              className={cn("relative flex items-center gap-2 px-3 py-4")}
            >
              <div
                className={cn(
                  "text-base font-semibold flex h-8 shrink-0 items-center rounded-md leading-none tracking-tight text-foreground",
                )}
              >
                Templates
              </div>
            </div>

            {categories.map((category, index) => (
              <SidebarGroup key={index} className="px-0">
                <SidebarGroupLabel
                  className={`${
                    index === 0
                      ? "hidden"
                      : "mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                  }`}
                >
                  {category.title}
                </SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {category.items.map((link) => (
                      <SidebarMenuItem key={link.id}>
                        <SidebarMenuButton
                          onClick={() => setCurrentTab(link.id)}
                          isActive={currentTab === link.id}
                          data-testid={`side_nav_options_${link.title.toLowerCase().replace(/\s+/g, "-")}`}
                        >
                          {/* coloe change needed here */}
                          <ForwardedIconComponent
                            name={link.icon}
                            className={`h-4 w-4 stroke-2 ${
                              currentTab === link.id
                                ? "text-accent-emerald-foreground"
                                : "text-muted-foreground"
                            }`}
                          />
                          <span
                            data-testid={`category_title_${convertTestName(link.title)}`}
                          >
                            {link.title}
                          </span>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            ))}
          </SidebarContent>
        </Sidebar>
        
        <main className="flex flex-1 flex-col gap-6 overflow-auto p-8 md:gap-8">
          {currentTab === "get-started" ? (
            <GetStartedComponentInline
              loading={loading}
              onFlowCreating={handleFlowCreating}
            />
          ) : (
            <TemplateContentComponent
              currentTab={currentTab}
              categories={categories.flatMap((category) => category.items)}
              loading={loading}
              onFlowCreating={handleFlowCreating}
            />
          )}
          <div className="flex w-full flex-col justify-between gap-4 rounded-xl border border-border bg-card p-6 shadow-sm sm:flex-row sm:items-center">
            <div className="flex flex-col items-start justify-center gap-1">
              <div className="text-base font-semibold text-foreground">Start from scratch</div>
              <div className="text-sm text-muted-foreground">
                Begin with a fresh flow to build from scratch.
              </div>
            </div>
            <Button
              onClick={handleCreateBlankFlow}
              size="default"
              data-testid="blank-flow"
              className={cn(
                "shrink-0 gap-2 font-semibold transition-all duration-200",
                loading ? "cursor-default opacity-60" : "cursor-pointer hover:scale-105 hover:shadow-md",
              )}
              disabled={loading}
            >
              <ForwardedIconComponent
                name="Plus"
                className="h-4 w-4 shrink-0"
              />
              Blank Flow
            </Button>
          </div>
        </main>
      </SidebarProvider>
    </div>
  );
}
