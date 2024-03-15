comment = "I think Google will overtake Apple in like 5 years i also think Nvidia is going to take over the world."
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
nlp = spacy.load("en_core_web_trf")

doc = nlp(comment)

# Define aspects
aspects = ['Apple', 'Google', 'Nvidia']
# Perform aspect-based sentiment analysis
for aspect in aspects:
    print(f"Sentiment analysis for {aspect}:")
    aspect_sentiments = []
    for sentence in doc.sents:
        print(sentence)
        if aspect.lower() in sentence.text.lower():
            aspect_sentiment = 0
            for token in sentence:
                if token.dep_ == "neg":
                    aspect_sentiment -= 1
                elif token.dep_ == "advmod" and token.text == "not":
                    aspect_sentiment -= 1
                elif token.dep_ == "advmod" and token.head.pos_ == "VERB":
                    aspect_sentiment -= 1
                elif token.dep_ == "amod" and token.head.pos_ == "NOUN":
                    aspect_sentiment += 1
                elif token.dep_ == "ROOT" and token.pos_ == "VERB":
                    aspect_sentiment += 1
            if aspect_sentiment > 0:
                aspect_sentiments.append('positive')
            elif aspect_sentiment < 0:
                aspect_sentiments.append('negative')
            else:
                aspect_sentiments.append('neutral')

    # Count sentiment occurrences
    sentiment_counts = {sentiment: aspect_sentiments.count(sentiment) for sentiment in set(aspect_sentiments)}
    print(sentiment_counts)