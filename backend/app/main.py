import uvicorn

from configs.app_config import DEBUG
from init_app import create_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", reload=DEBUG, app="main:app")
