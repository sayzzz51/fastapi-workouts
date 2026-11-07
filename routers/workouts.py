from db import DB
from schemas import Workout, WorkoutCreate, WorkoutPatch, WorkoutGroup, WorkoutUpdate, MuscleGroup, WorkoutBase
from fastapi import FastAPI, Query, Path, HTTPException, Depends, Body, APIRouter
from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("")
def get_workouts(db: DB, muscle_group: MuscleGroup | None = None, min_weight: Annotated[int, Query(ge=1)] | None = None) -> List[Workout]:
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
    query += " ORDER BY id "
    return db.execute(query, params).fetchall()


@router.get("/stats")
def get_stats(db: DB) -> List[WorkoutGroup]:
    return db.execute("SELECT muscle_group, COUNT(id) AS exercises_count, MAX(weight) AS max_weight FROM workouts GROUP BY muscle_group",).fetchall()


@router.get("/{workout_id}")
def get_workout(db: DB, workout_id: Annotated[int, Path(gt=0)]) -> Workout:
    workouty = db.execute("SELECT * FROM workouts WHERE id = %s",(workout_id,),).fetchone()
    if workouty is None:
        raise HTTPException(404)
    return workouty


@router.post("", status_code=201)
def post_workout(db: DB, data: WorkoutCreate) -> Workout:
    new_workout = db.execute("INSERT INTO workouts (exercise, muscle_group, weight, reps) VALUES (%s, %s, %s, %s) RETURNING *", 
    (data.exercise, data.muscle_group, data.weight, data.reps)).fetchone()
    db.commit()
    return new_workout


@router.put("/{workout_id}")
def edit_workout(db: DB, data: WorkoutUpdate, workout_id: Annotated[int, Path(gt=0)]) -> Workout:
    edited_workout = db.execute("UPDATE workouts SET exercise = %s, muscle_group = %s, weight = %s, reps = %s WHERE id = %s RETURNING *", 
    (data.exercise, data.muscle_group, data.weight, data.reps, workout_id)).fetchone()
    if not edited_workout:
        raise HTTPException(404)
    db.commit()
    return edited_workout


@router.patch("/{workout_id}")
def patch_workout(db: DB, data: WorkoutPatch, workout_id: Annotated[int, Path(ge=1)]) -> Workout:
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
    if patched is None: 
        raise HTTPException(404)
    db.commit()
    return patched


@router.delete("/{workout_id}", status_code=204)
def delete_workout(db: DB, workout_id: Annotated[int, Path(gt=0)]) -> None:
    deleted_workout = db.execute("DELETE FROM workouts WHERE id = %s RETURNING *", (workout_id,)).fetchone()
    if deleted_workout is None:
        raise HTTPException(404)
    db.commit()