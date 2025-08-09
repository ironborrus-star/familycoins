"""
Сервис для работы с заданиями
"""
import uuid
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Task, TaskTemplate, TaskAssignment, User
from app.schemas.task import TaskCreate, TaskAssignmentComplete, TaskAssignmentApprove
from app.services.coin_service import CoinService


class TaskService:
    
    @staticmethod
    async def get_task_templates(db: AsyncSession) -> List[TaskTemplate]:
        """Получить все шаблоны заданий"""
        result = await db.execute(select(TaskTemplate).where(TaskTemplate.is_system_template == True))
        return list(result.scalars().all())
    
    @staticmethod
    async def create_task(
        task_data: TaskCreate,
        creator_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Tuple[Task, List[TaskAssignment]]:
        """Создать новое задание"""
        
        # Проверяем, что все назначаемые пользователи - дети из той же семьи
        result = await db.execute(
            select(User).where(
                and_(
                    User.id.in_(task_data.assigned_to),
                    User.family_id == family_id,
                    User.role == "child"
                )
            )
        )
        children = result.scalars().all()
        
        if len(children) != len(task_data.assigned_to):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some assigned users are not children in this family"
            )
        
        # Получаем данные из шаблона если указан template_id
        title = task_data.title
        description = task_data.description
        category = task_data.category
        reward_coins = task_data.reward_coins
        
        if task_data.template_id:
            result = await db.execute(
                select(TaskTemplate).where(TaskTemplate.id == task_data.template_id)
            )
            template = result.scalar_one_or_none()
            if template:
                title = title or template.title
                description = description or template.description
                category = category or template.category
                reward_coins = reward_coins or template.default_reward_coins
        
        # Создаем задание
        task = Task(
            family_id=family_id,
            template_id=task_data.template_id,
            title=title,
            description=description,
            category=category,
            reward_coins=reward_coins,
            created_by=creator_id
        )
        db.add(task)
        await db.flush()  # Получаем ID задания
        
        # Создаем назначения для каждого ребенка
        assignments = []
        for child_id in task_data.assigned_to:
            assignment = TaskAssignment(
                task_id=task.id,
                child_id=child_id,
                due_date=task_data.due_date
            )
            db.add(assignment)
            assignments.append(assignment)
        
        await db.commit()
        await db.refresh(task)
        
        # Обновляем assignments с именами детей
        for assignment in assignments:
            await db.refresh(assignment)
        
        return task, assignments
    
    @staticmethod
    async def get_child_tasks(child_id: uuid.UUID, db: AsyncSession) -> List[TaskAssignment]:
        """Получить задания ребенка"""
        result = await db.execute(
            select(TaskAssignment)
            .options(selectinload(TaskAssignment.task))
            .where(TaskAssignment.child_id == child_id)
            .where(TaskAssignment.status.in_(["assigned", "completed"]))
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_parent_tasks(parent_id: uuid.UUID, family_id: uuid.UUID, db: AsyncSession) -> Tuple[List[Task], List[dict]]:
        """Получить задания родителя"""
        
        # Созданные задания
        result = await db.execute(
            select(Task)
            .where(and_(
                Task.created_by == parent_id,
                Task.status == "active"
            ))
        )
        created_tasks = list(result.scalars().all())
        
        # Задания, ожидающие подтверждения
        result = await db.execute(
            select(TaskAssignment)
            .options(
                selectinload(TaskAssignment.task),
                selectinload(TaskAssignment.child)
            )
            .join(Task)
            .where(and_(
                Task.family_id == family_id,
                TaskAssignment.status == "completed"
            ))
        )
        
        pending_assignments = result.scalars().all()
        pending_approvals = []
        
        for assignment in pending_assignments:
            pending_approvals.append({
                "assignment_id": assignment.id,
                "task_title": assignment.task.title,
                "child_name": assignment.child.name,
                "completed_at": assignment.completed_at,
                "proof_text": assignment.proof_text,
                "proof_image_url": assignment.proof_image_url
            })
        
        return created_tasks, pending_approvals
    
    @staticmethod
    async def complete_task(
        assignment_id: uuid.UUID,
        completion_data: TaskAssignmentComplete,
        child_id: uuid.UUID,
        db: AsyncSession
    ) -> TaskAssignment:
        """Отметить задание как выполненное"""
        
        # Получаем назначение
        result = await db.execute(
            select(TaskAssignment)
            .options(selectinload(TaskAssignment.task))
            .where(and_(
                TaskAssignment.id == assignment_id,
                TaskAssignment.child_id == child_id,
                TaskAssignment.status == "assigned"
            ))
        )
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task assignment not found or already completed"
            )
        
        # Обновляем статус
        assignment.status = "completed"
        assignment.completed_at = datetime.utcnow()
        assignment.proof_text = completion_data.proof_text
        assignment.proof_image_url = completion_data.proof_image_url
        
        await db.commit()
        await db.refresh(assignment)
        
        return assignment
    
    @staticmethod
    async def approve_task(
        assignment_id: uuid.UUID,
        approval_data: TaskAssignmentApprove,
        approver_id: uuid.UUID,
        db: AsyncSession
    ) -> Tuple[TaskAssignment, int]:
        """Одобрить или отклонить выполнение задания"""
        
        # Получаем назначение
        result = await db.execute(
            select(TaskAssignment)
            .options(selectinload(TaskAssignment.task))
            .where(and_(
                TaskAssignment.id == assignment_id,
                TaskAssignment.status == "completed"
            ))
        )
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task assignment not found or not ready for approval"
            )
        
        if approval_data.approved:
            # Одобряем и начисляем коины
            assignment.status = "approved"
            assignment.approved_at = datetime.utcnow()
            assignment.approved_by = approver_id
            assignment.coins_earned = assignment.task.reward_coins
            
            # Начисляем коины ребенку
            _, new_balance = await CoinService.add_coins(
                user_id=assignment.child_id,
                amount=assignment.task.reward_coins,
                description=f"Выполнение задания: {assignment.task.title}",
                transaction_type="earned",
                reference_id=assignment.id,
                reference_type="task",
                db=db
            )
        else:
            # Отклоняем
            assignment.status = "rejected"
            assignment.approved_at = datetime.utcnow()
            assignment.approved_by = approver_id
            new_balance = 0  # Не начисляем коины
        
        await db.commit()
        await db.refresh(assignment)
        
        # Обновляем прогресс целей при одобрении задания
        if approval_data.approved:
            try:
                from app.services.goal_service import GoalService
                await GoalService.update_goal_progress_on_task_completion(
                    child_id=assignment.child_id,
                    task_assignment_id=assignment.id,
                    db=db
                )
            except ImportError:
                # Игнорируем если модуль целей недоступен
                pass
            except Exception:
                # Не прерываем основную операцию при ошибке обновления целей
                pass
        
        return assignment, new_balance
    
    @staticmethod
    async def get_parent_task_statistics(parent_id: uuid.UUID, family_id: uuid.UUID, db: AsyncSession) -> dict:
        """Получить статистику заданий для родителя"""
        
        # Получаем все назначения заданий, созданных родителем
        result = await db.execute(
            select(TaskAssignment)
            .options(
                selectinload(TaskAssignment.task),
                selectinload(TaskAssignment.child)
            )
            .join(Task)
            .where(and_(
                Task.created_by == parent_id,
                Task.status == "active"
            ))
        )
        assignments = result.scalars().all()
        
        # Подсчитываем статистику по статусам
        stats = {
            "total_tasks": len(assignments),
            "in_progress": len([a for a in assignments if a.status == "assigned"]),
            "pending_approval": len([a for a in assignments if a.status == "completed"]),
            "completed": len([a for a in assignments if a.status in ["approved", "rejected"]]),
            "approved": len([a for a in assignments if a.status == "approved"]),
            "rejected": len([a for a in assignments if a.status == "rejected"])
        }
        
        # Статистика по детям
        children_stats = {}
        for assignment in assignments:
            child_id = str(assignment.child_id)
            child_name = assignment.child.name
            
            if child_id not in children_stats:
                children_stats[child_id] = {
                    "child_name": child_name,
                    "total": 0,
                    "assigned": 0,
                    "completed": 0,
                    "approved": 0,
                    "rejected": 0
                }
            
            children_stats[child_id]["total"] += 1
            if assignment.status == "assigned":
                children_stats[child_id]["assigned"] += 1
            elif assignment.status == "completed":
                children_stats[child_id]["completed"] += 1
            elif assignment.status == "approved":
                children_stats[child_id]["approved"] += 1
            elif assignment.status == "rejected":
                children_stats[child_id]["rejected"] += 1
        
        stats["children"] = list(children_stats.values())
        return stats
    
    @staticmethod
    async def get_parent_task_history(
        parent_id: uuid.UUID, 
        family_id: uuid.UUID, 
        db: AsyncSession,
        status_filter: Optional[str] = None,
        child_filter: Optional[str] = None,
        period_filter: Optional[str] = None
    ) -> List[dict]:
        """Получить историю заданий для родителя с фильтрами"""
        
        # Базовый запрос
        query = (
            select(TaskAssignment)
            .options(
                selectinload(TaskAssignment.task),
                selectinload(TaskAssignment.child)
            )
            .join(Task)
            .where(and_(
                Task.created_by == parent_id,
                Task.status == "active"
            ))
        )
        
        # Применяем фильтры
        if status_filter and status_filter != "all":
            query = query.where(TaskAssignment.status == status_filter)
        
        if child_filter and child_filter != "all":
            query = query.where(TaskAssignment.child_id == child_filter)
        
        if period_filter and period_filter != "all":
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            if period_filter == "week":
                start_date = now - timedelta(days=7)
            elif period_filter == "month":
                start_date = now - timedelta(days=30)
            else:
                start_date = None
                
            if start_date:
                query = query.where(TaskAssignment.created_at >= start_date)
        
        # Сортировка по дате создания (новые сверху)
        query = query.order_by(TaskAssignment.created_at.desc())
        
        result = await db.execute(query)
        assignments = result.scalars().all()
        
        # Формируем результат
        history = []
        for assignment in assignments:
            history.append({
                "assignment_id": assignment.id,
                "task_id": assignment.task_id,
                "task_title": assignment.task.title,
                "task_description": assignment.task.description,
                "child_id": assignment.child_id,
                "child_name": assignment.child.name,
                "status": assignment.status,
                "reward_coins": assignment.task.reward_coins,
                "coins_earned": assignment.coins_earned,
                "due_date": assignment.due_date,
                "created_at": assignment.created_at,
                "completed_at": assignment.completed_at,
                "approved_at": assignment.approved_at,
                "proof_text": assignment.proof_text,
                "proof_image_url": assignment.proof_image_url
            })
        
        return history