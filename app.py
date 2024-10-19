from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from langdetect import detect
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

def detect_language(text):
    """Detect the language of the given text."""
    try:
        return detect(text)
    except Exception as e:
        print(f"Language detection error: {e}")  # Log the error
        return 'unknown'

def translate_to_english(text, src_lang):
    """Translate text to English from its source language."""
    try:
        translated_text = translator.translate(text, src=src_lang, dest='en').text
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")  # Log the error
        return text

def analyze_sentiment(text):
    """Analyze the sentiment of the text using TextBlob."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def classify_sentiment(text, polarity):
    """Classify the sentiment based on keywords or polarity score."""
    happy_keywords = [
        'sandhosham', 'jolly', 'happy', 'nalla', 'perisu', 'joy', 'enjoy', 'fun', 
        'pleased', 'excited', 'bright', 'cheerful', 'smile', 'sirippu', 'santosham', 
        'santosha', 'arathanai', 'magizhchi', 'vettri', 'win', 'great', 'chanceless', 
        'super', 'semma', 'better', 'nalla vela', 'thrilled', 'eager', 'nalama', 
        'enjoyment', 'delighted', 'achieve', 'power', 'enthusiastic', 'awesome', 
        'fantastic', 'satisfaction', 'success'
    ]
    
    sad_keywords = [
        'kashtam', 'kastama', 'kavala', 'kavalaya', 'kadupu', 'kevalama', 'kadupa', 
        'eruchal', 'eruchala', 'sad', 'varale', 'sogam', 'pain', 'unhappy', 'disappointed', 
        'blue', 'dull', 'gloomy', 'hurt', 'frustrated', 'verupu', 'verupa', 'aluthom', 
        'thavani', 'azha', 'aavum', 'kavani', 'dislike', 'depressed', 'failure', 'loss', 
        'cry', 'loser', 'waste', 'tension', 'problem', 'issue', 'stress', 'karpu', 
        'valikuthu', 'throat choke', 'crying', 'betrayed'
    ]
    
    neutral_keywords = [
        'normal', 'paravala', 'pathukalam', 'okay', 'average', 'steady', 'chill', 
        'regular', 'nothing special', 'nallavela', 'ok', 'ippodhiku', 'so-so', 
        'medium', 'neutral', 'moderate', 'acceptable', 'nothing much', 'usual', 
        'balanced', 'neither', 'idhellam sari', 'middle', 'manam iruka', 'fine', 
        'decent', 'middle-ground', 'undecided', 'stable', 'normalcy'
    ]

    # Lowercase the text for easier keyword matching
    lower_text = text.lower()

    # Check for keywords first, then fallback to polarity
    if any(word in lower_text for word in happy_keywords):
        return "happy"
    elif any(word in lower_text for word in sad_keywords):
        return "sad"
    elif any(word in lower_text for word in neutral_keywords):
        return "neutral"
    else:
        # Use polarity for fallback classification
        if polarity > 0:
            return "happy"
        elif polarity < 0:
            return "sad"
        else:
            return "neutral"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Detect the language of the text
    lang = detect_language(text)
    
    # Translate the text to English if it's not already in English
    if lang != 'en':
        translated_text = translate_to_english(text, lang)
    else:
        translated_text = text

    # Analyze sentiment of the translated text
    polarity = analyze_sentiment(translated_text)
    
    # Classify the sentiment based on both keywords and polarity
    sentiment = classify_sentiment(translated_text, polarity)
    
    return jsonify({
        'sentiment': sentiment, 
        'translated_text': translated_text,
        'original_language': lang
    })

if __name__ == '__main__':
    app.run(debug=True)
