from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from langdetect import detect
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        return 'unknown'

def is_thanglish(text):
    thanglish_keywords = ['naan', 'kadhal', 'sandhosham', 'perisu', 'magizhchi', 'vettri', 'azhudhu', 'kovam', 'kashtam', 'kavala']
    return any(word in text.lower() for word in thanglish_keywords)

def translate_to_english(text, src_lang):
    try:
        translated_text = translator.translate(text, src=src_lang, dest='en').text
        return translated_text
    except Exception as e:
        return text

def translate_to_target_language(text, target_lang):
    try:
        translated_text = translator.translate(text, dest=target_lang).text
        return translated_text
    except Exception as e:
        return text

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def classify_sentiment(text, polarity):
    happy_keywords = ['sandhosham', 'jolly', 'happy', 'nalla', 'perisu', 'joy', 'enjoy', 'fun', 
        'pleased', 'excited', 'bright', 'cheerful', 'smile', 'sirippu', 'santosham', 
        'santosha', 'arathanai', 'magizhchi', 'vettri', 'win', 'great', 'chanceless', 
        'super', 'semma', 'better', 'nalla vela', 'thrilled', 'eager', 'nalama', 
        'enjoyment', 'delighted', 'achieve', 'power', 'enthusiastic', 'awesome', 
        'fantastic', 'satisfaction', 'success','nalairunthuchu']
    sad_keywords = ['kashtam', 'kastama', 'kavala', 'kavalaya', 'kadupu', 'kevalama', 'kadupa', 
        'eruchal', 'eruchala', 'sad', 'varale', 'sogam', 'pain', 'unhappy', 'disappointed', 
        'blue', 'dull', 'gloomy', 'hurt', 'frustrated', 'verupu', 'verupa', 'aluthom', 
        'thavani', 'azha', 'aavum', 'kavani', 'dislike', 'depressed', 'failure', 'loss', 
        'cry', 'loser', 'waste', 'tension', 'problem', 'issue', 'stress', 'karpu', 
        'valikuthu', 'throat choke', 'crying', 'betrayed','died','dead','accident','sethutan']
    neutral_keywords = ['normal', 'paravala', 'pathukalam', 'okay', 'average', 'steady', 'chill', 
        'regular', 'nothing special', 'nallavela', 'ok', 'ippodhiku', 'so-so', 
        'medium', 'neutral', 'moderate', 'acceptable', 'nothing much', 'usual', 
        'balanced', 'neither', 'idhellam sari', 'middle', 'manam iruka', 'fine', 
        'decent', 'middle-ground', 'undecided', 'stable', 'normalcy','confusing']

    lower_text = text.lower()
    sentiment = "neutral"
    emoji = "😐"

    if any(word in lower_text for word in happy_keywords):
        sentiment = "happy"
        emoji = "😊"
    elif any(word in lower_text for word in sad_keywords):
        sentiment = "sad"
        emoji = "😢"
    elif any(word in lower_text for word in neutral_keywords):
        sentiment = "neutral"
        emoji = "😐"
    else:
        if polarity > 0:
            sentiment = "happy"
            emoji = "😊"
        elif polarity < 0:
            sentiment = "sad"
            emoji = "😢"

    return sentiment, emoji

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text')
    display_language = data.get('display_language', 'en')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    lang = detect_language(text)

    if is_thanglish(text):
        translated_text = translate_to_english(text, 'ta')
    elif lang != 'en':
        translated_text = translate_to_english(text, lang)
    else:
        translated_text = text

    polarity = analyze_sentiment(translated_text)
    sentiment, emoji = classify_sentiment(translated_text, polarity)

    if display_language != 'no_option':
        translated_sentiment = translate_to_target_language(sentiment, display_language)
        translated_original_text = translate_to_target_language(translated_text, display_language)
    else:
        translated_sentiment = sentiment
        translated_original_text = None

    return jsonify({
        'sentiment': translated_sentiment,
        'emoji': emoji,
        'translated_text': translated_original_text,
        'original_language': lang
    })

if __name__ == '__main__':
    app.run(debug=True)
