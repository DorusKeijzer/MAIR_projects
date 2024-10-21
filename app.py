import os
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
from main import initialize_states, PreferenceExtractor, RestaurantLookup, DecisionTreeModel, DialogueManager
from assignment_1a.read_data import train_data_bow, train_label
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Load secret key from .env

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
    # Initialize a new DialogueManager for the session
    session['dialogue_manager'] = create_dialogue_manager()  # Store the dialogue manager in session
    
    # Start the conversation
    dialogue_manager = session['dialogue_manager']
    dialogue_manager.start_conversation()
    messages = dialogue_manager.get_messages()

    return jsonify({"messages": messages, "conversationStarted": True})

@app.route('/chat', methods=['POST'])
def chat():
    """Continue the conversation based on the user's input."""
    print("continuing conversation")
    
    # Get the user input from the request
    data = request.get_json()
    user_input = data.get('message', '')
    
    # Retrieve the dialogue manager for this user from the session
    if 'dialogue_manager' not in session:
        return jsonify({"error": "Conversation not started"}), 400
    
    dialogue_manager = session['dialogue_manager']
    
    # Add user message to the dialogue manager
    dialogue_manager.add_user_message(user_input)
    
    # Process the user input and get the next response
    dialogue_manager.continue_conversation(user_input)
    
    # Get all messages from the dialogue manager
    messages = dialogue_manager.get_messages()
    
    # Return all messages
    return jsonify({"messages": messages, "conversationStarted": True})

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5000, debug=True)

