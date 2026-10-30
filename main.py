"""FastAPI entry point for the Boond web application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.auth import router as auth_router
from routers.posts import router as posts_router
from routers.users import router as users_router


app = FastAPI(
    title="Boond Smart Water Harvesting Assistant",
    description="Rainwater harvesting feasibility, cost, and rainfall estimates.",
)

app.include_router(posts_router)
app.include_router(auth_router)
app.include_router(users_router)

# Serve the HTML, CSS, JavaScript, and images from the same origin as the API.
frontend_directory = Path(__file__).resolve().parent / "frontend sih"
app.mount(
    "/",
    StaticFiles(directory=frontend_directory, html=True),
    name="frontend",
)
