# Impression Tracker API

A simple FastAPI backend for tracking website impressions and storing them in MongoDB.

## Features

- Track website impressions with custom parameters
- Auto-capture user agent and IP address
- Filter and query impressions
- Get statistics and analytics
- CORS enabled for cross-origin requests
- Comprehensive logging

## Prerequisites

- Python 3.8+
- MongoDB (running locally or via connection string)

## Installation

1. Clone or navigate to the project directory
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Update `.env` with your MongoDB connection details if needed

## Running the Server

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check if the API is running

### Track Impression
- **POST** `/track`
  - Request body:
    ```json
    {
      "page_url": "https://example.com/page",
      "user_id": "user123",
      "session_id": "session456",
      "referrer": "https://google.com",
      "metadata": {"custom_field": "value"}
    }
    ```
  - Optional fields: user_id, session_id, referrer, user_agent, ip_address, metadata
  - Response: `{"id": "impression_id", "message": "Impression tracked successfully"}`

### Get Impressions
- **GET** `/impressions` - Get all impressions (paginated)
  - Query parameters:
    - `page_url`: Filter by page URL
    - `user_id`: Filter by user ID
    - `limit`: Results per page (default: 100)
    - `skip`: Pagination offset (default: 0)

### Get Single Impression
- **GET** `/impressions/{impression_id}` - Get a specific impression by ID

### Get Statistics
- **GET** `/stats` - Get aggregated statistics
  - Query parameters:
    - `page_url`: Filter stats by page URL (optional)
  - Returns: Total impressions, breakdown by page, top users

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Example Usage

### Track an impression with curl:
```bash
curl -X POST "http://localhost:8000/track" \
  -H "Content-Type: application/json" \
  -d '{
    "page_url": "https://example.com/products/item1",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

### Get all impressions:
```bash
curl "http://localhost:8000/impressions?limit=10"
```

### Get impressions for a specific page:
```bash
curl "http://localhost:8000/impressions?page_url=https://example.com/products/item1"
```

### Get statistics:
```bash
curl "http://localhost:8000/stats"
```

## Environment Variables

- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `DATABASE_NAME`: Database name (default: `impression_tracker`)
- `ENVIRONMENT`: Environment mode (default: `development`)

## Project Structure

```
impression-hit/
├── main.py              # FastAPI application and endpoints
├── models.py            # Pydantic models for data validation
├── database.py          # MongoDB connection and utilities
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md           # This file
```

## Notes

- Timestamps are automatically added in UTC
- User agent and IP address are auto-captured if not provided
- MongoDB indexes are created automatically on first insert
- The API accepts CORS requests from all origins (adjust in production)
