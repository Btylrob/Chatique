from transformers import pipeline

def detect_vulgar_language(text):
    classifier = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")
    result = classifier(text)
    label = result[0]['label']
    score = result[0]['score']
    return label, score

if __name__ == "__main__":
    while True:
        user_input = input("Enter text to analyze (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        label, score = detect_vulgar_language(user_input)
        print(f"Result: {label} (Confidence: {score:.2f})")

        if label == "hate":
            print("banned")
        else:
            print("no hate")    