import os
import uuid
import logging
from flask import Flask, jsonify, render_template, request
from flask_session import Session
from main import initialize_states, PreferenceExtractor, RestaurantLookup, DecisionTreeModel, DialogueManager
from assignment_1a.read_data import train_data_bow, train_label

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

dialogue_managers = {}

@app.route('/')
def index():
    return render_template('index.html')

def create_dialogue_manager():
    tm = initialize_states()
    preference_extractor = PreferenceExtractor()
    restaurant_lookup = RestaurantLookup()
    model = DecisionTreeModel(train_data_bow, train_label)
    
    weights_path = os.path.join(os.getcwd(), "assignment_1a", "model_weights", "decision_tree_model_normal.joblib")
    model.load_weights(weights_path)
    
    dialogue_manager = DialogueManager(tm, preference_extractor, model, restaurant_lookup)
    return dialogue_manager

@app.route('/start', methods=['POST'])
def start_conversation():
    app.logger.info("Starting a new conversation")
    user_id = str(uuid.uuid4())
    dialogue_manager = create_dialogue_manager()
    dialogue_managers[user_id] = dialogue_manager
    print(f"user id: {user_id}") 
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
    
    dialogue_manager = dialogue_managers.get(user_id)
    if dialogue_manager is None:
        app.logger.error(f"No dialogue manager found for user ID: {user_id}")
        return jsonify({"error": "Conversation not started"}), 400

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

@app.route('/end', methods=['POST'])
def end_conversation():
    app.logger.info("Ending conversation")
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if user_id in dialogue_managers:
        del dialogue_managers[user_id]
        app.logger.info(f"Conversation ended for user ID: {user_id}")
        return jsonify({"message": "Conversation ended"}), 200
    else:
        app.logger.error(f"No active conversation found for user ID: {user_id}")
        return jsonify({"error": "No active conversation found"}), 400

if __name__ == '__main__':
    app.logger.info("Starting Flask app...")
    app.run(host='0.0.0.0', port=5000, debug=True)
