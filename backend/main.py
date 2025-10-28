"""
Main entry point for the FastAPI backend application.
This file initializes the FastAPI app and includes basic setup.
"""

from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(
    title="NoCodeBackend API",
    description="A FastAPI backend for NoCodeBackend",
    version="1.0.0"
)

# Basic root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to NoCodeBackend API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}