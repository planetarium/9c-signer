from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def read_root():
        return {"Hello": "World"}

    @app.get("/ping")
    async def pong():
        return {"msg": "pong"}

    return app


app = create_app()

