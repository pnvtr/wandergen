from fastapi import FastAPI, HTTPException
from model import generate_itinerary, refine_itinerary, revert_to_original, get_refinement_history
from logger import setup_logger
from schemas import (
    ItineraryRequest,
    RefinementRequest,
    ItineraryResponse,
    RefinedItineraryResponse,
    HealthResponse,
    RefinementHistoryResponse
)

# Setup logger
logger = setup_logger("api")

app = FastAPI(
    title="WanderGen API",
    description="API for generating and refining travel itineraries using AI",
    version="1.0.0"
)

@app.post("/generate", response_model=ItineraryResponse)
async def create_itinerary(request: ItineraryRequest):
    try:
        itinerary = generate_itinerary(request.mood, request.preferences)
        return ItineraryResponse(itinerary=itinerary)
    except Exception as e:
        logger.error(f"Failed to generate itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine", response_model=RefinedItineraryResponse)
async def refine_existing_itinerary(request: RefinementRequest):
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
async def revert_itinerary(itinerary_id: int):
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
async def get_history(itinerary_id: int):
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
