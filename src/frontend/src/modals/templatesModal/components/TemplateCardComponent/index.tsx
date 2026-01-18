import { convertTestName } from "@/components/common/storeCardComponent/utils/convert-test-name";
import { swatchColors } from "@/utils/styleUtils";
import { cn, getNumberFromString } from "@/utils/utils";
import IconComponent, {
  ForwardedIconComponent,
} from "../../../../components/common/genericIconComponent";
import type { TemplateCardComponentProps } from "../../../../types/templates/types";

interface TemplateCardComponentExtendedProps
  extends TemplateCardComponentProps {
  disabled?: boolean;
}

export default function TemplateCardComponent({
  example,
  onClick,
  disabled = false,
}: TemplateCardComponentExtendedProps) {
  const swatchIndex =
    (example.gradient && !isNaN(parseInt(example.gradient))
      ? parseInt(example.gradient)
      : getNumberFromString(example.gradient ?? example.name)) %
    swatchColors.length;

  const handleKeyDown = (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onClick();
      if (!disabled) onClick();
    }
  };

  return (
    <div
      data-testid={`template-${convertTestName(example.name)}`}
      className={cn(
        "group flex gap-4 overflow-hidden rounded-lg border border-border bg-card p-4 transition-all duration-300 hover:shadow-lg hover:border-primary/50",
        disabled ? "cursor-default opacity-60" : "cursor-pointer hover:scale-[1.02]",
      )}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={handleKeyDown}
      onClick={() => !disabled && onClick()}
    >
      <div
        className={cn(
          "relative h-20 w-20 shrink-0 overflow-hidden rounded-lg p-4 outline-none ring-ring transition-transform duration-300 group-hover:scale-105",
          swatchColors[swatchIndex],
        )}
      >
        <IconComponent
          name={example.icon || "FileText"}
          className="absolute left-1/2 top-1/2 h-10 w-10 -translate-x-1/2 -translate-y-1/2 duration-300 group-hover:scale-110 group-focus-visible:scale-110"
        />
      </div>
      <div className="flex flex-1 flex-col justify-between gap-1">
        <div
          data-testid="text_card_container"
          role={convertTestName(example.name)}
        >
          <div className="flex w-full items-center justify-between">
            <h3
              className="line-clamp-2 text-base font-semibold text-foreground"
              data-testid={`template_${convertTestName(example.name)}`}
            >
              {example.name}
            </h3>
            <ForwardedIconComponent
              name="ArrowRight"
              className="h-5 w-5 shrink-0 translate-x-0 text-primary opacity-0 transition-all duration-300 group-hover:translate-x-2 group-hover:opacity-100 group-focus-visible:translate-x-2 group-focus-visible:opacity-100"
            />
          </div>
          <p className="mt-1.5 line-clamp-2 text-sm text-muted-foreground">
            {example.description}
          </p>
        </div>
      </div>
    </div>
  );
}
