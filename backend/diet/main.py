from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as diet_router

app = FastAPI(title="Flow - Diet Recommendation Service")

# Allow requests from the frontend (update this with your Vercel URL later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← replace "*" with your Vercel URL after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diet_router)

@app.get("/")
def health_check():
    return {"status": "Diet service is running"}

