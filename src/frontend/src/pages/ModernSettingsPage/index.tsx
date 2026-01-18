import { useState } from "react";
import { useParams } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import GeneralPage from "../SettingsPage/pages/GeneralPage";
import GlobalVariablesPage from "../SettingsPage/pages/GlobalVariablesPage";

export default function ModernSettingsPage() {
  const { scrollId } = useParams();
  const [activeTab, setActiveTab] = useState("general");

  return (
    <div className="flex h-full w-full flex-col p-6 mx-auto max-w-7xl overflow-hidden">
      {/* Header */}
      <div className="flex flex-col gap-2 flex-shrink-0">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Modern Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col mt-6 overflow-hidden">
        <TabsList className="grid w-full max-w-md grid-cols-2 h-12 flex-shrink-0">
          <TabsTrigger value="general" className="gap-2 text-sm">
            <ForwardedIconComponent name="User" className="h-4 w-4" />
            <span>General</span>
          </TabsTrigger>
          <TabsTrigger value="variables" className="gap-2 text-sm">
            <ForwardedIconComponent name="Globe" className="h-4 w-4" />
            <span>Global Variables</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="flex-1 mt-6 overflow-y-auto">
          <GeneralPage />
        </TabsContent>

        <TabsContent value="variables" className="flex-1 mt-6 overflow-y-auto">
          <GlobalVariablesPage />
        </TabsContent>
      </Tabs>
    </div>
  );
}
