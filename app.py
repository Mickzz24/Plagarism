import os
import sqlite3
import jwt
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Replace with a strong secret key in production
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()

init_db()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!', 'error': 'Unauthorized'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except Exception as e:
            return jsonify({'message': 'Token is invalid or expired!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), 'documents')

def load_documents():
    """Load text from all .txt files in the documents directory."""
    documents = []
    filenames = []
    if not os.path.exists(DOCUMENTS_DIR):
        os.makedirs(DOCUMENTS_DIR)
        
    for filename in os.listdir(DOCUMENTS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCUMENTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                documents.append(f.read())
            filenames.append(filename)
    return documents, filenames

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        db = get_db()
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        db.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    username = data['username']
    password = data['password']

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if user and check_password_hash(user['password'], password):
        token = jwt.encode({'username': user['username']}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/check', methods=['POST'])
@token_required
def check_plagiarism(current_user):
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
        
    user_text = data['text'].strip()
    if not user_text:
        return jsonify({'error': 'Empty input text'}), 400

    reference_docs, filenames = load_documents()
    
    # --- Live Academic Papers Search via arXiv API ---
    try:
        import urllib.request
        import urllib.parse
        import xml.etree.ElementTree as ET
        import re
        from collections import Counter
        
        # Extract top keywords to search the academic DB efficiently
        words = re.findall(r'\w+', user_text.lower())
        stopwords = set('the of and a to in is you that it he was for on are as with his they i at be this have from or one had by words but not what all were we when your can said there use an each which she do how their if will up other about out many then them these so some her would make like him into time has look two more write go see number no way could people my than first water been call who oil its now find long down day did get come made may part'.split())
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        top_keywords = [k[0] for k in Counter(keywords).most_common(4)]
        search_query = "+".join(top_keywords)
        
        if search_query:
            url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(search_query)}&start=0&max_results=3"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read()
                root = ET.fromstring(data)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                    summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                    # Add academic paper abstract to our reference docs
                    reference_docs.append(summary)
                    filenames.append(f"Web Source: arXiv ({title[:40]}...)")
    except Exception as e:
        print("Academic web search failed:", e)
    # -------------------------------------------------
    # ---------------------------------------
    
    if not reference_docs:
        return jsonify({
            'similarity': 0,
            'message': 'No reference documents found in database.',
            'details': {}
        })

    # Combine user text and reference documents
    all_texts = [user_text] + reference_docs
    
    # Calculate TF-IDF
    # Using English stop words to ignore common words like 'is', 'the', etc.
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
    except ValueError:
         # Handles case where text is empty or only stop words
         return jsonify({'similarity': 0, 'details': {}})

    # Calculate cosine similarity between user_text (index 0) and all other docs
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Calculate percentages
    similarity_percentages = [round(score * 100, 2) for score in cosine_similarities]
    
    if len(similarity_percentages) == 0:
        max_similarity = 0
    else:
        max_similarity = max(similarity_percentages)
        
    # Match docs with scores
    details = {filenames[i]: similarity_percentages[i] for i in range(len(filenames))}
    
    return jsonify({
        'similarity': max_similarity,
        'details': details
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
