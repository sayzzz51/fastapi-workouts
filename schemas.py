from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field

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