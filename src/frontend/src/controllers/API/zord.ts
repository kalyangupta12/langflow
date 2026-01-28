/**
 * API client for Zord AI endpoints
 */

const ZORD_BASE_URL = "/api/v1/zord";

export interface ZordAnalyzeRequest {
  prompt: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ZordMCQOption {
  id: string;
  question: string;
  options: Array<{ id: string; label: string; value: string }>;
}

export interface ZordAnalyzeResponse {
  mcqs: ZordMCQOption[];
  message: string;
}

export interface ZordPlanRequest {
  prompt: string;
  answers: Record<string, string>;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ZordPlanStep {
  id: string;
  description: string;
  component?: string;
}

export interface ZordPlan {
  id: string;
  title: string;
  steps: ZordPlanStep[];
  data_flow: string;
}

export interface ZordPlanResponse {
  plan: ZordPlan;
  message: string;
}

export interface ZordGenerateRequest {
  plan: ZordPlan;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ZordGenerateResponse {
  json: any;
  message: string;
}

export interface ZordCreateFlowRequest {
  flow_json: any;
  folder_id?: string;
}

export interface ZordCreateFlowResponse {
  flow_id: string;
  name: string;
  message: string;
}

/**
 * Analyze user intent and generate MCQs
 */
export async function analyzeIntent(
  request: ZordAnalyzeRequest
): Promise<ZordAnalyzeResponse> {
  const response = await fetch(`${ZORD_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to analyze intent");
  }

  return response.json();
}

/**
 * Generate workflow plan from MCQ answers
 */
export async function generatePlan(
  request: ZordPlanRequest
): Promise<ZordPlanResponse> {
  const response = await fetch(`${ZORD_BASE_URL}/plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to generate plan");
  }

  return response.json();
}

/**
 * Generate Langflow JSON from plan
 */
export async function generateJSON(
  request: ZordGenerateRequest
): Promise<ZordGenerateResponse> {
  const response = await fetch(`${ZORD_BASE_URL}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to generate JSON");
  }

  return response.json();
}

/**
 * Create a flow directly in user's account
 */
export async function createFlow(
  request: ZordCreateFlowRequest
): Promise<ZordCreateFlowResponse> {
  const response = await fetch(`${ZORD_BASE_URL}/create-flow`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create flow");
  }

  return response.json();
}
