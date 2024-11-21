from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
template = Jinja2Templates(directory="templates")


class User(BaseModel):
    id: Optional[int] = None
    username: str = Field(min_length=5, max_length=20, description='Enter username', example='UrbanStudent')
    age: int = Field(ge=18, le=120, description='Enter age', example=25)


users: List[User] = []


@app.get("/", response_class=HTMLResponse)
async def get_main_pages(request: Request):
    return template.TemplateResponse("users.html", {'request': request, 'users': users})


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def get_all_users(request: Request, user_id: int):
    user = next((user for user in users if user.id == user_id), None)
    if user:
        return template.TemplateResponse("users.html", {"request": request, "user": user, "title": "Пользователь"})
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/user", response_model=User, response_class=HTMLResponse)
async def reg_new_users(request: Request, user: User):
    if users:
        user.id = max(users, key=lambda usr: usr.id or 0).id + 1
    else:
        user.id = 1
    new_user = User(id=user.id, username=user.username, age=user.age)
    users.append(new_user)
    return template.TemplateResponse("users.html", {"request": request, "user": new_user})


@app.put("/user/{user_id}", response_model=User)
async def update_users_db(user_id: int, user: User):
    for i, u in enumerate(users):
        if u.id == user_id:
            users[i] = User(id=user_id, username=user.username, age=user.age)
            return users[i]
    raise HTTPException(status_code=404, detail="User was not found")


@app.delete("/user/{user_id}", response_model=User)
async def delete_user(user_id: int):
    for i, u in enumerate(users):
        if u.id == user_id:
            deleted_user = users.pop(i)
            return deleted_user
    raise HTTPException(status_code=404, detail="User was not found")


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')

