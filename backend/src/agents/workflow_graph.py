from .trend_agent import fetch_market_trends
from .topic_selector import extract_top10_topics
from .caption_generator import generate_captions
from .reviewer_agent import choose_best_two
from .meme_vision_agent import generate_meme_image
from backend.src.services.gcp_storage import upload_file

def run_full_pipeline():

    trends = fetch_market_trends()
    topics = extract_top10_topics(trends)

    final_output = []

    for topic in topics:
        captions = generate_captions(topic)
        best_two = choose_best_two(captions)

        meme_image_links = []
        for caption in best_two:
            image = generate_meme_image(caption)
            img_bytes = image.candidates[0].generated_images[0].image
            url = upload_file(img_bytes, f"{caption[:10]}.png")
            meme_image_links.append(url)

        final_output.append({
            "topic": topic,
            "captions": best_two,
            "images": meme_image_links
        })

    return final_output
