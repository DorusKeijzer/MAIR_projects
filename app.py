import os
import uuid
from flask import Flask, session, jsonify, render_template
from flask_session import Session
import redis
from dotenv import load_dotenv
from main import initialize_states, PreferenceExtractor, RestaurantLookup, DecisionTreeModel, DialogueManager
from assignment_1a.read_data import train_data_bow, train_label

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Load secret key from .env

# Configure Redis for session management
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'myapp_'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)  # Adjust host/port as necessary
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Initialize the session extension
Session(app)

@app.route('/')
def index():
    return render_template('index.html')

# Function to create a new DialogueManager
def create_dialogue_manager():
    tm = initialize_states()  # Initialize TransitionManager and states
    preference_extractor = PreferenceExtractor()  # Extract user preferences
    restaurant_lookup = RestaurantLookup()  # Lookup for restaurant info
    model = DecisionTreeModel(train_data_bow, train_label)  # Initialize model
    
    # Load model weights
    weights_path = os.path.join(os.getcwd(), "assignment_1a", "model_weights", "decision_tree_model_normal.joblib")
    model.load_weights(weights_path)
    
    # Create a new dialogue manager with all necessary components
    dialogue_manager = DialogueManager(tm, preference_extractor, model, restaurant_lookup)
    return dialogue_manager

@app.route('/start', methods=['POST'])
def start_conversation():
    """Start a new conversation."""
    print("starting a new conversation")
    user_id = str(uuid.uuid4())  # Generate a unique user ID
    session['user_id'] = user_id  # Store the user ID in the session 

    # Initialize a new DialogueManager and store it directly in the session
    dialogue_manager = create_dialogue_manager()
    
    # Store the dialogue manager's state in the session
    session['dialogue_manager'] = dialogue_manager.to_dict()  # Use to_dict() for serialization

    # Start the conversation
    dialogue_manager.start_conversation()
    data = dialogue_manager.to_dict()

    return jsonify({"data": data, "conversationStarted": True})

@app.route('/chat', methods=['POST'])
def chat():
    """Continue the conversation based on the user's input."""
    print("continuing conversation")
    
    # Get the user input from the request
    data = request.get_json()
    user_input = data.get('message', '')
    
    # Retrieve the dialogue manager's state from the session
    if 'dialogue_manager' not in session:
        return jsonify({"error": "Conversation not started"}), 400
    
    dialogue_manager_state = session['dialogue_manager']
    dialogue_manager = create_dialogue_manager()  # Create a new instance
    dialogue_manager.from_dict(dialogue_manager_state)  # Restore the state from the session
    
    # Process the user input and get the next response
    dialogue_manager.add_user_message(user_input)
    dialogue_manager.continue_conversation(user_input)
    
    # Update the state in the session
    session['dialogue_manager'] = dialogue_manager.to_dict()
    
    # Get all messages from the dialogue manager
    data = dialogue_manager.to_dict()
    
    # Return all messages
    return jsonify({"data": data, "conversationStarted": True})

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5000, debug=True)
