import os
from flask import Flask, request, jsonify, render_template
from main import initialize_states, PreferenceExtractor, RestaurantLookup, DecisionTreeModel, DialogueManager
from assignment_1a.read_data import train_data_bow, train_label
app = Flask(__name__)

# Global variable to hold dialogue managers per user
dialogue_managers = {}

@app.route('/')
def index():
    return render_template('index.html')

# Initialization of various components
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
    user_id = 'default_user'  # In practice, this should be more dynamic
    if user_id not in dialogue_managers:
        # Initialize a new DialogueManager for this user
        dialogue_managers[user_id] = create_dialogue_manager()
    
    # Start the conversation
    response = dialogue_managers[user_id].start_conversation()

    return jsonify({"response": "Hello! What kind of restaurant are you looking for?", "conversationStarted": True})

@app.route('/chat', methods=['POST'])
def chat():
    """Continue the conversation based on the user's input."""
    print("continuing conversation")
    # Get the user input from the request
    data = request.get_json()
    user_input = data.get('message', '')
    
    # Identify user (in practice, this should be more dynamic)
    user_id = 'default_user'
    
    # Retrieve the dialogue manager for this user
    if user_id not in dialogue_managers:
        return jsonify({"error": "Conversation not started"}), 400
    
    dialogue_manager = dialogue_managers[user_id]
    
    # Process the user input and get the next response
    response = dialogue_manager.continue_conversation(user_input)
    
    # Return the bot's next response
    return jsonify({"response": response, "conversationStarted": True})

if __name__ == '__main__':
    print("test")
    app.run(host='0.0.0.0', port=5000, debug=True)

