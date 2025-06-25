let availableTools = [];

function makeTool(tool) {
    const div = document.createElement('div');
    div.className = 'tool';
    div.textContent = tool.label;
    div.dataset.name = tool.name;
    div.draggable = true;
    div.addEventListener('dragstart', e => {
        e.dataTransfer.setData('text/plain', tool.name);
    });
    div.addEventListener('click', () => {
        const parent = div.parentElement.id === 'available-tools'
            ? document.getElementById('tools')
            : document.getElementById('available-tools');
        parent.appendChild(div);
    });
    return div;
}

function setupTools() {
    const avail = document.getElementById('available-tools');
    avail.innerHTML = '';
    availableTools.forEach(t => avail.appendChild(makeTool(t)));

    const areas = [document.getElementById('available-tools'), document.getElementById('tools')];
    areas.forEach(area => {
        area.addEventListener('dragover', e => e.preventDefault());
        area.addEventListener('drop', e => {
            e.preventDefault();
            const name = e.dataTransfer.getData('text/plain');
            const tool = [...document.querySelectorAll('.tool')].find(d => d.dataset.name === name);
            if (tool) {
                area.appendChild(tool);
            }
        });
    });
}

async function fetchTools() {
    const resp = await fetch('/tools');
    const data = await resp.json();
    availableTools = data.tools;
    setupTools();
}

let ws;
let pendingQuestion = false;
let historyMarkdown = '';
function connect() {
    ws = new WebSocket(`ws://${location.host}/ws`);
    ws.onmessage = event => {
        const history = document.getElementById('history');
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'question') {
                historyMarkdown += `\n**[Agent asks]:** ${data.text}\n`;
                history.innerHTML = marked.parse(historyMarkdown);
                history.scrollTop = history.scrollHeight;
                pendingQuestion = true;
                return;
            }
        } catch (e) {}
        historyMarkdown += event.data;
        history.innerHTML = marked.parse(historyMarkdown);
        history.scrollTop = history.scrollHeight;
    };
}

function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const systemPrompt = document.getElementById('system-prompt').value;
    const extraEnabled = document.getElementById('enable-extra').checked;
    const extraPrompt = extraEnabled ? document.getElementById('extra-prompt').value : '';
    const userMsg = document.getElementById('user-msg').value;
    const tools = [...document.getElementById('tools').children].map(d => d.dataset.name);
    const payload = {systemPrompt, extraPrompt, userMsg, tools};
    ws.send(JSON.stringify(payload));
    document.getElementById('user-msg').value = '';
    const history = document.getElementById('history');
    historyMarkdown += `\n**User:** ${userMsg}\n`;
    history.innerHTML = marked.parse(historyMarkdown);
    pendingQuestion = false;
}

function toggleExtraPrompt() {
    const cb = document.getElementById('enable-extra');
    const area = document.getElementById('extra-prompt');
    if (cb.checked) {
        area.classList.remove('inactive');
        area.disabled = false;
    } else {
        area.classList.add('inactive');
        area.disabled = true;
    }
}

    window.addEventListener('load', () => {
        fetchTools();
        connect();
        toggleExtraPrompt();
        document.getElementById('send-btn').addEventListener('click', sendMessage);
        document.getElementById('user-msg').addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
        document.getElementById('enable-extra').addEventListener('change', toggleExtraPrompt);
    });
