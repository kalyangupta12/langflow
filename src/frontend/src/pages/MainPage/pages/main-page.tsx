import { useState } from "react";
import { Outlet } from "react-router-dom";
import WorkflowSidebar from "@/components/core/workflowSidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import CustomEmptyPageCommunity from "@/customization/components/custom-empty-page";
import CustomLoader from "@/customization/components/custom-loader";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import ModalsComponent from "../components/modalsComponent";

export default function CollectionPage(): JSX.Element {
  const [openModal, setOpenModal] = useState(false);
  const flows = useFlowsManagerStore((state) => state.flows);
  const examples = useFlowsManagerStore((state) => state.examples);

  // Workflow-first architecture with sidebar
  return (
    <SidebarProvider defaultOpen={true}>
      <main className="flex h-full w-full overflow-hidden">
        <WorkflowSidebar />
        {flows && examples ? (
          <div
            className={`relative mx-auto flex h-full w-full flex-col overflow-hidden`}
          >
            {flows?.length !== examples?.length ? (
              <Outlet />
            ) : (
              <CustomEmptyPageCommunity setOpenModal={setOpenModal} />
            )}
          </div>
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <CustomLoader remSize={30} />
          </div>
        )}
        <ModalsComponent
          openModal={openModal}
          setOpenModal={setOpenModal}
        />
      </main>
    </SidebarProvider>
  );
}
