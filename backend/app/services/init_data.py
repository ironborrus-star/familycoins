"""
Сервис для инициализации начальных данных
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import TaskTemplate


async def create_default_task_templates(db: AsyncSession):
    """Создать шаблоны заданий по умолчанию"""
    
    # Проверяем, есть ли уже шаблоны
    result = await db.execute(select(TaskTemplate).where(TaskTemplate.is_system_template == True))
    existing_templates = result.scalars().all()
    
    if existing_templates:
        return  # Шаблоны уже созданы
    
    default_templates = [
        # Домашние дела
        {
            "category": "household",
            "title": "Убрать свою комнату",
            "description": "Навести порядок в своей комнате: заправить кровать, убрать вещи",
            "default_reward_coins": 15
        },
        {
            "category": "household", 
            "title": "Помочь с посудой",
            "description": "Помыть посуду или загрузить/разгрузить посудомоечную машину",
            "default_reward_coins": 10
        },
        {
            "category": "household",
            "title": "Вынести мусор",
            "description": "Собрать и вынести мусор из дома",
            "default_reward_coins": 5
        },
        {
            "category": "household",
            "title": "Помочь с готовкой",
            "description": "Помочь готовить еду или накрыть на стол",
            "default_reward_coins": 15
        },
        {
            "category": "household",
            "title": "Пропылесосить",
            "description": "Пропылесосить комнату или общие зоны",
            "default_reward_coins": 20
        },
        
        # Экранное время
        {
            "category": "screen_time",
            "title": "Соблюдать экранное время",
            "description": "Не превышать лимит использования телефона/планшета",
            "default_reward_coins": 15
        },
        {
            "category": "screen_time",
            "title": "Выключить устройство за час до сна",
            "description": "Убрать все экраны за час до отхода ко сну",
            "default_reward_coins": 10
        },
        {
            "category": "screen_time",
            "title": "Делать перерывы каждый час",
            "description": "Делать 10-минутный перерыв каждый час использования экрана",
            "default_reward_coins": 5
        },
        
        # Активность
        {
            "category": "activity",
            "title": "Погулять на улице 30 минут",
            "description": "Провести не менее 30 минут на свежем воздухе",
            "default_reward_coins": 15
        },
        {
            "category": "activity",
            "title": "Сделать зарядку",
            "description": "Выполнить утреннюю зарядку или физические упражнения",
            "default_reward_coins": 10
        },
        {
            "category": "activity",
            "title": "Поиграть в активную игру",
            "description": "Поиграть в футбол, баскетбол или другую активную игру",
            "default_reward_coins": 20
        },
        {
            "category": "activity",
            "title": "Прогулка с семьей",
            "description": "Совместная прогулка или активность с семьей",
            "default_reward_coins": 25
        }
    ]
    
    # Создаем шаблоны
    for template_data in default_templates:
        template = TaskTemplate(**template_data)
        db.add(template)
    
    await db.commit()