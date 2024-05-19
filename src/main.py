from fastapi import FastAPI

from src.api_v1.routers import all_routers


app = FastAPI(
    title="Workflow management"
)


for router in all_routers:
    app.include_router(router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
