import uvicorn
from init_app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", reload=True, app="main:app")
