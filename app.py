from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

TOOLS = [
    {"name": "Calculator"},
    {"name": "Weather"},
    {"name": "Search"}
]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/tools', methods=['GET'])
def get_tools():
    return jsonify(TOOLS)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    message = data.get('message', '')
    prompts = data.get('prompts', [])
    tools = data.get('tools', [])
    response = {
        'responses': [
            f"Echo: {message}",
            f"Prompts: {', '.join(prompts)}",
            f"Tools: {', '.join(tools)}"
        ]
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
