from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
from fastapi import Depends, Query, Path, HTTPException
from db import DB
from functools import wraps 
import time

MuscleGroup = Literal["chest", "back", "legs", "arms"]

class WorkoutBase(BaseModel):
    exercise: Annotated[str, Field(max_length=50)]
    muscle_group: MuscleGroup
    weight: Annotated[int, Field(ge=0)]
    reps: Annotated[int, Field(gt=0, le=100)]

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: Annotated[int, Field(gt=0)]

class WorkoutGroup(BaseModel):
    muscle_group: MuscleGroup
    exercises_count: int
    max_weight: int

class WorkoutPatch(BaseModel):
    exercise: Annotated[str, Field(max_length=50)] | None = None
    muscle_group: MuscleGroup | None = None
    weight: Annotated[int, Field(ge=0)] | None = None
    reps: Annotated[int, Field(gt=0)] | None = None 

class PaginationParams(BaseModel):
    limit: Annotated[int, Field(ge=1, le=100)] = 10
    offset: Annotated[int, Field(ge=0)] = 0

Pagination = Annotated[PaginationParams, Query()]


### Проверка на 404
def getid_or404(db: DB, workout_id: Annotated[int, Path(ge=1)]):
    workout = db.execute("SELECT * FROM workouts WHERE id = %s",(workout_id,)).fetchone()
    if workout is None:
        raise HTTPException(404)
    return workout
    

WorkourOr404 = Annotated[dict, Depends(getid_or404)]

Order = Literal["ASC", "DESC"]
Sort = Literal["id", "weight", "reps"]
### Зависимость сортировки и фильтра
def filter(sort: Sort = "id", order: Order = "ASC") -> str:
    filtred = f" ORDER BY {sort} {order} "
    return filtred
    
Filter = Annotated[str, Depends(filter)]



def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"запускаю функцию {func.__name__}")
        start = time.time()
        res = func(*args,**kwargs)
        end = time.time() - start
        print(f"Время работы: {round(end,3)}")
        return res
    return wrapper