from fastapi import FastAPI
from app.api.routes import router
from app.utils.logger import LoggingMiddleware
from app.utils.exceptions import register_exception_handlers

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    version="1.0.0"
)

from fastapi.responses import HTMLResponse

# Register logging middleware
app.add_middleware(LoggingMiddleware)

# Register global exception handlers
register_exception_handlers(app)

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend file not found</h1>", status_code=404)

app.include_router(router)
