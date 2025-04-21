import pandas as pd
import torch
import emoji
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    pf = pd.read_csv("Emoji.csv", header=None, names=["emoji"])
    # Convert emojis to text form
    flagged_emojis = [emoji.demojize(e.strip()) for e in pf["emoji"].tolist()]
    print(f"✅ Loaded flagged emojis: {flagged_emojis}")
except FileNotFoundError:
    print("❌ Emoji.csv file not found.")
    flagged_emojis = []

def contains_flagged_emoji(text):
    # Convert full message to demojized form
    demojized_text = emoji.demojize(text)

    for e in flagged_emojis:
        if e in demojized_text:
            return True, e
    return False, None

# Load flagged words from CSV
try:
    df = pd.read_csv("English.csv", header=None, names=["word"])
except FileNotFoundError:
    print("CSV file English.csv not found")
    exit(1)

flagged_words = [word.lower() for word in df["word"].tolist()]
flagged_word_embeddings = embedding_model.encode(flagged_words, convert_to_tensor=True)

# Load hate speech classifier
classifier = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

def contains_similar_flagged_word(text, threshold=0.7):
    words = text.lower().split()
    word_embeddings = embedding_model.encode(words, convert_to_tensor=True)

    for i, word_embedding in enumerate(word_embeddings):
        similarity_scores = util.pytorch_cos_sim(word_embedding, flagged_word_embeddings)
        max_score = torch.max(similarity_scores).item()
        if max_score >= threshold:
            return True, words[i], max_score

    return False, None, None

def detect_vulgar_language(text):
    result = classifier(text)
    label = result[0]['label']
    score = result[0]['score']

    if label == "hate":
        return f"🚫 Hate Speech Detected (Confidence: {score:.2f})"
    else:
        return f"✅ No hate detected (Confidence: {score:.2f})"

def analyze_text(text):
    # Emoji check
    has_emoji, emoji_found = contains_flagged_emoji(text)
    if has_emoji:
        return f"⚠️ Flagged Emoji Detected: '{emoji_found}'"

    # Similar-word check
    is_flagged, flagged_word, similarity = contains_similar_flagged_word(text)
    if is_flagged:
        return f"⚠️ Banned: Detected similar word '{flagged_word}' (Similarity: {similarity:.2f})"

    # Hate speech detection
    return detect_vulgar_language(text)
