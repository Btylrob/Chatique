import pandas as pd
import torch
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load flagged words from CSV
df = pd.read_csv("English.csv", header=None, names=["word"])
flagged_words = [word.lower() for word in df["word"].tolist()]

# Convert flagged words to embeddings
flagged_word_embeddings = embedding_model.encode(flagged_words, convert_to_tensor=True)

# Load hate speech classifier
classifier = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

def contains_similar_flagged_word(text, threshold=0.7):
    """Check if the input text contains words similar to flagged words using embeddings."""
    words = text.lower().split()
    word_embeddings = embedding_model.encode(words, convert_to_tensor=True)

    for i, word_embedding in enumerate(word_embeddings):
        similarity_scores = util.pytorch_cos_sim(word_embedding, flagged_word_embeddings)
        max_score = torch.max(similarity_scores).item()

        if max_score >= threshold:
            return True, words[i], max_score

    return False, None, None

def detect_vulgar_language(text):
    """Classify the input text using the hate speech detection model."""
    result = classifier(text)
    label = result[0]['label']
    score = result[0]['score']

    if label == "hate":
        return f"🚫 Hate Speech Detected (Confidence: {score:.2f})"
    else:
        return f"✅ No hate detected (Confidence: {score:.2f})"

def analyze_text(text):
    """Runs both detection functions and returns the final result."""
    is_flagged, flagged_word, similarity = contains_similar_flagged_word(text)

    if is_flagged:
        return f"⚠️ Vulgar Language Detected: '{flagged_word}' (Similarity: {similarity:.2f})"

    return detect_vulgar_language(text)
