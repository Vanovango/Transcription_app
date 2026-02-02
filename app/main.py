from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# Создаем экземпляр приложения
app = FastAPI(title="TODO App", description="Простое приложение для управления задачами")

# Подключаем статические файлы (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем шаблоны HTML
templates = Jinja2Templates(directory="templates")

# Модель данных для задачи
class TodoItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: str
    priority: int = 1  # 1 - низкий, 2 - средний, 3 - высокий

# "База данных" в памяти
todo_db: List[TodoItem] = []

# Корневой маршрут - отображает все задачи
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Сортируем задачи по приоритету и статусу выполнения
    sorted_todos = sorted(todo_db, key=lambda x: (x.completed, -x.priority))
    return templates.TemplateResponse("index.html", {"request": request, "todos": sorted_todos})

# Маршрут для добавления новой задачи
@app.post("/add")
async def add_todo(
    title: str = Form(...),
    description: str = Form(None),
    priority: int = Form(1)
):
    # Создаем новую задачу
    new_todo = TodoItem(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        priority=priority,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    
    # Добавляем в "базу данных"
    todo_db.append(new_todo)
    
    # Перенаправляем на главную страницу
    return RedirectResponse(url="/", status_code=303)

# Маршрут для отметки задачи как выполненной/невыполненной
@app.get("/toggle/{todo_id}")
async def toggle_todo(todo_id: str):
    # Ищем задачу по ID
    for todo in todo_db:
        if todo.id == todo_id:
            # Меняем статус
            todo.completed = not todo.completed
            return RedirectResponse(url="/", status_code=303)
    
    # Если задача не найдена
    raise HTTPException(status_code=404, detail="Задача не найдена")

# Маршрут для удаления задачи
@app.get("/delete/{todo_id}")
async def delete_todo(todo_id: str):
    # Ищем задачу по ID
    for i, todo in enumerate(todo_db):
        if todo.id == todo_id:
            # Удаляем задачу
            todo_db.pop(i)
            return RedirectResponse(url="/", status_code=303)
    
    # Если задача не найдена
    raise HTTPException(status_code=404, detail="Задача не найдена")

# API эндпоинт для получения всех задач в формате JSON
@app.get("/api/todos", response_model=List[TodoItem])
async def get_todos_api():
    return todo_db

# API эндпоинт для получения конкретной задачи
@app.get("/api/todos/{todo_id}", response_model=TodoItem)
async def get_todo_api(todo_id: str):
    for todo in todo_db:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Задача не найдена")

# API эндпоинт для создания задачи через API
@app.post("/api/todos", response_model=TodoItem)
async def create_todo_api(todo: TodoItem):
    # Проверяем, что ID уникален
    for existing_todo in todo_db:
        if existing_todo.id == todo.id:
            raise HTTPException(status_code=400, detail="Задача с таким ID уже существует")
    
    # Добавляем задачу
    todo_db.append(todo)
    return todo

# Запуск приложения (для разработки)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)