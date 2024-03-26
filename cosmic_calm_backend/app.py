from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
import spacy

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\Harsh Bhat\OneDrive\Desktop\Cosmic Calm FullStack\cosmic_calm_backend\cosmic-calm-firebase-adminsdk-umqvg-b7d679aea9.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load the SpaCy model for embeddings
nlp = spacy.load("en_core_web_md")

# In your Flask route
@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        # Get user statistics (Minutes and Sessions)
        stats_ref = db.collection('stats').document(user_id)
        stats_data = stats_ref.get().to_dict()
        minutes = stats_data.get('Minutes', 0)
        sessions = stats_data.get('Sessions', 0)

        # Get user answers
        forms_ref = db.collection('form').document(user_id)
        forms_data = forms_ref.get().to_dict()
        answers = forms_data.get('answers', [])

        # Combine user statistics and answers to form a user query
        user_query = ' '.join(answers)

        # Calculate embedding for user query
        user_embedding = nlp(user_query).vector

        # Get meditations data (name, tag, duration)
        meditations_ref = db.collection('meditations')
        meditations_data = [doc.to_dict() for doc in meditations_ref.stream()]

        # Calculate embeddings for all meditations
        meditations_embeddings = []
        for meditation in meditations_data:
            meditation_text = f"{meditation['name']} {meditation['tag']} {meditation['duration']}"
            meditation_embedding = nlp(meditation_text).vector
            meditations_embeddings.append(meditation_embedding)

        # Convert to numpy array for efficient calculations
        meditations_embeddings = np.array(meditations_embeddings)

        similarities = np.dot(meditations_embeddings, user_embedding) / (
                np.linalg.norm(meditations_embeddings, axis=1) * np.linalg.norm(user_embedding))

        top_indices = np.argsort(similarities)[::-1][:3]

        similar_meditations_names = [meditations_data[i]['name'] for i in top_indices]

        return jsonify({
            'user_id': user_id,
            'similar_meditations_names': similar_meditations_names
        })

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Serve the frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path == '':
        return send_from_directory('build', 'index.html')
    else:
        if path.startswith('static/') or path.startswith('media/'):
            return send_from_directory('build', path)
        else:
            return send_from_directory('build', 'index.html')

if __name__ == '__main__':
    # Set Flask app configurations for production
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False

    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
