"""
API Gateway Service for DataAptor AI

This service handles authentication, rate limiting, and routing of API requests
to the appropriate microservices.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
import time
from datetime import datetime, timedelta
import jwt
from collections import defaultdict

app = FastAPI(
    title="DataAptor AI API Gateway",
    description="API Gateway for the DataAptor AI platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ORCHESTRATION_SERVICE_URL = os.getenv("ORCHESTRATION_SERVICE_URL", "http://localhost:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8080")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# In-memory rate limiting store (use Redis in production)
rate_limit_store = defaultdict(list)

security = HTTPBearer(auto_error=False)


# Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCredentials(BaseModel):
    username: str
    password: str


class DatasetUploadResponse(BaseModel):
    id: int
    name: str
    file_type: str
    file_size: int
    created_at: str
    metadata: dict


class AssessmentRequest(BaseModel):
    dataset_id: int
    modules: Optional[List[str]] = None
    weights: Optional[dict] = None


class AssessmentResponse(BaseModel):
    id: int
    dataset_id: int
    status: str
    started_at: str
    modules: List[str]


# Rate limiting middleware
def check_rate_limit(client_ip: str) -> bool:
    """Check if the client has exceeded the rate limit."""
    current_time = time.time()
    window_start = current_time - RATE_LIMIT_WINDOW
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if t > window_start
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return True


# Authentication helpers
def create_token(user_id: str, username: str) -> str:
    """Create a JWT token for the user."""
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """Get the current user from the JWT token."""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)


# Rate limiting dependency
async def rate_limit_check(request: Request):
    """Check rate limit for the request."""
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


# Authentication endpoints
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserCredentials):
    """
    Authenticate user and return JWT token.
    
    In production, this would validate against Keycloak or another auth service.
    """
    # For MVP, accept any credentials and return a token
    # In production, validate against auth service
    token = create_token(user_id="1", username=credentials.username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600
    )


@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh the JWT token."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = create_token(
        user_id=current_user["sub"],
        username=current_user["username"]
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600
    )


# Dataset endpoints (proxy to orchestration service)
@app.post("/api/datasets/upload", dependencies=[Depends(rate_limit_check)])
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a dataset for assessment."""
    async with httpx.AsyncClient() as client:
        try:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            data = {"name": name} if name else {}
            response = await client.post(
                f"{ORCHESTRATION_SERVICE_URL}/api/datasets/upload",
                files=files,
                data=data,
                timeout=300.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.get("/api/datasets", dependencies=[Depends(rate_limit_check)])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """List all datasets."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/datasets",
                params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.get("/api/datasets/{dataset_id}", dependencies=[Depends(rate_limit_check)])
async def get_dataset(
    dataset_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get details for a specific dataset."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/datasets/{dataset_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.delete("/api/datasets/{dataset_id}", dependencies=[Depends(rate_limit_check)])
async def delete_dataset(
    dataset_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a dataset."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{ORCHESTRATION_SERVICE_URL}/api/datasets/{dataset_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


# Assessment endpoints (proxy to orchestration service)
@app.post("/api/assessments", dependencies=[Depends(rate_limit_check)])
async def start_assessment(
    request: AssessmentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start an assessment for a dataset."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ORCHESTRATION_SERVICE_URL}/api/assessments",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.get("/api/assessments", dependencies=[Depends(rate_limit_check)])
async def list_assessments(
    dataset_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """List all assessments."""
    async with httpx.AsyncClient() as client:
        try:
            params = {"skip": skip, "limit": limit}
            if dataset_id:
                params["dataset_id"] = dataset_id
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/assessments",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.get("/api/assessments/{assessment_id}", dependencies=[Depends(rate_limit_check)])
async def get_assessment(
    assessment_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get details for a specific assessment."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/assessments/{assessment_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.get("/api/assessments/{assessment_id}/status", dependencies=[Depends(rate_limit_check)])
async def get_assessment_status(
    assessment_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of an assessment."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/assessments/{assessment_id}/status"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


# Report endpoints (proxy to orchestration service)
@app.get("/api/reports/{assessment_id}", dependencies=[Depends(rate_limit_check)])
async def get_report(
    assessment_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get the report for an assessment."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/reports/{assessment_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


@app.get("/api/reports/{assessment_id}/export", dependencies=[Depends(rate_limit_check)])
async def export_report(
    assessment_id: int,
    format: str = "json",
    current_user: dict = Depends(get_current_user)
):
    """Export the report in the specified format."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORCHESTRATION_SERVICE_URL}/api/reports/{assessment_id}/export",
                params={"format": format}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Upstream service error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
