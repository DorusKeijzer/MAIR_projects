import os
import uuid
import logging
from flask import Flask, jsonify, render_template, request
from main import initialize_states, PreferenceExtractor, RestaurantLookup, DecisionTreeModel, DialogueManager
from assignment_1a.read_data import train_data_bow, train_label
import assignment_1c.config as config

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

dialogue_managers = {}

@app.route('/')
def index():
    """Default route with normal preference settings"""
    # Default behavior: assume 'yes_pref' by default
    return render_template('index.html', preference_mode="default")

@app.route('/<preference>/')
def preference_route(preference):
    """Handle different preference modes via URL paths"""
    if preference not in ['no_pref', 'yes_pref']:
        return jsonify({"error": "Invalid preference value"}), 400

    # Render template with the preference mode specified in the URL
    return render_template('index.html', preference_mode=preference)

@app.route('/start', methods=['POST'])
def start_conversation():
    data = request.get_json()
    preference_mode = data.get('preference_mode', 'default')

    app.logger.info(f"Starting conversation with preference_mode: {preference_mode}")
    
    # Generate a user ID and create a dialogue manager
    user_id = str(uuid.uuid4())
    dialogue_manager = create_dialogue_manager(preference_mode=preference_mode)
    
    # Store the dialogue manager in memory (by user ID)
    dialogue_managers[user_id] = dialogue_manager
    
    initial_message = dialogue_manager.start_conversation()
    app.logger.info(f"Initial message: {initial_message}")

    return jsonify({
        "conversationStarted": True,
        "user_id": user_id,
        "data": {
            "messages": [
                {
                    "sender": "bot",
                    "content": initial_message
                }
            ]
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id')
    user_input = data.get('message', '')

    app.logger.info(f"Received chat request. User ID: {user_id}, Message: {user_input}")
    
    # Retrieve the dialogue manager by user ID
    dialogue_manager = dialogue_managers.get(user_id)
    if dialogue_manager is None:
        app.logger.error(f"No dialogue manager found for user ID: {user_id}")
        return jsonify({"error": "Conversation not started"}), 400
    
    # Use the user-specific preference mode stored in the dialogue manager
    preference_confirmation = dialogue_manager.preference_confirmation
    
    # Continue the conversation based on user input
    dialogue_manager.add_user_message(user_input)
    bot_response = dialogue_manager.continue_conversation(user_input)
    
    app.logger.info(f"Bot response: {bot_response}")
    
    messages = dialogue_manager.get_messages()
    formatted_messages = [
        {"sender": "bot" if i % 2 == 0 else "user", "content": msg}
        for i, msg in enumerate(messages)
    ]
    
    return jsonify({
        "conversationStarted": True,
        "data": {
            "messages": formatted_messages
        }
    })

def create_dialogue_manager(preference_mode='default'):
    """Creates a DialogueManager with user-specific preference settings."""
    tm = initialize_states()
    preference_extractor = PreferenceExtractor()
    restaurant_lookup = RestaurantLookup()
    model = DecisionTreeModel(train_data_bow, train_label)
    
    # Load model weights
    weights_path = os.path.join(os.getcwd(), "assignment_1a", "model_weights", "decision_tree_model_normal.joblib")
    model.load_weights(weights_path)
    
    # Initialize dialogue manager with a preference mode
    dialogue_manager = DialogueManager(tm, preference_extractor, model, restaurant_lookup)
    
    # Set user-specific preference in the dialogue manager
    if preference_mode == 'yes_pref':
        dialogue_manager.preference_confirmation = True
    else: 
        dialogue_manager.preference_confirmation = False
    return dialogue_manager


if __name__ == "__main__":
    app.run(debug=True)  # Set debug=True for development; remove in production
