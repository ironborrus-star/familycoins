"""
Сервис для статистики
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.models import User, Task, TaskAssignment, CoinTransaction


class StatsService:
    
    @staticmethod
    async def get_family_stats(
        family_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: AsyncSession = None
    ) -> Dict:
        """Получить статистику по семье (для родителей)"""
        
        # Устанавливаем период по умолчанию (текущий месяц)
        if not start_date:
            start_date = date.today().replace(day=1)
        if not end_date:
            end_date = date.today()
        
        # Получаем всех детей в семье
        result = await db.execute(
            select(User).where(and_(
                User.family_id == family_id,
                User.role == "child"
            ))
        )
        children = result.scalars().all()
        
        # Получаем задания семьи в указанном периоде
        result = await db.execute(
            select(TaskAssignment)
            .join(Task)
            .where(and_(
                Task.family_id == family_id,
                TaskAssignment.created_at.between(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            ))
        )
        assignments = result.scalars().all()
        
        # Подсчитываем общую статистику
        total_assigned = len(assignments)
        total_completed = len([a for a in assignments if a.status in ["approved", "completed"]])
        completion_rate = (total_completed / total_assigned * 100) if total_assigned > 0 else 0
        
        # Подсчитываем коины
        result = await db.execute(
            select(func.sum(CoinTransaction.amount)).where(and_(
                CoinTransaction.user_id.in_([child.id for child in children]),
                CoinTransaction.transaction_type == "earned",
                CoinTransaction.created_at.between(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            ))
        )
        total_coins_earned = result.scalar() or 0
        
        result = await db.execute(
            select(func.sum(-CoinTransaction.amount)).where(and_(
                CoinTransaction.user_id.in_([child.id for child in children]),
                CoinTransaction.transaction_type == "spent",
                CoinTransaction.created_at.between(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            ))
        )
        total_coins_spent = result.scalar() or 0
        
        # Статистика по детям
        children_stats = []
        for child in children:
            child_assignments = [a for a in assignments if a.child_id == child.id]
            child_completed = len([a for a in child_assignments if a.status in ["approved", "completed"]])
            child_completion_rate = (child_completed / len(child_assignments) * 100) if child_assignments else 0
            
            # Коины ребенка
            result = await db.execute(
                select(func.sum(CoinTransaction.amount)).where(and_(
                    CoinTransaction.user_id == child.id,
                    CoinTransaction.transaction_type == "earned",
                    CoinTransaction.created_at.between(
                        datetime.combine(start_date, datetime.min.time()),
                        datetime.combine(end_date, datetime.max.time())
                    )
                ))
            )
            child_coins_earned = result.scalar() or 0
            
            result = await db.execute(
                select(func.sum(-CoinTransaction.amount)).where(and_(
                    CoinTransaction.user_id == child.id,
                    CoinTransaction.transaction_type == "spent",
                    CoinTransaction.created_at.between(
                        datetime.combine(start_date, datetime.min.time()),
                        datetime.combine(end_date, datetime.max.time())
                    )
                ))
            )
            child_coins_spent = result.scalar() or 0
            
            children_stats.append({
                "child_id": child.id,
                "child_name": child.name,
                "tasks_completed": child_completed,
                "coins_earned": child_coins_earned,
                "coins_spent": child_coins_spent,
                "completion_rate": round(child_completion_rate, 1)
            })
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_tasks_assigned": total_assigned,
                "total_tasks_completed": total_completed,
                "completion_rate": round(completion_rate, 1),
                "total_coins_earned": total_coins_earned,
                "total_coins_spent": total_coins_spent,
                "active_children": len(children)
            },
            "children_stats": children_stats,
            "daily_activity": []  # Можно добавить позже
        }
    
    @staticmethod
    async def get_child_stats(child_id: uuid.UUID, db: AsyncSession) -> Dict:
        """Получить статистику ребенка"""
        
        # Текущий месяц
        start_date = date.today().replace(day=1)
        end_date = date.today()
        
        # Задания за месяц
        result = await db.execute(
            select(TaskAssignment).where(and_(
                TaskAssignment.child_id == child_id,
                TaskAssignment.created_at.between(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            ))
        )
        assignments = list(result.scalars().all())
        
        completed_count = len([a for a in assignments if a.status == "approved"])
        completion_rate = (completed_count / len(assignments) * 100) if assignments else 0
        
        # Коины за месяц
        result = await db.execute(
            select(func.sum(CoinTransaction.amount)).where(and_(
                CoinTransaction.user_id == child_id,
                CoinTransaction.transaction_type == "earned",
                CoinTransaction.created_at.between(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            ))
        )
        coins_earned = result.scalar() or 0
        
        result = await db.execute(
            select(func.sum(-CoinTransaction.amount)).where(and_(
                CoinTransaction.user_id == child_id,
                CoinTransaction.transaction_type == "spent",
                CoinTransaction.created_at.between(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            ))
        )
        coins_spent = result.scalar() or 0
        
        # Простые достижения
        achievements = []
        if completed_count >= 1:
            achievements.append({
                "title": "Первое задание",
                "description": "Выполнил первое задание",
                "earned_at": assignments[0].approved_at if assignments else None
            })
        
        if completed_count >= 7:
            achievements.append({
                "title": "Неделя без пропусков",
                "description": "Выполнял задания каждый день недели",
                "earned_at": datetime.now()
            })
        
        return {
            "current_month": {
                "tasks_completed": completed_count,
                "coins_earned": coins_earned,
                "coins_spent": coins_spent,
                "completion_rate": round(completion_rate, 1)
            },
            "achievements": achievements
        }