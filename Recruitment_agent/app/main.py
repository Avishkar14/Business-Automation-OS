from fastapi import FastAPI
from routers.jobs import router as jobs_router
from routers.candidates import router as candidates_router
from routers.applications import router as applications_router
from routers.screenings import router as screenings_router
from routers.tests import router as tests_router
from routers.questions import router as questions_router
from routers.test_attempts import router as test_attempts_router
from routers.answers import router as answers_router

app = FastAPI(title="Recruitment Agent API")

app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(applications_router)
app.include_router(screenings_router)
app.include_router(tests_router)
app.include_router(questions_router)
app.include_router(test_attempts_router)
app.include_router(answers_router)

@app.get("/")
def root():
    return {"message": "Recruitment Agent API is running"}
