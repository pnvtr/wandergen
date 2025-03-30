from fastapi import FastAPI, Depends, HTTPException
from auth.router import router as auth_router
from auth.dependencies import get_current_user
from model import (
    generate_itinerary, 
    refine_itinerary, 
    revert_to_original, 
    get_refinement_history, 
    toggle_favorite_itinerary, 
    get_favorite_itineraries,
    get_user_itineraries
)
from logger import setup_logger
from schemas import (
    ItineraryRequest,
    RefinementRequest,
    ItineraryResponse,
    RefinedItineraryResponse,
    HealthResponse,
    RefinementHistoryResponse,
    FavoriteUpdate,
    ItineraryList
)
from supabase import create_client

# Setup logger
logger = setup_logger("api")

app = FastAPI(
    title="WanderGen API",
    description="API for generating and refining travel itineraries using AI",
    version="1.0.0"
)

# Public routes
app.include_router(auth_router)

# Protected routes
@app.post("/generate", response_model=ItineraryResponse)
async def create_itinerary(
    request: ItineraryRequest,
    user = Depends(get_current_user)
):
    try:
        itinerary = generate_itinerary(request.mood, request.preferences, user.id)
        return itinerary
    except Exception as e:
        logger.error(f"Failed to generate itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine", response_model=RefinedItineraryResponse)
async def refine_existing_itinerary(
    request: RefinementRequest,
    user = Depends(get_current_user)  # Add authentication
):
    try:
        refined = refine_itinerary(request.itinerary_id, request.refinement_request)
        return RefinedItineraryResponse(refined_itinerary=refined)
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to refine itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/revert/{itinerary_id}", response_model=ItineraryResponse)
async def revert_itinerary(itinerary_id: int, user = Depends(get_current_user)):
    try:
        original = revert_to_original(itinerary_id)
        return ItineraryResponse(itinerary=original)
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to revert itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{itinerary_id}", response_model=RefinementHistoryResponse)
async def get_history(itinerary_id: int, user = Depends(get_current_user)):
    try:
        history = get_refinement_history(itinerary_id)
        return RefinementHistoryResponse(history=history)
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch refinement history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")

@app.post("/itineraries/{itinerary_id}/favorite", response_model=ItineraryResponse)
async def toggle_favorite(
    itinerary_id: int,
    favorite: FavoriteUpdate,
    user = Depends(get_current_user)
):
    try:
        updated = toggle_favorite_itinerary(itinerary_id, user.id, favorite.is_favorite)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/itineraries/favorites", response_model=ItineraryList)
async def get_favorite_itineraries_endpoint(user = Depends(get_current_user)):
    try:
        favorites = await get_favorite_itineraries(user.id)
        return ItineraryList(itineraries=favorites)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/itineraries", response_model=ItineraryList)
async def get_user_itineraries_endpoint(user = Depends(get_current_user)):
    try:
        itineraries = get_user_itineraries(user.id)
        return ItineraryList(itineraries=itineraries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
