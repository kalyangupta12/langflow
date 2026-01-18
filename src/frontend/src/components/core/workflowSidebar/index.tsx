import { useLocation } from "react-router-dom";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar";
import { ENABLE_KNOWLEDGE_BASES } from "@/customization/feature-flags";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { useIsMobile } from "@/hooks/use-mobile";

export default function WorkflowSidebar() {
  const location = useLocation();
  const navigate = useCustomNavigate();
  const isMobile = useIsMobile({ maxWidth: 1024 });

  const handleFilesNavigation = () => {
    navigate("/assets/files");
  };

  const handleKnowledgeNavigation = () => {
    navigate("/assets/knowledge-bases");
  };

  const isDashboardActive = location.pathname === "/" || location.pathname === "/dashboard";
  const isWorkflowsActive = location.pathname.includes("/workflows");
  const isMCPActive = location.pathname.includes("/mcp-servers");
  const isModelProvidersActive = location.pathname.includes("/model-providers");
  const isShortcutsActive = location.pathname.includes("/shortcuts");
  const isMessagesActive = location.pathname.includes("/messages");
  const isFilesActive = location.pathname.includes("/assets/files");
  const isKnowledgeActive = location.pathname.includes("/assets/knowledge-bases");
  const isGeneralSettingsActive = location.pathname.includes("/general-settings");
  const isApiKeysActive = location.pathname === "/api-keys";

  return (
    <Sidebar
      collapsible={isMobile ? "offcanvas" : "none"}
      data-testid="workflow-sidebar"
      className="border-r"
    >
      <SidebarHeader className="border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Main Menu</h2>
        </div>
      </SidebarHeader>

      <SidebarContent className="p-2">
        <div className="space-y-1">
          {/* Dashboard */}
          <Button
            variant={isDashboardActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/dashboard")}
            data-testid="dashboard-nav-button"
          >
            <ForwardedIconComponent name="LayoutDashboard" className="h-4 w-4" />
            <span>Dashboard</span>
          </Button>

          {/* Workflows */}
          <Button
            variant={isWorkflowsActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/workflows")}
            data-testid="workflows-nav-button"
          >
            <ForwardedIconComponent name="Workflow" className="h-4 w-4" />
            <span>Workflows</span>
          </Button>

          {/* MCP Servers */}
          <Button
            variant={isMCPActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/mcp-servers")}
            data-testid="mcp-servers-nav-button"
          >
            <ForwardedIconComponent name="Mcp" className="h-4 w-4" />
            <span>MCP Servers</span>
          </Button>

          {/* Model Providers */}
          <Button
            variant={isModelProvidersActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/model-providers")}
            data-testid="model-providers-nav-button"
          >
            <ForwardedIconComponent name="Brain" className="h-4 w-4" />
            <span>Model Providers</span>
          </Button>

          {/* Training */}
          <Button
            variant={isFilesActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={handleFilesNavigation}
            data-testid="training-nav-button"
          >
            <ForwardedIconComponent name="File" className="h-4 w-4" />
            <span>Training Data</span>
          </Button>

          {/* Shortcuts */}
          <Button
            variant={isShortcutsActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/shortcuts")}
            data-testid="shortcuts-nav-button"
          >
            <ForwardedIconComponent name="Keyboard" className="h-4 w-4" />
            <span>Shortcuts</span>
          </Button>

          {/* Messages */}
          <Button
            variant={isMessagesActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/messages")}
            data-testid="messages-nav-button"
          >
            <ForwardedIconComponent name="MessagesSquare" className="h-4 w-4" />
            <span>Messages</span>
          </Button>
        </div>
      </SidebarContent>

      <SidebarFooter className="border-t p-2">
        <div className="space-y-1">
          {ENABLE_KNOWLEDGE_BASES && (
            <Button
              variant={isKnowledgeActive ? "secondary" : "ghost"}
              className="w-full justify-start gap-2"
              onClick={handleKnowledgeNavigation}
              data-testid="knowledge-nav-button"
            >
              <ForwardedIconComponent name="Library" className="h-4 w-4" />
              <span>Knowledge</span>
            </Button>
          )}

          <Button
            variant={isApiKeysActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/api-keys")}
            data-testid="api-keys-nav-button"
          >
            <ForwardedIconComponent name="Key" className="h-4 w-4" />
            <span>API Keys</span>
          </Button>

          <Button
            variant={isGeneralSettingsActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={() => navigate("/general-settings")}
            data-testid="settings-nav-button"
          >
            <ForwardedIconComponent name="Settings" className="h-4 w-4" />
            <span>Settings</span>
          </Button>
          
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
