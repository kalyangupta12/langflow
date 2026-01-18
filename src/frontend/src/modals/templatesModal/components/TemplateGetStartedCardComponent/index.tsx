import { useParams } from "react-router-dom";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { convertTestName } from "@/components/common/storeCardComponent/utils/convert-test-name";
import { DottedGlowBackground } from "@/components/ui/dotted-glow-background";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { track } from "@/customization/utils/analytics";
import useAddFlow from "@/hooks/flows/use-add-flow";
import { useFolderStore } from "@/stores/foldersStore";
import { updateIds } from "@/utils/reactflowUtils";
import { cn } from "@/utils/utils";
import type { CardData } from "../../../../types/templates/types";

interface TemplateGetStartedCardComponentProps extends CardData {
  loading: boolean;
  onFlowCreating: (loading: boolean) => void;
  onClose?: () => void;
}

export default function TemplateGetStartedCardComponent({
  bgImage,
  bgHorizontalImage,
  icon,
  category,
  flow,
  loading,
  onFlowCreating,
  onClose,
}: TemplateGetStartedCardComponentProps) {
  const addFlow = useAddFlow();
  const navigate = useCustomNavigate();
  const { folderId } = useParams();
  const myCollectionId = useFolderStore((state) => state.myCollectionId);

  const folderIdUrl = folderId ?? myCollectionId;

  const handleClick = () => {
    console.log("Card clicked, loading state:", loading);
    if (loading) return;

    if (flow) {
      console.log("Flow found:", flow.name, "Starting creation...");
      
      track("New Flow Created", { template: `${flow.name} Template` });
      
      onFlowCreating(true);
      updateIds(flow.data!);
      
      addFlow({ flow })
        .then((id) => {
          console.log("✅ Flow created with ID:", id);
          console.log("Immediately navigating to /flow/" + id);
          // Navigate FIRST before updating state to prevent unmounting
          navigate(`/flow/${id}`);
          // Then update state
          setTimeout(() => {
            onFlowCreating(false);
            onClose?.();
          }, 100);
        })
        .catch((error) => {
          console.error("❌ Error creating flow:", error);
          onFlowCreating(false);
        });
    } else {
      console.error("❌ Flow template not found");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  };

  return flow ? (
    <div
      className={cn(
        "group relative flex h-full min-h-[200px] w-full flex-col overflow-hidden rounded-2xl border bg-black transition-all duration-200 md:min-h-[250px]",
        loading 
          ? "cursor-default opacity-60 border-zinc-800" 
          : "cursor-pointer border-zinc-800 hover:border-zinc-700",
      )}
      tabIndex={1}
      onKeyDown={handleKeyDown}
      onClick={handleClick}
    >
      {/* Simple dotted background */}
      <DottedGlowBackground
        className="pointer-events-none"
        opacity={0.8}
        gap={10}
        radius={1.5}
        color="rgba(100, 100, 100, 0.4)"
        glowColor="rgba(200, 200, 200, 0.6)"
        backgroundOpacity={0}
        speedMin={0.3}
        speedMax={1.2}
        speedScale={1}
      />
      
      <div className="relative z-10 flex h-full flex-col items-start gap-2 p-6 md:gap-3 lg:p-8">
        <div className="flex items-center gap-2 text-zinc-500">
          <ForwardedIconComponent name={icon} className="h-4 w-4" />
          <span className="font-mono text-xs font-medium uppercase tracking-wider">
            {category}
          </span>
        </div>
        <div className="flex w-full items-center justify-between">
          <h3
            data-testid={`template-get-started-card-${convertTestName(
              flow?.name,
            )}`}
            className="line-clamp-3 text-lg font-semibold text-white lg:text-xl"
          >
            {flow.name}
          </h3>
          <ForwardedIconComponent
            name="ArrowRight"
            className="ml-2 h-4 w-4 shrink-0 text-zinc-500"
          />
        </div>

        <p className="line-clamp-3 w-full overflow-hidden text-sm text-zinc-400">
          {flow.description}
        </p>
      </div>
    </div>
  ) : (
    <></>
  );
}
