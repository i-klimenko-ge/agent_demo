let availableTools = [];

function makeTool(tool) {
    const div = document.createElement('div');
    div.className = 'tool';
    div.textContent = tool.label;
    div.dataset.name = tool.name;
    div.dataset.required = tool.required ? 'true' : 'false';
    div.draggable = !tool.required;
    div.addEventListener('dragstart', e => {
        if (tool.required) {
            e.preventDefault();
            return;
        }
        e.dataTransfer.setData('text/plain', tool.name);
    });
    div.addEventListener('click', () => {
        if (tool.required) return;
        const parent = div.parentElement.id === 'available-tools'
            ? document.getElementById('tools')
            : document.getElementById('available-tools');
        parent.appendChild(div);
    });
    return div;
}

function setupTools() {
    const avail = document.getElementById('available-tools');
    const selected = document.getElementById('tools');
    avail.innerHTML = '';
    selected.innerHTML = '';
    availableTools.forEach(t => {
        const div = makeTool(t);
        if (t.required) {
            selected.appendChild(div);
        } else {
            avail.appendChild(div);
        }
    });

    const areas = [document.getElementById('available-tools'), document.getElementById('tools')];
    areas.forEach(area => {
        area.addEventListener('dragover', e => e.preventDefault());
        area.addEventListener('drop', e => {
            e.preventDefault();
            const name = e.dataTransfer.getData('text/plain');
            const tool = [...document.querySelectorAll('.tool')].find(d => d.dataset.name === name);
            if (tool) {
                if (tool.dataset.required === 'true' && area.id === 'available-tools') {
                    return;
                }
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
    const tools = [...document.getElementById('tools').children].map(d => d.dataset.name);
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
