from .trend_agent import fetch_market_trends
from .prompt_generator import generate_meme_prompt, generate_caption_for_image
from .meme_vision_agent import generate_meme_image
from backend.src.services.file_manager import (
    save_trends_json,
    save_meme_image,
    update_trend_with_image,
    get_date_folder
)
from datetime import datetime
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)

def run_full_pipeline(date_str: str = None):
    """
    Complete workflow:
    1. Fetch trends using CrewAI agents (saves to data/YYYY-MM-DD/trends.json)
    2. Generate prompts based on mood/category
    3. Generate images and save with topic names
    4. Update JSON with image paths and captions
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Starting pipeline for date: {date_str}")

    # Step 1: Fetch trends using CrewAI
    logger.info("Step 1: Fetching trends using CrewAI agents...")
    try:
        trends = fetch_market_trends()  # Returns list of HotTopic objects

        if not trends:
            logger.error("No trends found - fetch_market_trends returned empty list")
            return {"status": "error", "message": "No trends found. Check backend logs for details."}

        logger.info(f"Fetched {len(trends)} trends")
    except Exception as e:
        logger.error(f"Error in fetch_market_trends: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Error fetching trends: {str(e)}"}

    # Step 2: Save trends to JSON
    logger.info(f"Step 2: Saving {len(trends)} trends to data/{date_str}/trends.json...")
    try:
        save_trends_json(trends, date_str)
    except Exception as e:
        logger.error(f"Error saving trends: {str(e)}", exc_info=True)

    # Step 3: Generate images for each trend
    logger.info("Step 3: Generating images...")
    generated_count = 0

    for trend in trends:
        try:
            # Generate prompt based on mood/category
            prompt = generate_meme_prompt(
                trend.topic,
                trend.description,
                trend.category.value  # Convert enum to string
            )

            # Generate caption for Instagram
            caption = generate_caption_for_image(
                trend.topic,
                trend.description,
                trend.category.value
            )

            # Generate image
            logger.info(f"Generating image for: {trend.topic}")
            image_response = generate_meme_image(prompt)
            img_bytes = image_response.candidates[0].generated_images[0].image

            # Save image with topic name
            image_path = save_meme_image(img_bytes, trend.topic, date_str)

            # Update trend JSON with image path and caption
            update_trend_with_image(trend.topic, image_path, caption, date_str)

            generated_count += 1
            logger.info(f"Generated image {generated_count}/{len(trends)}: {trend.topic}")

        except Exception as e:
            logger.error(f"Error generating image for {trend.topic}: {str(e)}")
            continue

    logger.info(f"Pipeline completed. Generated {generated_count}/{len(trends)} images")

    return {
        "status": "success",
        "date": date_str,
        "total_trends": len(trends),
        "generated_images": generated_count
    }
