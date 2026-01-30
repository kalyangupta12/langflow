"""Zord AI - Intelligent Workflow Architect API."""

from __future__ import annotations

import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.flow.model import Flow, FlowCreate
from langflow.services.database.models.folder.constants import DEFAULT_FOLDER_NAME
from langflow.services.database.models.folder.model import Folder
from langflow.services.deps import get_storage_service, get_settings_service, get_telemetry_service
from langflow.services.storage.service import StorageService
from langflow.services.zord.service import ZordAIService

router = APIRouter(prefix="/zord", tags=["Zord AI"])


class ZordAnalyzeRequest(BaseModel):
    """Request to analyze user intent and generate MCQs."""

    prompt: str
    conversation_history: list[dict] = []


class ZordMCQ(BaseModel):
    """Multiple choice question model."""

    id: str
    question: str
    options: list[dict]


class ZordAnalyzeResponse(BaseModel):
    """Response containing MCQs."""

    mcqs: list[ZordMCQ]
    message: str


class ZordPlanRequest(BaseModel):
    """Request to generate workflow plan."""

    prompt: str
    answers: dict[str, str]
    conversation_history: list[dict] = []


class ZordPlanStep(BaseModel):
    """Workflow plan step."""

    id: str
    description: str
    component: str | None = None


class ZordPlan(BaseModel):
    """Workflow plan model."""

    id: str
    title: str
    steps: list[ZordPlanStep]
    data_flow: str


class ZordPlanResponse(BaseModel):
    """Response containing workflow plan."""

    plan: ZordPlan
    message: str


class ZordGenerateRequest(BaseModel):
    """Request to generate Langflow JSON."""

    plan: ZordPlan
    conversation_history: list[dict] = []


class ZordGenerateResponse(BaseModel):
    """Response containing generated JSON."""

    json: dict
    message: str


class ZordModifyRequest(BaseModel):
    """Request to modify existing plan."""

    plan: ZordPlan
    modification_request: str
    conversation_history: list[dict] = []


class ZordCreateFlowRequest(BaseModel):
    """Request to create flow from Zord JSON."""

    flow_json: dict = Field(..., description="Langflow JSON workflow to create")
    folder_id: UUID | None = Field(None, description="Folder ID to create flow in")


class ZordCreateFlowResponse(BaseModel):
    """Response from flow creation."""

    flow_id: UUID = Field(..., description="ID of created flow")
    name: str = Field(..., description="Name of created flow")
    message: str = Field(..., description="Success message")


@router.post("/analyze", response_model=ZordAnalyzeResponse)
async def analyze_user_intent(
    request: ZordAnalyzeRequest,
    current_user: CurrentActiveUser,
    settings_service: Annotated["SettingsService", Depends(get_settings_service)],
    telemetry_service: Annotated["TelemetryService", Depends(get_telemetry_service)],
) -> ZordAnalyzeResponse:
    """Analyze user intent and generate clarifying MCQs.

    This endpoint takes a user's workflow description and generates
    multiple choice questions to clarify technical details.

    Args:
        request: User prompt and conversation history
        current_user: Authenticated user
        settings_service: Settings service for component loading
        telemetry_service: Telemetry service

    Returns:
        MCQs for technical clarification

    Raises:
        HTTPException: If analysis fails
    """
    try:
        service = ZordAIService(
            settings_service=settings_service,
            telemetry_service=telemetry_service
        )
        result = await service.analyze_intent(
            prompt=request.prompt,
            conversation_history=request.conversation_history,
        )
        return ZordAnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze intent: {str(e)}",
        ) from e


@router.post("/plan", response_model=ZordPlanResponse)
async def generate_workflow_plan(
    request: ZordPlanRequest,
    current_user: CurrentActiveUser,
    settings_service: Annotated["SettingsService", Depends(get_settings_service)],
    telemetry_service: Annotated["TelemetryService", Depends(get_telemetry_service)],
) -> ZordPlanResponse:
    """Generate a detailed workflow plan based on user answers.

    Args:
        request: User prompt, MCQ answers, and conversation history
        current_user: Authenticated user
        settings_service: Settings service for component loading
        telemetry_service: Telemetry service

    Returns:
        Detailed workflow plan

    Raises:
        HTTPException: If plan generation fails
    """
    try:
        service = ZordAIService(
            settings_service=settings_service,
            telemetry_service=telemetry_service
        )
        result = await service.generate_plan(
            prompt=request.prompt,
            answers=request.answers,
            conversation_history=request.conversation_history,
        )
        return ZordPlanResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}",
        ) from e


@router.post("/generate", response_model=ZordGenerateResponse)
async def generate_workflow_json(
    request: ZordGenerateRequest,
    current_user: CurrentActiveUser,
    settings_service: Annotated["SettingsService", Depends(get_settings_service)],
    telemetry_service: Annotated["TelemetryService", Depends(get_telemetry_service)],
) -> ZordGenerateResponse:
    """Generate Langflow JSON from workflow plan.

    Args:
        request: Workflow plan and conversation history
        current_user: Authenticated user
        settings_service: Settings service for component loading
        telemetry_service: Telemetry service

    Returns:
        Generated Langflow JSON

    Raises:
        HTTPException: If JSON generation fails
    """
    try:
        service = ZordAIService(
            settings_service=settings_service,
            telemetry_service=telemetry_service
        )
        result = await service.generate_json(
            plan=request.plan,
            conversation_history=request.conversation_history,
        )
        return ZordGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate JSON: {str(e)}",
        ) from e


@router.post("/modify", response_model=ZordPlanResponse)
async def modify_workflow_plan(
    request: ZordModifyRequest,
    current_user: CurrentActiveUser,
    settings_service: Annotated["SettingsService", Depends(get_settings_service)],
    telemetry_service: Annotated["TelemetryService", Depends(get_telemetry_service)],
) -> ZordPlanResponse:
    """Modify an existing workflow plan.

    Args:
        request: Current plan, modification request, and conversation history
        current_user: Authenticated user
        settings_service: Settings service for component loading
        telemetry_service: Telemetry service

    Returns:
        Modified workflow plan

    Raises:
        HTTPException: If modification fails
    """
    try:
        service = ZordAIService(
            settings_service=settings_service,
            telemetry_service=telemetry_service
        )
        result = await service.modify_plan(
            plan=request.plan,
            modification_request=request.modification_request,
            conversation_history=request.conversation_history,
        )
        return ZordPlanResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to modify plan: {str(e)}",
        ) from e


@router.post("/create-flow", response_model=ZordCreateFlowResponse, status_code=201)
async def create_flow_from_zord(
    *,
    session: DbSession,
    request: ZordCreateFlowRequest,
    current_user: CurrentActiveUser,
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> ZordCreateFlowResponse:
    """Create a new flow from Zord-generated JSON.

    Args:
        session: Database session
        request: Flow JSON and optional folder ID
        current_user: Authenticated user
        storage_service: Storage service for saving flow files

    Returns:
        Created flow information

    Raises:
        HTTPException: If flow creation fails
    """
    try:
        flow_json = request.flow_json

        # Extract flow metadata
        flow_name = flow_json.get("name", f"Zord Flow {flow_json.get('id', 'untitled')[:8]}")
        flow_description = flow_json.get("description", "Generated by Zord AI")
        flow_data = flow_json.get("data", {})

        # Determine folder_id
        folder_id = request.folder_id
        if not folder_id:
            # Get default folder for user
            statement = select(Folder).where(
                Folder.name == DEFAULT_FOLDER_NAME,
                Folder.user_id == current_user.id,
            )
            result = await session.exec(statement)
            default_folder = result.first()
            if default_folder:
                folder_id = default_folder.id

        # Create flow using FlowCreate model
        flow_create = FlowCreate(
            name=flow_name,
            description=flow_description,
            data=flow_data,
            folder_id=folder_id,
        )

        # Create new flow in database
        db_flow = Flow.model_validate(flow_create, from_attributes=True)
        db_flow.user_id = current_user.id
        session.add(db_flow)
        await session.commit()
        await session.refresh(db_flow)

        # Save to filesystem
        base_dir = storage_service.data_dir / "flows" / str(current_user.id)
        await base_dir.mkdir(parents=True, exist_ok=True)

        flow_path = base_dir / f"{db_flow.id}.json"
        flow_dict = db_flow.model_dump(mode="json")

        async with await flow_path.open("w", encoding="utf-8") as f:
            await f.write(json.dumps(flow_dict, indent=2))

        return ZordCreateFlowResponse(
            flow_id=db_flow.id,
            name=db_flow.name,
            message=f"Flow '{db_flow.name}' created successfully! You can find it in your flows list.",
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create flow: {str(e)}",
        ) from e
