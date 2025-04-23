import uvicorn
from bson import ObjectId
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["todoDB"]
collection = db["todoCollection"]

class Todo(BaseModel):
    name: str
    status: bool

@app.get("/getAll", response_model=list[Todo])
async def get_all_todos():
    cursor = collection.find({})
    items: list[Todo] = []
    for doc in cursor:
        items.append(doc)
    return items


@app.get("/get/{todo_id}", response_model=Todo)
async def get_todo(todo_id: str):
    todo = collection.find_one({"_id": ObjectId(todo_id)})
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"name": todo["name"], "status": todo["status"]}

@app.post("/create", response_model=Todo)
async def create_todo(todo: Todo):
    result = collection.insert_one(todo.model_dump())
    return todo

@app.post("/createMany", response_model=list[Todo])
async def create_many_todos(todos: list[Todo]):
    result = collection.insert_many([todo.model_dump() for todo in todos])
    return todos

@app.put("/update/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, todo: Todo):
    result = collection.update_one({"_id": ObjectId(todo_id)}, {"$set": todo.model_dump()})
    return todo

@app.put("/updateMany", response_model=dict)
async def update_many( filter: dict = Body(..., embed=True), update: dict = Body(..., embed=True)):
    result = collection.update_many(filter, {"$set": update})
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }

@app.delete("/delete/{todo_id}", response_model=dict)
async def delete_todo(todo_id: str):
    result = collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"deleted": todo_id}

@app.delete("/deleteMany", response_model=dict)
async def delete_many_todos(ids: list[str]):
    object_ids = [ObjectId(todo_id) for todo_id in ids]
    result = collection.delete_many({"_id": {"$in": object_ids}})
    return {"deleted_count": result.deleted_count}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
