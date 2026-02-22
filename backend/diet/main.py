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

@app.on_event("startup")
async def startup():
    # Pre-load TensorFlow model in background so first /diet/recommend is instant
    import asyncio

    async def _warm_up():
        loop = asyncio.get_event_loop()
        try:
            from routes import load_assets
            await loop.run_in_executor(None, load_assets)
            print("✅ Diet model warmed up")
        except Exception as e:
            print(f"⚠️ Diet model warm-up failed: {e}")

    asyncio.create_task(_warm_up())
    print("🚀 Diet service ready — model loading in background")

@app.api_route("/", methods=["GET", "HEAD"])
def health_check():
    return {"status": "Diet service is running"}
