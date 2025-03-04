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
    words = text.lower().split()  # Tokenize input text
    word_embeddings = embedding_model.encode(words, convert_to_tensor=True)

    for i, word_embedding in enumerate(word_embeddings):
        similarity_scores = util.pytorch_cos_sim(word_embedding, flagged_word_embeddings)
        max_score = torch.max(similarity_scores).item()  # Get highest similarity score
        
        if max_score >= threshold:
            return True, words[i], max_score  # Return flagged word and similarity score

    return False, None, None

def detect_vulgar_language(text):
    """Classify the input text using the hate speech detection model."""
    result = classifier(text)
    label = result[0]['label']
    score = result[0]['score']
    return label, score

if __name__ == "__main__":
    while True:
        user_input = input("Enter text to analyze (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        # Step 1: Check for similar words in the CSV list
        is_flagged, flagged_word, similarity = contains_similar_flagged_word(user_input)

        if is_flagged:
            print(f"⚠️ Banned: Detected similar word '{flagged_word}' (Similarity: {similarity:.2f})")
            continue  # Skip the LLM classifier if a match is found

        # Step 2: If no match, use the LLM classifier
        label, score = detect_vulgar_language(user_input)
        print(f"Result: {label} (Confidence: {score:.2f})")

        if label == "hate":
            print("🚫 Banned")
        else:
            print("✅ No hate detected")
