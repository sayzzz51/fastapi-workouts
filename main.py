from fastapi import FastAPI
from routers import workouts

app = FastAPI()
app.include_router(workouts.router)
    


