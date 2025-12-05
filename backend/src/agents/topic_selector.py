def extract_top10_topics(trend_text):
    # Later convert to structured Pydantic model
    lines = trend_text.split("\n")
    topics = [line for line in lines if line.strip()][:10]
    return topics
