import os
import json
from groq import Groq
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from routers.analytics import top_posts, followers, account_stats, compare
from routers.system import list_accounts

router = APIRouter()

_SYSTEM = """\
You are an analytics assistant for the Threads poster system.
Participants: budimir, slava, tanya — each manages several Threads accounts.
Be concise and specific. Use tools to fetch real data.
Reply in the same language the user writes in.\
"""

_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_accounts",
            "description": "Список всех аккаунтов с участниками",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_posts",
            "description": "Топ постов по просмотрам",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                    "days": {"type": "integer", "default": 30},
                    "participant": {"type": "string", "description": "budimir, slava или tanya"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "follower_growth",
            "description": "Динамика фолловеров аккаунта",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "days": {"type": "integer", "default": 30},
                },
                "required": ["account_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "account_stats",
            "description": "Сводная статистика аккаунта: просмотры, лайки, фолловеры",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "days": {"type": "integer", "default": 7},
                },
                "required": ["account_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare",
            "description": "Сравнение всех аккаунтов по просмотрам и вовлечённости",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "default": 7},
                },
                "required": [],
            },
        },
    },
]


def _get_api_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        raise RuntimeError("GROQ_API_KEY not set")
    return key


def _call_tool(name: str, inp: dict) -> dict:
    try:
        if name == "list_accounts":
            return list_accounts()
        elif name == "top_posts":
            return top_posts(**inp)
        elif name == "follower_growth":
            return followers(**inp)
        elif name == "account_stats":
            return account_stats(**inp)
        elif name == "compare":
            return compare(**inp)
        return {"error": f"unknown tool: {name}"}
    except Exception as e:
        return {"error": str(e)}


class ChatRequest(BaseModel):
    message: str
    history: list = []


async def _stream(req: ChatRequest):
    client = Groq(api_key=_get_api_key())
    messages = (
        [{"role": "system", "content": _SYSTEM}]
        + req.history
        + [{"role": "user", "content": req.message}]
    )

    while True:
        tool_calls_acc: dict[int, dict] = {}
        full_text = ""
        finish_reason = None

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=_TOOLS,
            tool_choice="auto",
            max_completion_tokens=2048,
            stream=True,
        )

        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta
            finish_reason = choice.finish_reason or finish_reason

            if delta.content:
                full_text += delta.content
                yield f"data: {json.dumps({'type': 'text', 'text': delta.content})}\n\n"

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_acc:
                        tool_calls_acc[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc.id:
                        tool_calls_acc[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls_acc[idx]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_calls_acc[idx]["arguments"] += tc.function.arguments

        if finish_reason == "tool_calls" and tool_calls_acc:
            # Add assistant message with tool_calls
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["arguments"]},
                    }
                    for tc in tool_calls_acc.values()
                ],
            })
            # Execute tools and add results
            for tc in tool_calls_acc.values():
                yield f"data: {json.dumps({'type': 'tool', 'name': tc['name']})}\n\n"
                try:
                    inp = json.loads(tc["arguments"] or "{}")
                except json.JSONDecodeError:
                    inp = {}
                result = _call_tool(tc["name"], inp)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })
        else:
            new_history = req.history + [
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": full_text},
            ]
            yield f"data: {json.dumps({'type': 'done', 'history': new_history})}\n\n"
            break


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    return StreamingResponse(_stream(req), media_type="text/event-stream")


@router.get("/")
def landing():
    return HTMLResponse(_HTML)


_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Threads Analytics</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f0f0f;
    color: #e0e0e0;
    height: 100vh;
    display: flex;
    flex-direction: column;
}
header {
    padding: 16px 24px;
    border-bottom: 1px solid #1e1e1e;
    display: flex;
    align-items: center;
    gap: 12px;
}
header h1 { font-size: 16px; font-weight: 600; color: #fff; }
header span { font-size: 13px; color: #555; }
#chat {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.msg {
    max-width: 78%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-word;
}
.msg.user {
    background: #1c1c3a;
    border: 1px solid #2e2e5a;
    align-self: flex-end;
    color: #c8d8ff;
}
.msg.assistant {
    background: #181818;
    border: 1px solid #252525;
    align-self: flex-start;
    color: #e0e0e0;
}
.tool-hint {
    font-size: 12px;
    color: #4a9eff;
    align-self: flex-start;
    padding: 4px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.dot {
    width: 6px; height: 6px;
    background: #4a9eff;
    border-radius: 50%;
    animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:.2 } }
#form {
    padding: 16px 24px;
    border-top: 1px solid #1e1e1e;
    display: flex;
    gap: 10px;
    align-items: flex-end;
}
#input {
    flex: 1;
    background: #181818;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 12px 16px;
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
    outline: none;
    resize: none;
    max-height: 120px;
    line-height: 1.5;
}
#input:focus { border-color: #4a9eff; }
#input::placeholder { color: #444; }
button {
    background: #4a9eff;
    border: none;
    border-radius: 12px;
    padding: 12px 18px;
    color: #fff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
}
button:disabled { opacity: 0.4; cursor: default; }
button:hover:not(:disabled) { background: #3a8eef; }
</style>
</head>
<body>
<header>
    <h1>Threads Analytics</h1>
    <span>budimir · slava · tanya</span>
</header>
<div id="chat">
    <div class="msg assistant">Hi! Ask me about account stats — top posts, follower growth, participant comparison.</div>
</div>
<form id="form" onsubmit="send(event)">
    <textarea id="input" placeholder="Ask about stats..." rows="1"
        oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"
        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();document.getElementById('form').dispatchEvent(new Event('submit',{cancelable:true}))}">
    </textarea>
    <button id="btn" type="submit">Send</button>
</form>
<script>
let history = [];

function addMsg(role, text) {
    const chat = document.getElementById('chat');
    const el = document.createElement('div');
    el.className = 'msg ' + role;
    el.textContent = text;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
    return el;
}

function addToolHint(name) {
    const chat = document.getElementById('chat');
    const el = document.createElement('div');
    el.className = 'tool-hint';
    el.innerHTML = '<div class="dot"></div>' + name;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
    return el;
}

async function send(e) {
    e.preventDefault();
    const input = document.getElementById('input');
    const btn = document.getElementById('btn');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    input.style.height = 'auto';
    btn.disabled = true;

    addMsg('user', msg);
    const aiEl = addMsg('assistant', '');
    let toolEl = null;
    let fullText = '';

    const res = await fetch('/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg, history}),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';

    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        buf += decoder.decode(value, {stream: true});
        const lines = buf.split('\\n');
        buf = lines.pop();
        for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const data = JSON.parse(line.slice(6));
            if (data.type === 'text') {
                if (toolEl) { toolEl.remove(); toolEl = null; }
                fullText += data.text;
                aiEl.textContent = fullText;
                document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
            } else if (data.type === 'tool') {
                toolEl = addToolHint(data.name);
            } else if (data.type === 'done') {
                if (toolEl) { toolEl.remove(); toolEl = null; }
                history = data.history;
            }
        }
    }

    btn.disabled = false;
    input.focus();
}
</script>
</body>
</html>"""
