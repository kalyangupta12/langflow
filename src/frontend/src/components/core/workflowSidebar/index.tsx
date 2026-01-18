import { useState } from "react";
import { useLocation } from "react-router-dom";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar";
import { ENABLE_KNOWLEDGE_BASES } from "@/customization/feature-flags";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { createFileUpload } from "@/helpers/create-file-upload";
import { getObjectsFromFilelist } from "@/helpers/get-objects-from-filelist";
import useUploadFlow from "@/hooks/flows/use-upload-flow";
import useAlertStore from "@/stores/alertStore";
import { useIsMobile } from "@/hooks/use-mobile";

export default function WorkflowSidebar() {
  const location = useLocation();
  const navigate = useCustomNavigate();
  const uploadFlow = useUploadFlow();
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const isMobile = useIsMobile({ maxWidth: 1024 });
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadWorkflow = async () => {
    try {
      setIsUploading(true);
      const files: File[] = await createFileUpload();
      
      if (files?.length === 0) {
        setIsUploading(false);
        return;
      }

      const objects = await getObjectsFromFilelist<any>(files);
      
      if (objects.every((flow) => flow.data?.nodes)) {
        await uploadFlow({ files });
        setSuccessData({
          title: "Workflow uploaded successfully",
        });
      } else {
        setErrorData({
          title: "Invalid workflow file",
          list: ["Please upload a valid Langflow workflow file"],
        });
      }
    } catch (error) {
      setErrorData({
        title: "Upload failed",
        list: [error instanceof Error ? error.message : "An error occurred"],
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleFilesNavigation = () => {
    navigate("/assets/files");
  };

  const handleKnowledgeNavigation = () => {
    navigate("/assets/knowledge-bases");
  };

  const isFilesActive = location.pathname.includes("/assets/files");
  const isKnowledgeActive = location.pathname.includes("/assets/knowledge-bases");

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
          <ShadTooltip content="Upload workflow from file" side="right">
            <Button
              variant="ghost"
              className="w-full justify-start gap-2"
              onClick={handleUploadWorkflow}
              disabled={isUploading}
              data-testid="upload-workflow-button"
            >
              <ForwardedIconComponent 
                name={isUploading ? "Loader2" : "Upload"} 
                className={`h-4 w-4 ${isUploading ? "animate-spin" : ""}`}
              />
              <span>Upload Workflow</span>
            </Button>
            
          </ShadTooltip>
          
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
            variant={isFilesActive ? "secondary" : "ghost"}
            className="w-full justify-start gap-2"
            onClick={handleFilesNavigation}
            data-testid="my-files-nav-button"
          >
            <ForwardedIconComponent name="File" className="h-4 w-4" />
            <span>My Files</span>
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
