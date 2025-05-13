import logging
import pandas as pd
import torch
import emoji
import bot_commands
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from logger_config import logger
import re

# Load embedeed model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

#load global variables for toggle functionality
global url
url = True

global nsfwemoji
nsfwemoji = True

#load urls from url.csv
try:
    pf = pd.read_csv("csv_data/url.csv")  # using real header
    flagged_url = [
        ext.strip().lower() for ext in pf["extension"].tolist()
        if isinstance(ext, str) and ext.startswith(".")
    ]
    logger.info(
        f"✅ Loaded {len(flagged_url)} flagged URL extensions from url.csv.")
    print(f"✅ Loaded {len(flagged_url)} flagged URL extensions.")
except FileNotFoundError:
    logger.error("❌ url.csv not found.")
    print("❌ url.csv not found.")
    flagged_url = []


def contains_flagged_url(text):
    text = text.lower()

    # Skip text containing '/t' or if '/' is used by itself
    if '/t' in text or text == '/':
        return False, None

    # Use regex to detect URLs in the text
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(url_pattern, text):
        # Check for flagged URL extensions
        for ext in flagged_url:
            if ext in text:
                return True, ext  # Return the flagged extension
    return False, None


# Load flagged emojis
try:
    emoji_df = pd.read_csv("csv_data/Emoji.csv")  # uses header
    flagged_emojis = [
        emoji.demojize(str(e).strip()) for e in emoji_df["emoji"].tolist()
    ]
    logger.info(
        f"✅ Loaded {len(flagged_emojis)} flagged emojis from Emoji.csv.")
    print(f"✅ Loaded {len(flagged_emojis)} flagged emojis.")
except FileNotFoundError:
    logger.error("❌ Emoji.csv not found.")
    print("❌ Emoji.csv not found.")
    flagged_emojis = []


def contains_flagged_emoji(text):
    demojized_text = emoji.demojize(text)
    for e in flagged_emojis:
        if e in demojized_text:
            return True, e
    return False, None


# Load english csv data
try:
    word_df = pd.read_csv("csv_data/English.csv")
    flagged_words = [str(word).lower() for word in word_df["word"].tolist()]
    flagged_word_embeddings = embedding_model.encode(flagged_words,
                                                     convert_to_tensor=True)
    logger.info(
        f"✅ Loaded and encoded {len(flagged_words)} flagged words from English.csv."
    )
    logger.info(f"✅ Loaded and encoded {len(flagged_words)} flagged words.")
except FileNotFoundError:
    logger.error("❌ English.csv not found.")
    print("❌ English.csv not found.")
    flagged_words = []
    flagged_word_embeddings = torch.tensor([])


def contains_similar_flagged_word(text, threshold=0.7):
    words = text.lower().split()
    word_embeddings = embedding_model.encode(words, convert_to_tensor=True)

    for i, word_embedding in enumerate(word_embeddings):
        similarity_scores = util.pytorch_cos_sim(word_embedding,
                                                 flagged_word_embeddings)
        max_score = torch.max(similarity_scores).item()
        if max_score >= threshold:
            return True, words[i], max_score
    return False, None, None


# Load robert-hate-speech classifier
classifier = pipeline("text-classification",
                      model="facebook/roberta-hate-speech-dynabench-r4-target")


def detect_vulgar_language(text):
    result = classifier(text)
    label = result[0]['label']
    score = result[0]['score']
    if label == "hate":
        return f"🚫 Hate Speech Detected (Confidence: {score:.2f})"
    return f"✅ No hate detected (Confidence: {score:.2f})"


# Main analasis function
def analyze_text(text):
    results = []

    # Emoji check
    if nsfwemoji == True:
        logger.info("Emoji detection off")

    elif nsfwemoji == False:
        emoji_found, flagged_emoji = contains_flagged_emoji(text)
        if emoji_found:
            results.append(f"⚠️ Flagged Emoji Detected: '{flagged_emoji}'")

    # URL check
    if url == False:
        logger.info("URL detection off")

    elif url == True:
        url_found, flagged_ext = contains_flagged_url(text)
        if url_found:
            results.append(f"⚠️ Flagged URL Detected: '{flagged_ext}'")

    # Similar-word check
    is_flagged, flagged_word, similarity = contains_similar_flagged_word(text)
    if is_flagged:
        results.append(
            f"⚠️ Banned Word Detected: '{flagged_word}' (Similarity: {similarity:.2f})"
        )

    # Hate speech check
    results.append(detect_vulgar_language(text))

    return "\n".join(results)
