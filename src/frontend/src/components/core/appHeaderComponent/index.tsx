import { useEffect, useRef, useState } from "react";
import AlertDropdown from "@/alerts/alertDropDown";
// import LangflowLogo from "@/assets/LangflowLogo.svg?react";
import AgentsTrailLogo from "@/assets/AgentsTrail.svg?react";
import { AssistantButton } from "@/components/common/assistant";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import ModelProviderCount from "@/components/common/modelProviderCountComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import CustomAccountMenu from "@/customization/components/custom-AccountMenu";
import CustomLangflowCounts from "@/customization/components/custom-langflow-counts";
import { CustomOrgSelector } from "@/customization/components/custom-org-selector";
import { LANGFLOW_AGENTIC_EXPERIENCE } from "@/customization/feature-flags";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import useTheme from "@/customization/hooks/use-custom-theme";
import useAlertStore from "@/stores/alertStore";
import FlowMenu from "./components/FlowMenu";
import { Bot } from "lucide-react";

export default function AppHeader(): JSX.Element {
  const notificationCenter = useAlertStore((state) => state.notificationCenter);
  const navigate = useCustomNavigate();
  const [activeState, setActiveState] = useState<"notifications" | null>(null);
  const notificationRef = useRef<HTMLButtonElement | null>(null);
  const notificationContentRef = useRef<HTMLDivElement | null>(null);
  useTheme();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as Node;
      const isNotificationButton = notificationRef.current?.contains(target);
      const isNotificationContent =
        notificationContentRef.current?.contains(target);

      if (!isNotificationButton && !isNotificationContent) {
        setActiveState(null);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const getNotificationBadge = () => {
    const baseClasses = "absolute h-1 w-1 rounded-full bg-destructive";
    return notificationCenter
      ? `${baseClasses} right-[0.3rem] top-[5px]`
      : "hidden";
  };

  return (
    <div
      className={`z-10 flex h-[64px] w-full items-center justify-between border-b pr-5 pl-2.5 dark:bg-background`}
      data-testid="app-header"
    >
      {/* Left Section */}
      <div
        className={`z-30 flex shrink-0 items-center gap-1`}
        data-testid="header_left_section_wrapper"
      >
        <Button
          unstyled
          onClick={() => navigate("/")}
          className="flex h-16 w-16 items-center"
          data-testid="icon-ChevronLeft"
        >
          <AgentsTrailLogo className="h-14 w-14" />
        </Button>
        <span className="text-xl font-semibold tracking-tight" style={{ fontFamily: '"Space Grotesk", sans-serif' }}>
          AgentsTrail AI  
        </span>
        <span className="text-xl text-emerald-100 font-semibold tracking-tight animate-pulse" style={{ fontFamily: '"Space Grotesk", sans-serif' }}>
          | Where AI Agents Meet Web3  
        </span>
        <CustomOrgSelector />
      </div>

      {/* Middle Section */}
      <div className="absolute left-1/2 -translate-x-1/2">
        <FlowMenu />
      </div>

{/* Right Section */}
<div
  className={`relative left-3 z-30 flex shrink-0 items-center gap-3`}
  data-testid="header_right_section_wrapper"
>
  {false && <ModelProviderCount />}
  {LANGFLOW_AGENTIC_EXPERIENCE && <AssistantButton type="header" />}
  {/* <div className="hidden pr-2 whitespace-nowrap lg:inline-flex lg:items-center">
    <CustomLangflowCounts />
  </div> */}
  <ShadTooltip
    content="Chat with Zod Assistant"
    side="bottom"
    styleClasses="z-10"
  >
    <Button
      unstyled
      onClick={() => {
        // Add your bot chat handler here
        console.log("Open bot chat");
      }}
      className="hit-area-hover group relative items-center rounded-md px-3 py-1.5 text-muted-foreground hover:text-primary"
      data-testid="bot_chat_button"
    >
      <div className="flex items-center gap-2">
        <Bot
          name="MessageSquare"
          className="h-4 w-4"
          strokeWidth={2}
        />
        <span className="text-sm font-medium">Zod Bot</span>
      </div>
    </Button>
  </ShadTooltip>

  <Button
    onClick={() => {
      // Add your upgrade handler here
      console.log("Navigate to upgrade page");
    }}
    className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white px-4 py-1.5 h-auto text-sm font-semibold rounded-md shadow-sm transition-all"
    data-testid="upgrade_pro_button"
  >
    <div className="flex items-center gap-2">
      <ForwardedIconComponent
        name="Sparkles"
        className="h-4 w-4"
        strokeWidth={2}
      />
      <span>Upgrade to Pro</span>
    </div>
  </Button>
  <AlertDropdown
          notificationRef={notificationContentRef}
          onClose={() => setActiveState(null)}
        >
          <ShadTooltip
            content="Notifications and errors"
            side="bottom"
            styleClasses="z-10"
          >
            <AlertDropdown onClose={() => setActiveState(null)}>
              <Button
                ref={notificationRef}
                unstyled
                onClick={() =>
                  setActiveState((prev) =>
                    prev === "notifications" ? null : "notifications",
                  )
                }
                data-testid="notification_button"
              >
                <div className="hit-area-hover group relative items-center rounded-md px-2 py-2 text-muted-foreground">
                  <span className={getNotificationBadge()} />
                  <ForwardedIconComponent
                    name="Bell"
                    className={`side-bar-button-size h-4 w-4 ${
                      activeState === "notifications"
                        ? "text-primary"
                        : "text-muted-foreground group-hover:text-primary"
                    }`}
                    strokeWidth={2}
                  />
                  <span className="hidden whitespace-nowrap">
                    Notifications
                  </span>
                </div>
              </Button>
            </AlertDropdown>
          </ShadTooltip>
        </AlertDropdown>
        <Separator
          orientation="vertical"
          className="my-auto h-7 dark:border-zinc-700"
        />

        <div className="flex">
          <CustomAccountMenu />
        </div>
      </div>
    </div>
  );
}
