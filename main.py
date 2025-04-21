import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Todo(BaseModel):
    name: str
    status: bool

todo_list: list[Todo] = [Todo(name="Brush Teeth", status=True)]


@app.get("/")
async def read_root() -> list[Todo]:
    return todo_list


@app.post("/add_todo")
async def add_todo(todo: Todo) -> Todo | str:
    if any(existing_todo.name.lower() == todo.name.lower() for existing_todo in todo_list):
        raise HTTPException(status_code=403, detail="Error: todo already present")
    todo.name = todo.name.title()
    todo_list.append(todo)
    with open('tasks.json', 'w') as _taskfd:
        json.dump([todo.model_dump() for todo in todo_list], _taskfd)
    return todo
