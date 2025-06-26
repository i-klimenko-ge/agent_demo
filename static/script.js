let availableTools = [];
let requiredToolNames = [];

function makeTool(tool) {
    const div = document.createElement('div');
    div.className = 'tool';
    if (tool.required) {
        div.classList.add('required');
        div.draggable = false;
    } else {
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
    }
    div.textContent = tool.label + (tool.required ? ' *' : '');
    div.dataset.name = tool.name;
    return div;
}

function setupTools() {
    const avail = document.getElementById('available-tools');
    const active = document.getElementById('tools');
    avail.innerHTML = '';
    active.innerHTML = '';

    const req = availableTools.filter(t => t.required);
    const opt = availableTools.filter(t => !t.required);

    req.forEach(t => active.appendChild(makeTool(t)));
    opt.forEach(t => avail.appendChild(makeTool(t)));

    const areas = [avail, active];
    areas.forEach(area => {
        area.addEventListener('dragover', e => e.preventDefault());
        area.addEventListener('drop', e => {
            e.preventDefault();
            const name = e.dataTransfer.getData('text/plain');
            const tool = [...document.querySelectorAll('.tool')].find(d => d.dataset.name === name);
            if (tool && !tool.classList.contains('required')) {
                area.appendChild(tool);
            }
        });
    });
}

async function fetchTools() {
    const resp = await fetch('/tools');
    const data = await resp.json();
    availableTools = data.tools;
    requiredToolNames = availableTools.filter(t => t.required).map(t => t.name);
    setupTools();
}

let ws;
let pendingQuestion = false;
let historyMarkdown = '';
let resetBtn;
let retryBtn;
let lastPayload = null;
function connect(onOpen) {
    ws = new WebSocket(`ws://${location.host}/ws`);
    if (onOpen) {
        ws.addEventListener('open', onOpen, { once: true });
    }
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
    ws.onclose = () => {
        const history = document.getElementById('history');
        historyMarkdown += '\n**[System]:** Соединение прервано. Нажмите \"Повторить\".\n';
        history.innerHTML = marked.parse(historyMarkdown);
        history.scrollTop = history.scrollHeight;
        retryBtn.disabled = false;
    };
}

function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const systemPrompt = document.getElementById('system-prompt').value;
    const extraEnabled = document.getElementById('enable-extra').checked;
    const extraPrompt = extraEnabled ? document.getElementById('extra-prompt').value : '';
    const userMsg = document.getElementById('user-msg').value;
    let tools = [...document.getElementById('tools').children].map(d => d.dataset.name);
    tools = Array.from(new Set([...tools, ...requiredToolNames]));
    lastPayload = {systemPrompt, extraPrompt, userMsg, tools};
    ws.send(JSON.stringify(lastPayload));
    document.getElementById('user-msg').value = '';
    const history = document.getElementById('history');
    historyMarkdown += `\n**User:** ${userMsg}\n`;
    history.innerHTML = marked.parse(historyMarkdown);
    pendingQuestion = false;
    retryBtn.disabled = true;
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
        retryBtn = document.getElementById('retry-btn');
        retryBtn.addEventListener('click', () => {
            if (!lastPayload) return;
            const sendPayload = () => {
                ws.send(JSON.stringify(lastPayload));
                const history = document.getElementById('history');
                historyMarkdown += `\n**User (повтор):** ${lastPayload.userMsg}\n`;
                history.innerHTML = marked.parse(historyMarkdown);
                retryBtn.disabled = true;
            };
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                connect(() => sendPayload());
            } else {
                sendPayload();
            }
        });
        resetBtn = document.getElementById('reset-btn');
        resetBtn.addEventListener('click', () => {
            if (ws) {
                ws.onclose = null;
                ws.close();
            }
            historyMarkdown = '';
            document.getElementById('history').innerHTML = '';
            lastPayload = null;
            retryBtn.disabled = true;
            connect();
        });
    });
