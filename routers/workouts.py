from db import DB
from schemas import Workout, WorkoutCreate, WorkoutPatch, WorkoutGroup, WorkoutUpdate 
from schemas import MuscleGroup, WorkoutBase, Pagination, WorkourOr404, Filter
from fastapi import FastAPI, Query, Path, HTTPException, Depends, Body, APIRouter
from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("")
def get_workouts(db: DB, filter: Filter, page: Pagination, muscle_group: MuscleGroup | None = None, 
min_weight: Annotated[int, Query(ge=1)] | None = None) -> List[Workout]:
    conditions = []
    params = []
    if muscle_group is not None:
        conditions.append("muscle_group = %s")
        params.append(muscle_group)
    if min_weight is not None:
        conditions.append("weight >= %s")
        params.append(min_weight)
    query = "SELECT * FROM workouts"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += filter
    query += "LIMIT %s OFFSET %s"
    params.append(page.limit)
    params.append(page.offset)
    return db.execute(query, params).fetchall()


@router.get("/stats")
def get_stats(db: DB) -> List[WorkoutGroup]:
    return db.execute("SELECT muscle_group, COUNT(id) AS exercises_count, MAX(weight) AS max_weight FROM workouts GROUP BY muscle_group",).fetchall()


@router.get("/{workout_id}")
def get_workout(db: DB,  workout_id: Annotated[int, Path(gt=0)], workout: WorkourOr404) -> Workout:
    return workout


@router.post("", status_code=201)
def post_workout(db: DB, data: WorkoutCreate) -> Workout:
    new_workout = db.execute("INSERT INTO workouts (exercise, muscle_group, weight, reps) VALUES (%s, %s, %s, %s) RETURNING *", 
    (data.exercise, data.muscle_group, data.weight, data.reps)).fetchone()
    db.commit()
    return new_workout


@router.put("/{workout_id}")
def edit_workout(db: DB, data: WorkoutUpdate, workout_id: Annotated[int, Path(gt=0)], workout: WorkourOr404) -> Workout:
    edited_workout = db.execute("UPDATE workouts SET exercise = %s, muscle_group = %s, weight = %s, reps = %s WHERE id = %s RETURNING *", 
    (data.exercise, data.muscle_group, data.weight, data.reps, workout_id)).fetchone()
    db.commit()
    return edited_workout


@router.patch("/{workout_id}")
def patch_workout(db: DB, data: WorkoutPatch, workout_id: Annotated[int, Path(ge=1)], workout: WorkourOr404) -> Workout:
    updated = data.model_dump(exclude_unset = True)
    if not updated:
        raise HTTPException(400)
    
    conditions = []
    params = []
    for key, value in updated.items():
        conditions.append(f"{key} = %s")
        params.append(value)
    params.append(workout_id)

    query = "UPDATE workouts SET " + ", ".join(conditions) + " WHERE id = %s RETURNING *"
    patched = db.execute(query, params).fetchone()
    db.commit()
    return patched


@router.delete("/{workout_id}", status_code=204)
def delete_workout(db: DB, workout_id: Annotated[int, Path(gt=0)], workout: WorkourOr404) -> None:
    db.execute("DELETE FROM workouts WHERE id = %s", (workout_id,))
    db.commit()
        