from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("C:/Users/Harsh Bhat/OneDrive/Desktop/Cosmic Calm FullStack/cosmic_calm_backend/cosmic-calm-firebase-adminsdk-umqvg-b7d679aea9.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return 'Backend server is running!'

@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        # Get stats data for the specified user ID
        stats_ref = db.collection('stats').document(user_id)
        stats_data = stats_ref.get().to_dict()
        minutes = stats_data.get('Minutes', 0)
        sessions = stats_data.get('Sessions', 0)

        # Get forms data for the specified user ID
        forms_ref = db.collection('form').document(user_id)
        forms_data = forms_ref.get().to_dict()
        answers = forms_data.get('answers', [])

        return jsonify({
            'user_id': user_id,
            'stats': {
                'minutes': minutes,
                'sessions': sessions
            },
            'form': {
                'answers': answers
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting backend server...")
    app.run(debug=True)
