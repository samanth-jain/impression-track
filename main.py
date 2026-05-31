from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId
from models import ImpressionCreate, ImpressionResponse
from database import connect_to_mongo, close_mongo_connection, get_database
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Impression Tracker API",
    description="Simple API to track website impressions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    close_mongo_connection()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/track")
async def track_impression(impression: ImpressionCreate, request: Request):
    """
    Track a website impression.
    
    Parameters:
    - page_url: URL of the page being tracked (required)
    - user_id: Optional user identifier
    - session_id: Optional session identifier
    - referrer: Optional referrer URL
    - user_agent: Optional user agent (auto-filled if not provided)
    - ip_address: Optional IP address (auto-filled if not provided)
    - metadata: Optional metadata as JSON object
    """
    try:
        db = get_database()
        
        # Auto-fill user_agent if not provided
        if not impression.user_agent:
            impression.user_agent = request.headers.get("user-agent", "")
        
        # Auto-fill ip_address if not provided
        if not impression.ip_address:
            impression.ip_address = request.client.host if request.client else ""
        
        impression_dict = impression.dict()
        impression_dict["timestamp"] = datetime.utcnow()
        
        result = db.impressions.insert_one(impression_dict)
        
        logger.info(f"Impression tracked: {result.inserted_id}")
        
        return {
            "id": str(result.inserted_id),
            "message": "Impression tracked successfully"
        }
    except Exception as e:
        logger.error(f"Error tracking impression: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/impressions")
async def get_impressions(
    page_url: str = None,
    user_id: str = None,
    limit: int = 100,
    skip: int = 0
):
    """
    Get impressions with optional filtering.
    
    Parameters:
    - page_url: Filter by page URL
    - user_id: Filter by user ID
    - limit: Number of results to return (default: 100)
    - skip: Number of results to skip for pagination (default: 0)
    """
    try:
        db = get_database()
        
        # Build filter
        filter_dict = {}
        if page_url:
            filter_dict["page_url"] = page_url
        if user_id:
            filter_dict["user_id"] = user_id
        
        # Query database
        impressions = list(
            db.impressions.find(filter_dict)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON response
        for imp in impressions:
            imp["_id"] = str(imp["_id"])
        
        return {
            "count": len(impressions),
            "impressions": impressions
        }
    except Exception as e:
        logger.error(f"Error fetching impressions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/impressions/{impression_id}")
async def get_impression(impression_id: str):
    """Get a specific impression by ID"""
    try:
        db = get_database()
        
        if not ObjectId.is_valid(impression_id):
            raise HTTPException(status_code=400, detail="Invalid impression ID")
        
        impression = db.impressions.find_one({"_id": ObjectId(impression_id)})
        
        if not impression:
            raise HTTPException(status_code=404, detail="Impression not found")
        
        impression["_id"] = str(impression["_id"])
        return impression
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching impression: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats(page_url: str = None):
    """
    Get statistics about impressions.
    
    Parameters:
    - page_url: Filter stats by page URL (optional)
    """
    try:
        db = get_database()
        
        match_stage = {}
        if page_url:
            match_stage = {"$match": {"page_url": page_url}}
        
        pipeline = []
        if match_stage:
            pipeline.append(match_stage)
        
        pipeline.extend([
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "by_page": [
                        {"$group": {"_id": "$page_url", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}}
                    ],
                    "by_user": [
                        {"$match": {"user_id": {"$ne": None}}},
                        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 10}
                    ]
                }
            }
        ])
        
        stats = list(db.impressions.aggregate(pipeline))
        
        if stats:
            return stats[0]
        else:
            return {
                "total": [],
                "by_page": [],
                "by_user": []
            }
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
