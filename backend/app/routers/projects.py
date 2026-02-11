"""Project CRUD routes."""

import os
import shutil

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.db.mongodb import get_db
from app.dependencies import get_current_user
from app.models.project import create_project_doc
from app.schemas.project import (
    AIConfigUpdate,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter()


def _project_to_response(doc: dict) -> ProjectResponse:
    """Convert a MongoDB project document to a response schema."""
    return ProjectResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        slug=doc["slug"],
        description=doc["description"],
        owner_id=doc["owner_id"],
        status=doc["status"],
        ai_config=doc["ai_config"],
        git=doc["git"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List all projects for the current user."""
    cursor = db.projects.find({"owner_id": user["_id"]}).sort("created_at", -1)
    projects = await cursor.to_list(length=100)
    return ProjectListResponse(
        projects=[_project_to_response(p) for p in projects],
        total=len(projects),
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Create a new project."""
    doc = create_project_doc(
        name=request.name,
        description=request.description,
        owner_id=user["_id"],
    )

    # Check slug uniqueness
    existing = await db.projects.find_one({"slug": doc["slug"]})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A project with slug '{doc['slug']}' already exists",
        )

    result = await db.projects.insert_one(doc)
    project_id = str(result.inserted_id)

    # Create project directories on disk
    project_dir = os.path.join(settings.projects_data_dir, project_id)
    os.makedirs(os.path.join(project_dir, "staging"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "prod"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, ".home", ".claude"), exist_ok=True)

    doc["_id"] = result.inserted_id
    return _project_to_response(doc)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get a project by ID."""
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Update a project."""
    update_data = request.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    from datetime import datetime, timezone

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await db.projects.update_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    return _project_to_response(project)


@router.patch("/{project_id}/ai-config", response_model=ProjectResponse)
async def update_ai_config(
    project_id: str,
    request: AIConfigUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Update a project's AI configuration."""
    update_fields = {}
    for key, value in request.model_dump(exclude_none=True).items():
        update_fields[f"ai_config.{key}"] = value

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    from datetime import datetime, timezone

    update_fields["updated_at"] = datetime.now(timezone.utc)

    result = await db.projects.update_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    return _project_to_response(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Delete a project and its data."""
    result = await db.projects.delete_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")

    # Clean up related data
    await db.environments.delete_many({"project_id": project_id})
    await db.chat_sessions.delete_many({"project_id": project_id})
    await db.chat_messages.delete_many({"project_id": project_id})
    await db.deploys.delete_many({"project_id": project_id})
    await db.tasks.delete_many({"project_id": project_id})

    # Remove project directory
    project_dir = os.path.join(settings.projects_data_dir, project_id)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
