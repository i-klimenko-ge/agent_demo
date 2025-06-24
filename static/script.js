const availableTools = ["calculator", "search", "wikipedia", "weather"]; // sample tools

function makeTool(name) {
    const div = document.createElement('div');
    div.className = 'tool';
    div.textContent = name;
    div.draggable = true;
    div.addEventListener('dragstart', e => {
        e.dataTransfer.setData('text/plain', name);
    });
    div.addEventListener('click', () => {
        const parent = div.parentElement.id === 'available-tools' ? document.getElementById('tools') : document.getElementById('available-tools');
        parent.appendChild(div);
    });
    return div;
}

function setupTools() {
    const avail = document.getElementById('available-tools');
    availableTools.forEach(t => avail.appendChild(makeTool(t)));

    const areas = [document.getElementById('available-tools'), document.getElementById('tools')];
    areas.forEach(area => {
        area.addEventListener('dragover', e => e.preventDefault());
        area.addEventListener('drop', e => {
            e.preventDefault();
            const name = e.dataTransfer.getData('text/plain');
            const tool = [...document.querySelectorAll('.tool')].find(d => d.textContent === name);
            area.appendChild(tool);
        });
    });
}

let ws;
function connect() {
    ws = new WebSocket(`ws://${location.host}/ws`);
    ws.onmessage = event => {
        const history = document.getElementById('history');
        history.value += event.data;
        history.scrollTop = history.scrollHeight;
    };
}

function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const systemPrompt = document.getElementById('system-prompt').value;
    const extraEnabled = document.getElementById('enable-extra').checked;
    const extraPrompt = extraEnabled ? document.getElementById('extra-prompt').value : '';
    const userMsg = document.getElementById('user-msg').value;
    const tools = [...document.getElementById('tools').children].map(d => d.textContent);
    const payload = {systemPrompt, extraPrompt, userMsg, tools};
    ws.send(JSON.stringify(payload));
    document.getElementById('user-msg').value = '';
    const history = document.getElementById('history');
    history.value += `\nUser: ${userMsg}\n`;
}

window.addEventListener('load', () => {
    setupTools();
    connect();
    document.getElementById('send-btn').addEventListener('click', sendMessage);
});
