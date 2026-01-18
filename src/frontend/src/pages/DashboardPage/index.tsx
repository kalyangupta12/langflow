import { useEffect, useState } from "react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import useAlertStore from "@/stores/alertStore";
import { useGetRefreshFlowsQuery } from "@/controllers/API/queries/flows/use-get-refresh-flows-query";
import { api } from "@/controllers/API/api";
import type { FlowType } from "@/types/flow";

interface Schedule {
  id: string;
  flow_id: string;
  frequency: string;
  schedule_time: string;
  status: string;
  last_run_at?: string;
  last_run_status?: string;
  next_run_at?: string;
  last_run_error?: string;
}

export default function DashboardPage() {
  const flows = useFlowsManagerStore((state) => state.flows);
  const { data: flowsData } = useGetRefreshFlowsQuery({ get_all: true });
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isScheduleDialogOpen, setIsScheduleDialogOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("");
  const [scheduleFrequency, setScheduleFrequency] = useState<string>("");
  const [scheduleTime, setScheduleTime] = useState<string>("");
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const itemsPerPage = 5;
  
  const fetchSchedules = async () => {
    try {
      const { data } = await api.get("/api/v1/schedules/");
      console.log("Fetched schedules:", data);
      setSchedules(data);
    } catch (error) {
      console.error("Error fetching schedules:", error);
    }
  };
  
  useEffect(() => {
    fetchSchedules();
  }, []);
  
  useEffect(() => {
    // Flows will be automatically set by the query
  }, [flowsData]);

  // Calculate stats from actual flows
  const totalWorkflows = flows?.length || 0;
  const activeFlows = flows?.filter((f) => !f.is_component).length || 0;
  
  // Get all workflows (non-components) sorted by updated_at
  const allWorkflows = flows
    ?.filter((f) => !f.is_component)
    ?.sort((a, b) => {
      const dateA = new Date(a.updated_at || 0).getTime();
      const dateB = new Date(b.updated_at || 0).getTime();
      return dateB - dateA;
    }) || [];

  // Filter workflows based on search
  const filteredWorkflows = allWorkflows.filter((flow) =>
    flow.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Calculate pagination
  const totalPages = Math.ceil(filteredWorkflows.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const recentWorkflows = filteredWorkflows.slice(startIndex, endIndex);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hr ago`;
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  };

  // Extract model from flow data
  const getModelFromFlow = (flow: FlowType): string => {
    try {
      const nodes = flow.data?.nodes || [];
      for (const node of nodes) {
        const modelName = node.data?.node?.template?.model_name?.value;
        const model = node.data?.node?.template?.model?.value;
        
        // Check model_name first
        if (modelName) {
          if (typeof modelName === 'string') return modelName;
          if (typeof modelName === 'object' && modelName?.name) return modelName.name;
        }
        
        // Check model
        if (model) {
          if (typeof model === 'string') return model;
          if (typeof model === 'object' && model?.name) return model.name;
        }
      }
      return "N/A";
    } catch {
      return "N/A";
    }
  };

  // Calculate most used model from flows
  const getMostUsedModel = (): string => {
    if (!flows || flows.length === 0) return "N/A";
    
    const modelCounts: { [key: string]: number } = {};
    
    flows.forEach((flow) => {
      const model = getModelFromFlow(flow);
      if (model && model !== "N/A") {
        modelCounts[model] = (modelCounts[model] || 0) + 1;
      }
    });
    
    const sortedModels = Object.entries(modelCounts).sort((a, b) => b[1] - a[1]);
    return sortedModels.length > 0 ? sortedModels[0][0] : "N/A";
  };

  const mostUsedModel = getMostUsedModel();

  // Mock data for charts (can be replaced with actual API data)
  const stats = {
    taskSuccessRate: 96.7,
    taskSuccessChange: 4,
    avgExecutionTime: "12.4m",
    avgExecutionChange: -27,
  };

  const agentsByStatus = {
    total: totalWorkflows,
    active: activeFlows,
    idle: Math.max(0, totalWorkflows - activeFlows),
    offline: 0,
  };

  const tasksBreakdown = [
    { date: "Feb 03", completed: 12, pending: 5, failed: 3 },
    { date: "Feb 04", completed: 15, pending: 7, failed: 2 },
    { date: "Feb 05", completed: 11, pending: 6, failed: 3 },
    { date: "Feb 06", completed: 13, pending: 8, failed: 4 },
    { date: "Feb 07", completed: 16, pending: 9, failed: 2 },
    { date: "Feb 08", completed: 14, pending: 7, failed: 3 },
    { date: "Feb 09", completed: 12, pending: 6, failed: 2 },
  ];

  const handleScheduleWorkflow = () => {
    setEditingSchedule(null);
    setSelectedWorkflow("");
    setScheduleFrequency("");
    setScheduleTime("");
    setIsScheduleDialogOpen(true);
  };

  const handleEditSchedule = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    setSelectedWorkflow(schedule.flow_id);
    setScheduleFrequency(schedule.frequency);
    setScheduleTime(schedule.schedule_time);
    setIsScheduleDialogOpen(true);
  };

  const handleSaveSchedule = async () => {
    if (!selectedWorkflow || !scheduleFrequency || !scheduleTime) {
      setErrorData({
        title: "Missing Information",
        list: ["Please fill in all fields: workflow, frequency, and time."],
      });
      return;
    }

    try {
      const isEditing = !!editingSchedule;
      const payload = {
        flow_id: selectedWorkflow,
        frequency: scheduleFrequency,
        schedule_time: scheduleTime,
      };

      if (isEditing) {
        await api.patch(`/api/v1/schedules/${editingSchedule.id}`, payload);
      } else {
        await api.post("/api/v1/schedules/", payload);
      }

      await fetchSchedules();
      
      const workflowName = flows?.find((f) => f.id === selectedWorkflow)?.name || 'Unknown';
      setSuccessData({
        title: `Schedule ${isEditing ? 'updated' : 'created'} successfully for ${workflowName}!`,
      });

      // Reset form
      setSelectedWorkflow("");
      setScheduleFrequency("");
      setScheduleTime("");
      setEditingSchedule(null);
      setIsScheduleDialogOpen(false);
    } catch (error) {
      console.error("Error saving schedule:", error);
      setErrorData({
        title: "Failed to save schedule",
        list: [error instanceof Error ? error.message : "Please try again."],
      });
    }
  };
  const handleDeleteSchedule = async (scheduleId: string) => {
    if (!confirm("Are you sure you want to delete this schedule?")) return;
    
    try {
      await api.delete(`/api/v1/schedules/${scheduleId}`);

      await fetchSchedules();
      setSuccessData({ title: "Schedule deleted successfully!" });
    } catch (error) {
      console.error("Error deleting schedule:", error);
      setErrorData({
        title: "Failed to delete schedule",
        list: [error instanceof Error ? error.message : "Please try again."],
      });
    }
  };

  const handlePauseSchedule = async (scheduleId: string) => {
    try {
      await api.post(`/api/v1/schedules/${scheduleId}/pause`);

      await fetchSchedules();
      setSuccessData({ title: "Schedule paused successfully!" });
    } catch (error) {
      console.error("Error pausing schedule:", error);
      setErrorData({
        title: "Failed to pause schedule",
        list: [error instanceof Error ? error.message : "Please try again."],
      });
    }
  };

  const handleResumeSchedule = async (scheduleId: string) => {
    try {
      await api.post(`/api/v1/schedules/${scheduleId}/resume`);

      await fetchSchedules();
      setSuccessData({ title: "Schedule resumed successfully!" });
    } catch (error) {
      console.error("Error resuming schedule:", error);
      setErrorData({
        title: "Failed to resume schedule",
        list: [error instanceof Error ? error.message : "Please try again."],
      });
    }
  };

  const getScheduleForFlow = (flowId: string): Schedule | undefined => {
    return schedules.find((s) => s.flow_id === flowId);
  };
  return (
    <div className="flex h-full w-full flex-col gap-6 p-6 overflow-y-auto">
      {/* Header with Schedule Button */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Monitor and manage your workflows
          </p>
        </div>
        <Button onClick={handleScheduleWorkflow} className="gap-2">
          <ForwardedIconComponent name="Calendar" className="h-4 w-4" />
          Schedule Workflow
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Workflows */}
        <div className="rounded-lg border p-6 bg-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-3xl font-bold">{totalWorkflows}</p>
              <p className="text-sm text-muted-foreground mt-1">Total workflows</p>
            </div>
            <div className="rounded-lg bg-blue-100 dark:bg-blue-900/30 p-2">
              <ForwardedIconComponent name="Bot" className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>

        {/* Active Flows */}
        <div className="rounded-lg border p-6 bg-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-3xl font-bold">{activeFlows}</p>
              <p className="text-sm text-muted-foreground mt-1">Active workflows</p>
            </div>
            <div className="flex items-center gap-1 text-xs font-medium text-green-600">
              <ForwardedIconComponent name="Activity" className="h-3 w-3" />
            </div>
          </div>
        </div>

        {/* Components */}
        <div className="rounded-lg border p-6 bg-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-3xl font-bold">{flows?.filter((f) => f.is_component).length || 0}</p>
              <p className="text-sm text-muted-foreground mt-1">Components</p>
            </div>
            <div className="rounded-lg bg-purple-100 dark:bg-purple-900/30 p-2">
              <ForwardedIconComponent name="Blocks" className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>

        {/* Most Used Model */}
        <div className="rounded-lg border p-6 bg-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-3xl font-bold">{mostUsedModel}</p>
              <p className="text-sm text-muted-foreground mt-1">Most used model</p>
            </div>
            <div className="rounded-lg bg-amber-100 dark:bg-amber-900/30 p-2">
              <ForwardedIconComponent name="Brain" className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Schedule Workflow Dialog */}
      <Dialog open={isScheduleDialogOpen} onOpenChange={setIsScheduleDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{editingSchedule ? 'Edit Schedule' : 'Schedule Workflow'}</DialogTitle>
            <DialogDescription>
              {editingSchedule ? 'Update the schedule for your workflow' : 'Set up a schedule for your workflow to run automatically'}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="workflow">Select Workflow</Label>
              <Select value={selectedWorkflow} onValueChange={setSelectedWorkflow}>
                <SelectTrigger id="workflow">
                  <SelectValue placeholder="Choose a workflow" />
                </SelectTrigger>
                <SelectContent>
                  {allWorkflows.map((flow) => (
                    <SelectItem key={flow.id} value={flow.id}>
                      {flow.icon && <span className="mr-2">{flow.icon}</span>}
                      {flow.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="frequency">Frequency</Label>
              <Select value={scheduleFrequency} onValueChange={setScheduleFrequency}>
                <SelectTrigger id="frequency">
                  <SelectValue placeholder="Choose frequency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="once">Once</SelectItem>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="time">Time</Label>
              <div className="relative">
                <Input
                  id="time"
                  type="time"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  className="w-full pr-10 [&::-webkit-calendar-picker-indicator]:hidden"
                  style={{ colorScheme: 'dark' }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById('time') as HTMLInputElement;
                    input?.showPicker?.();
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <ForwardedIconComponent name="Clock" className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsScheduleDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleSaveSchedule}>
              Save Schedule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Workflow Monitor Table */}
      <div className="rounded-lg border bg-card">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Recent Workflows</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                  Workflow Name
                </th>
                <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <ForwardedIconComponent name="Brain" className="h-4 w-4" />
                    Model
                  </div>
                </th>
                <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <ForwardedIconComponent name="Activity" className="h-4 w-4" />
                    Status
                  </div>
                </th>
                <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <ForwardedIconComponent name="Clock" className="h-4 w-4" />
                    Last Edited
                  </div>
                </th>
                <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <ForwardedIconComponent name="Calendar" className="h-4 w-4" />
                    Schedule
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {recentWorkflows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-muted-foreground">
                    No workflows yet. Create your first workflow to get started.
                  </td>
                </tr>
              ) : (
                recentWorkflows.map((flow) => (
                  <tr key={flow.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {flow.icon && (
                          <span className="text-xl">{flow.icon}</span>
                        )}
                        <span className="font-medium">{flow.name}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <Badge variant="secondary" className="gap-1.5">
                        <ForwardedIconComponent name="Sparkles" className="h-3 w-3" />
                        {getModelFromFlow(flow)}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-green-500" />
                        <span className="text-sm">Active</span>
                      </div>
                    </td>
                    <td className="p-4 text-sm text-muted-foreground">
                      {formatDate(flow.updated_at)}
                    </td>
                    <td className="p-4">
                      {(() => {
                        const schedule = getScheduleForFlow(flow.id);
                        if (!schedule) {
                          return (
                            <Badge variant="outline" className="text-muted-foreground">
                              Not scheduled
                            </Badge>
                          );
                        }
                        return (
                          <div className="flex items-center gap-2">
                            <div className="flex flex-col gap-1">
                              <div className="flex items-center gap-2">
                                <Badge 
                                  variant={schedule.status === 'active' ? 'default' : 'secondary'}
                                  className="gap-1.5 cursor-pointer hover:opacity-80"
                                  onClick={() => handleEditSchedule(schedule)}
                                >
                                  <ForwardedIconComponent 
                                    name={schedule.status === 'active' ? 'Play' : 'Pause'} 
                                    className="h-3 w-3" 
                                  />
                                  {schedule.frequency} at {schedule.schedule_time}
                                </Badge>
                                {schedule.last_run_status && (
                                  <Badge 
                                    variant="outline" 
                                    className={`text-xs ${
                                      schedule.last_run_status === 'success' 
                                        ? 'text-green-600 border-green-600' 
                                        : schedule.last_run_status === 'failed'
                                        ? 'text-red-600 border-red-600'
                                        : 'text-muted-foreground'
                                    }`}
                                  >
                                    {schedule.last_run_status}
                                  </Badge>
                                )}
                              </div>
                              {schedule.last_run_at && (
                                <span className="text-xs text-muted-foreground">
                                  Last: {formatDate(schedule.last_run_at)}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-1">
                              {schedule.status === 'active' ? (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-8 w-8 p-0"
                                  onClick={() => handlePauseSchedule(schedule.id)}
                                  title="Pause schedule"
                                >
                                  <ForwardedIconComponent name="Pause" className="h-4 w-4" />
                                </Button>
                              ) : (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-8 w-8 p-0"
                                  onClick={() => handleResumeSchedule(schedule.id)}
                                  title="Resume schedule"
                                >
                                  <ForwardedIconComponent name="Play" className="h-4 w-4" />
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                                onClick={() => handleDeleteSchedule(schedule.id)}
                                title="Delete schedule"
                              >
                                <ForwardedIconComponent name="Trash2" className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        );
                      })()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Search and Pagination */}
        <div className="p-4 border-t flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2 flex-1 min-w-[200px]">
            <ForwardedIconComponent name="Search" className="h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search workflows..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-xs"
            />
          </div>
          
          {totalPages > 1 && (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                <ForwardedIconComponent name="ChevronLeft" className="h-4 w-4" />
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                <ForwardedIconComponent name="ChevronRight" className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Row - Charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Workflows by Status */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Workflows by status</h2>
          </div>
          <div className="flex items-center justify-center py-8">
            <div className="relative">
              {/* Donut Chart - Using SVG */}
              <svg width="200" height="200" viewBox="0 0 200 200">
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="30"
                />
                {agentsByStatus.total > 0 && (
                  <>
                    <circle
                      cx="100"
                      cy="100"
                      r="80"
                      fill="none"
                      stroke="#f87171"
                      strokeWidth="30"
                      strokeDasharray={`${(agentsByStatus.active / agentsByStatus.total) * 502.65} 502.65`}
                      strokeDashoffset="0"
                      transform="rotate(-90 100 100)"
                    />
                    <circle
                      cx="100"
                      cy="100"
                      r="80"
                      fill="none"
                      stroke="#fca5a5"
                      strokeWidth="30"
                      strokeDasharray={`${(agentsByStatus.idle / agentsByStatus.total) * 502.65} 502.65`}
                      strokeDashoffset={`-${(agentsByStatus.active / agentsByStatus.total) * 502.65}`}
                      transform="rotate(-90 100 100)"
                    />
                  </>
                )}
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <p className="text-4xl font-bold">{agentsByStatus.total}</p>
                <p className="text-sm text-muted-foreground">Workflows</p>
              </div>
            </div>
            <div className="ml-8 space-y-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-sm bg-[#f87171]" />
                <span className="text-sm">Active ({agentsByStatus.active})</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-sm bg-[#fca5a5]" />
                <span className="text-sm">Components ({agentsByStatus.idle})</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-sm bg-[#e5e7eb]" />
                <span className="text-sm">Offline ({agentsByStatus.offline})</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tasks Breakdown */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Tasks breakdown</h2>
            <select className="text-sm border rounded-md px-3 py-1.5 text-muted-foreground">
              <option>Past 7 days</option>
            </select>
          </div>
          <div className="h-64 flex items-end justify-between gap-2">
            {tasksBreakdown.map((day, index) => {
              const total = day.completed + day.pending + day.failed;
              const completedHeight = (day.completed / 25) * 100;
              const pendingHeight = (day.pending / 25) * 100;
              const failedHeight = (day.failed / 25) * 100;

              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-full flex flex-col-reverse" style={{ height: "200px" }}>
                    <div
                      className="w-full bg-[#f87171] rounded-t-sm"
                      style={{ height: `${completedHeight}%` }}
                    />
                    <div
                      className="w-full bg-[#fca5a5]"
                      style={{ height: `${pendingHeight}%` }}
                    />
                    <div
                      className="w-full bg-[#fecaca]"
                      style={{ height: `${failedHeight}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">{day.date}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
