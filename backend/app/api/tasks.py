"""
API для работы с заданиями
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_session
from app.schemas.task import (
    TaskTemplatesResponse, TaskCreate, TaskCreateResponse,
    MyTasksChildResponse, MyTasksParentResponse,
    TaskAssignmentComplete, TaskAssignmentApprove
)
from app.services.task_service import TaskService
from app.utils.permissions import get_current_user, require_parent, require_child
from app.models import User

router = APIRouter()


@router.get("/templates", response_model=TaskTemplatesResponse)
async def get_task_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить шаблоны заданий"""
    templates = await TaskService.get_task_templates(db)
    
    return TaskTemplatesResponse(templates=templates)


@router.post("", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Создать задание (только родители)"""
    task, assignments = await TaskService.create_task(
        task_data=task_data,
        creator_id=current_user.id,
        family_id=current_user.family_id,
        db=db
    )
    
    # Формируем ответ с именами детей
    assignments_with_names = []
    for assignment in assignments:
        # Получаем имя ребенка
        result = await db.execute(
            select(User).where(User.id == assignment.child_id)
        )
        child = result.scalar_one()
        
        # Создаем словарь с данными assignment + child_name
        assignment_dict = {
            'id': assignment.id,
            'task_id': assignment.task_id,
            'child_id': assignment.child_id,
            'status': assignment.status,
            'due_date': assignment.due_date,
            'completed_at': assignment.completed_at,
            'approved_at': assignment.approved_at,
            'approved_by': assignment.approved_by,
            'proof_text': assignment.proof_text,
            'proof_image_url': assignment.proof_image_url,
            'coins_earned': assignment.coins_earned,
            'created_at': assignment.created_at,
            'updated_at': assignment.updated_at,
            'child_name': child.name
        }
        
        assignments_with_names.append(assignment_dict)
    
    return TaskCreateResponse(
        task=task,
        assignments=assignments_with_names
    )


@router.get("/my")
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить задания текущего пользователя"""
    
    if current_user.role == "child":
        # Для детей - их назначенные задания
        assignments = await TaskService.get_child_tasks(current_user.id, db)
        return MyTasksChildResponse(assignments=assignments)
    
    elif current_user.role == "parent":
        # Для родителей - созданные задания и ожидающие подтверждения
        created_tasks, pending_approvals = await TaskService.get_parent_tasks(
            parent_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        return MyTasksParentResponse(
            created_tasks=created_tasks,
            pending_approvals=pending_approvals
        )


@router.put("/assignments/{assignment_id}/complete")
async def complete_task(
    assignment_id: uuid.UUID = Path(...),
    completion_data: TaskAssignmentComplete = ...,
    current_user: User = Depends(require_child),
    db: AsyncSession = Depends(get_async_session)
):
    """Отметить задание как выполненное (дети)"""
    assignment = await TaskService.complete_task(
        assignment_id=assignment_id,
        completion_data=completion_data,
        child_id=current_user.id,
        db=db
    )
    
    return {
        "assignment": {
            "id": assignment.id,
            "status": assignment.status,
            "completed_at": assignment.completed_at,
            "proof_text": assignment.proof_text
        }
    }


@router.put("/assignments/{assignment_id}/approve")
async def approve_task(
    assignment_id: uuid.UUID = Path(...),
    approval_data: TaskAssignmentApprove = ...,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Одобрить выполнение задания (родители)"""
    assignment, new_balance = await TaskService.approve_task(
        assignment_id=assignment_id,
        approval_data=approval_data,
        approver_id=current_user.id,
        db=db
    )
    
    response = {
        "assignment": {
            "id": assignment.id,
            "status": assignment.status,
            "approved_at": assignment.approved_at,
            "coins_earned": assignment.coins_earned
        }
    }
    
    if approval_data.approved:
        response["new_balance"] = new_balance
    
    return response


@router.get("/statistics")
async def get_task_statistics(
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить статистику заданий для родителя"""
    stats = await TaskService.get_parent_task_statistics(
        parent_id=current_user.id,
        family_id=current_user.family_id,
        db=db
    )
    
    return stats


@router.get("/history")
async def get_task_history(
    status_filter: str = None,
    child_filter: str = None,
    period_filter: str = None,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить историю заданий для родителя с фильтрами"""
    history = await TaskService.get_parent_task_history(
        parent_id=current_user.id,
        family_id=current_user.family_id,
        db=db,
        status_filter=status_filter,
        child_filter=child_filter,
        period_filter=period_filter
    )
    
    return {"history": history}