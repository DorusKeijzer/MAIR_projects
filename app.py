import os
from flask import Flask, request, jsonify, render_template
from main import initialize_states, PreferenceExtractor, RestaurantLookup, DecisionTreeModel, DialogueManager

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
    """Initialize a new conversation and get the initial response."""
    # Identify user (in practice, you would have user authentication or session)
    user_id = 'default_user'  # Static for now; can be extended with user authentication

    # Initialize a new dialogue manager for the user
    if user_id not in dialogue_managers:
        dialogue_managers[user_id] = create_dialogue_manager()

    # Start the conversation and get the initial message
    dialogue_manager = dialogue_managers[user_id]
    response = dialogue_manager.start_conversation()

    # Return the initial response from the bot
    return jsonify({"response": response})

@app.route('/chat', methods=['POST'])
def chat():
    """Continue the conversation based on the user's input."""
    # Get the user input from the request
    data = request.get_json()
    user_input = data.get('message', None)
    # Identify user (in practice, this should be more dynamic)
    user_id = 'default_user'

    # Retrieve the dialogue manager for this user
    if user_id not in dialogue_managers:
        return jsonify({"error": "Conversation not started"}), 400

    dialogue_manager = dialogue_managers[user_id]

    # Process the user input and get the next response
    response = dialogue_manager.start_conversation(user_input)

    # Return the bot's next response
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

