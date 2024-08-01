from flask import Flask, request, render_template, redirect, url_for
from openai import OpenAI
import uuid

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)
app = Flask(__name__)

# Store sessions and their chat histories
sessions = {}

@app.route('/')
def home():
    # Get the session ID from the request args
    session_id = request.args.get('session_id', None)
    
    if not session_id or session_id not in sessions:
        # If no session or invalid session, create a new one
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"name": "New Chat", "history": []}

    chat_history = sessions[session_id]["history"]
    return render_template('index.html', chat_history=chat_history, session_id=session_id, sessions=sessions)

@app.route('/get_response', methods=['POST'])
def get_response():
    session_id = request.form.get('session_id')
    
    if not session_id or session_id not in sessions:
        return redirect(url_for('home'))

    if 'reset_chat' in request.form:
        # Reset the chat history for the session
        sessions[session_id]["history"].clear()
    else:
        user_input = request.form.get('user_input')
        if not user_input:
            return redirect(url_for('home', session_id=session_id))
        
        chat_history = sessions[session_id]["history"]
        
        if not chat_history:
            # Set the initial name based on the first user input
            sessions[session_id]["name"] = user_input
        
        chat_history.append({"role": "user", "content": user_input})
        
        response_text = ""
        completion = client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
        
        chat_history.append({"role": "assistant", "content": response_text})
    
    return render_template('index.html', chat_history=chat_history, session_id=session_id, sessions=sessions)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    # Create a new chat session
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"name": "New Chat", "history": []}
    return redirect(url_for('home', session_id=session_id))

@app.route('/delete_chat/<session_id>', methods=['POST'])
def delete_chat(session_id):
    if session_id in sessions:
        del sessions[session_id]
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
