document.addEventListener('DOMContentLoaded', () => {
    fetch('/tools')
        .then(res => res.json())
        .then(tools => {
            const list = document.getElementById('availableTools');
            tools.forEach(t => {
                const li = document.createElement('li');
                li.textContent = t.name;
                li.draggable = true;
                li.addEventListener('click', () => moveTool(li));
                li.addEventListener('dragstart', dragStart);
                list.appendChild(li);
            });
        });

    document.getElementById('prompt2').addEventListener('click', (e) => {
        e.target.classList.toggle('active');
    });

    document.getElementById('sendBtn').addEventListener('click', sendMessage);

    const selectedTools = document.getElementById('selectedTools');
    const availableTools = document.getElementById('availableTools');

    selectedTools.addEventListener('dragover', evt => evt.preventDefault());
    selectedTools.addEventListener('drop', evt => {
        evt.preventDefault();
        const id = evt.dataTransfer.getData('text');
        const el = document.getElementById(id);
        if (el && el.parentNode !== selectedTools) {
            selectedTools.appendChild(el);
        }
    });

    availableTools.addEventListener('dragover', evt => evt.preventDefault());
    availableTools.addEventListener('drop', evt => {
        evt.preventDefault();
        const id = evt.dataTransfer.getData('text');
        const el = document.getElementById(id);
        if (el && el.parentNode !== availableTools) {
            availableTools.appendChild(el);
        }
    });
});

function dragStart(evt) {
    evt.dataTransfer.setData('text', evt.target.id);
}

function moveTool(li) {
    const selected = document.getElementById('selectedTools');
    const available = document.getElementById('availableTools');
    if (li.parentNode === available) {
        selected.appendChild(li);
    } else {
        available.appendChild(li);
    }
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value;
    const prompts = Array.from(document.querySelectorAll('#prompts .prompt.active')).map(p => p.dataset.name);
    const tools = Array.from(document.querySelectorAll('#selectedTools li')).map(li => li.textContent);

    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message, prompts, tools})
    })
    .then(res => res.json())
    .then(data => {
        const chat = document.getElementById('chat');
        data.responses.forEach(r => {
            const div = document.createElement('div');
            div.textContent = r;
            chat.appendChild(div);
        });
        chat.scrollTop = chat.scrollHeight;
    });

    input.value = '';
}
