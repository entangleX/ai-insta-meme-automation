# Data Organization Structure

## Overview
The application automatically organizes all trend data and generated memes in date-based folders with structured JSON files.

## Folder Structure

```
data/
├── 2025-12-06/
│   ├── trends.json              # All fetched trends with metadata
│   └── images/
│       ├── New_election_funding_scandal.png
│       ├── AI_regulation_debate.png
│       └── ...
├── 2025-12-07/
│   ├── trends.json
│   └── images/
│       └── ...
└── ...
```

## JSON Structure

### `trends.json`

```json
{
  "date": "2025-12-06",
  "total_trends": 10,
  "trends": [
    {
      "topic": "New election funding scandal",
      "category": "corruption",
      "description": "A major political party is under fire for alleged hidden funding sources...",
      "fetched_at": "2025-12-06T14:30:45.123456",
      "image_path": "data/images/2025-12-06/New_election_funding_scandal.png",
      "caption": "New election funding scandal - When reality is stranger than fiction 😂",
      "generated": true
    },
    {
      "topic": "AI regulation debate",
      "category": "tech_ai",
      "description": "Global discussions intensify around regulating artificial intelligence...",
      "fetched_at": "2025-12-06T14:30:45.123456",
      "image_path": "data/images/2025-12-06/AI_regulation_debate.png",
      "caption": "AI regulation debate - The internet never disappoints 😄",
      "generated": true
    }
  ]
}
```

## Trend Categories

The system categorizes trends into:
- `politics` - Political satire and news
- `scam` - Scam-related topics
- `corruption` - Corruption scandals
- `social` - Social issues and debates
- `entertainment` - Bollywood, celebrities, pop culture
- `international` - Global news
- `tech_ai` - Technology and AI topics
- `economy` - Economic news and trends
- `other` - Miscellaneous topics

## Workflow

1. **Fetch Trends** (Step 1)
   - CrewAI agents search current internet trends
   - Fetches ~25-30 candidate topics
   - Selects top 10 most viral topics
   - Saves to `data/YYYY-MM-DD/trends.json`

2. **Generate Images** (Step 2)
   - For each trend, generates meme image
   - Saves to `data/images/YYYY-MM-DD/{topic_name}.png`
   - Updates JSON with image path and caption

3. **Access Data**
   - Frontend can query by date: `GET /trends?date=2025-12-06`
   - Get specific trend: `GET /trend?date=2025-12-06&topic=New+election+funding+scandal`
   - View image: `GET /image/2025-12-06/New_election_funding_scandal`

## API Endpoints

- `POST /generate_memes` - Run full pipeline for today
- `GET /dates` - List all available dates
- `GET /trends?date=YYYY-MM-DD` - Get all trends for a date
- `GET /trend?date=YYYY-MM-DD&topic=...` - Get specific trend with image
- `GET /image/{date}/{topic}` - Serve image file
- `POST /publish` - Publish meme to Instagram

## Benefits

✅ **Organized by date** - Easy to find trends from any day
✅ **Structured JSON** - All metadata in one place
✅ **Reusable** - Can regenerate images or use different dates
✅ **Searchable** - Query trends by category, date, or topic
✅ **Audit trail** - Know when each trend was fetched
