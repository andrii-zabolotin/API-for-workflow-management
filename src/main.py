from fastapi import FastAPI


app = FastAPI(
    title="Workflow management"
)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
