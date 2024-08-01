from flask import Flask, request, render_template
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

app = Flask(__name__)

chat_history = []

@app.route('/')
def home():
    return render_template('index.html', chat_history=chat_history)

@app.route('/get_response', methods=['POST'])
def get_response():
    if 'reset_chat' in request.form:
        # Reset the chat history
        chat_history.clear()
        return render_template('index.html', chat_history=chat_history)
    
    # Handle user input if present
    user_input = request.form.get('user_input')
    if user_input:
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
    
    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)
