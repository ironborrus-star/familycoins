"""
Pydantic схемы для заданий
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskTemplateBase(BaseModel):
    category: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    default_reward_coins: int = Field(10, ge=1)


class TaskTemplate(TaskTemplateBase):
    id: uuid.UUID
    is_system_template: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    reward_coins: int = Field(10, ge=1)


class TaskCreate(BaseModel):
    template_id: Optional[uuid.UUID] = None
    assigned_to: List[uuid.UUID] = Field(..., min_items=1)
    due_date: Optional[date] = None
    # Поля опциональны, если используется template_id
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    reward_coins: Optional[int] = Field(None, ge=1)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    reward_coins: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None, pattern="^(active|paused|archived)$")


class Task(TaskBase):
    id: uuid.UUID
    family_id: uuid.UUID
    template_id: Optional[uuid.UUID]
    status: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskAssignmentBase(BaseModel):
    due_date: Optional[date] = None


class TaskAssignmentCreate(TaskAssignmentBase):
    task_id: uuid.UUID
    child_id: uuid.UUID


class TaskAssignmentComplete(BaseModel):
    proof_text: Optional[str] = None
    proof_image_url: Optional[str] = Field(None, max_length=255)


class TaskAssignmentApprove(BaseModel):
    approved: bool
    feedback: Optional[str] = None


class TaskAssignment(TaskAssignmentBase):
    id: uuid.UUID
    task_id: uuid.UUID
    child_id: uuid.UUID
    status: str
    completed_at: Optional[datetime]
    approved_at: Optional[datetime]
    approved_by: Optional[uuid.UUID]
    proof_text: Optional[str]
    proof_image_url: Optional[str]
    coins_earned: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskAssignmentWithTask(TaskAssignment):
    task: Task


class TaskAssignmentWithChild(TaskAssignment):
    child_name: str


class TaskWithAssignments(Task):
    assignments: List[TaskAssignmentWithChild] = []


class TaskCreateResponse(BaseModel):
    task: Task
    assignments: List[TaskAssignmentWithChild]


class MyTasksChildResponse(BaseModel):
    assignments: List[TaskAssignmentWithTask]


class MyTasksParentResponse(BaseModel):
    created_tasks: List[Task]
    pending_approvals: List[dict]  # Будет содержать детализированную информацию


class TaskTemplatesResponse(BaseModel):
    templates: List[TaskTemplate]