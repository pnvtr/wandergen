# WanderGen

A travel itinerary generator powered by AI that creates personalized travel plans based on your mood and preferences.

## Features

- 🤖 AI-powered itinerary generation
- 🔄 Itinerary refinement and customization
- 📱 User authentication and profiles
- ⭐ Favorite itineraries
- 📊 Refinement history tracking
- 🔄 Revert to original versions

## Tech Stack

- FastAPI (Python web framework)
- Supabase (Authentication & Database)
- OpenAI GPT-4 (AI model)
- Python 3.8+

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wandergen.git
cd wandergen
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

5. Run the FastAPI backend:
```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/signup` - Create a new account
- `POST /auth/login` - Login to your account
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### Itineraries
- `POST /generate` - Generate a new itinerary
- `POST /refine` - Refine an existing itinerary
- `POST /revert/{itinerary_id}` - Revert to original version
- `GET /history/{itinerary_id}` - Get refinement history
- `GET /itineraries` - Get all user itineraries
- `GET /itineraries/favorites` - Get favorite itineraries
- `POST /itineraries/{itinerary_id}/favorite` - Toggle favorite status

## Example Usage

1. Sign up for an account:
```bash
curl -X POST "http://localhost:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "yourpassword"}'
```

2. Generate an itinerary:
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{"mood": "adventurous", "preferences": "outdoor activities, local cuisine"}'
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
