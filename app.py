# bulk_send.py — WhatsApp Cloud + local Mistral-7B (LangChain)
# Simple: prints IN/OUT, no extra logging. Fixes double "hello_world" by disabling Flask reloader.

import os
import sys
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading

# ================== ENV ==================
load_dotenv()
META_TOKEN      = os.getenv("META_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN", "testtoken")
TEMPLATE_NAME   = os.getenv("TEMPLATE_NAME", "hello_world")
TEMPLATE_LANG   = os.getenv("TEMPLATE_LANG", "en_US")

# Ensure prints show immediately
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

# ================== FLASK ==================
app = Flask(__name__)

# ================== LANGCHAIN (local llama.cpp) ==================
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

print("[MODEL] Loading Mistral-7B via LangChain (llama.cpp)...", flush=True)
lc_llm = LlamaCpp(
    model_path="mistral-7b-instruct-v0.2.Q4_K_M.gguf",  # your local model
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0,         # set >0 if you have GPU offload
    temperature=0.7,
    max_tokens=256,
    stop=["User:", "Assistant:"],
)
print("[MODEL] Mistral loaded successfully!", flush=True)

PROMPT = PromptTemplate(
    input_variables=["history", "user"],
    template="You are a friendly, concise WhatsApp assistant.\n{history}\nUser: {user}\nAssistant:",
)
chain = LLMChain(llm=lc_llm, prompt=PROMPT, verbose=False)

# Tiny per-sender memory
user_history = {}  # sender -> str buffer

def generate_reply(sender: str, user_text: str) -> str:
    hist = user_history.get(sender, "").strip()
    try:
        reply = chain.predict(history=hist, user=user_text).strip()
    except Exception as e:
        print("[LLM ERROR]", e, flush=True)
        reply = "Sorry, I hit a small snag generating that. Mind rephrasing?"
    new_hist = (hist + f"\nUser: {user_text}\nAssistant: {reply}").strip()
    user_history[sender] = new_hist[-4000:]  # trim to keep prompt small
    return reply

# ================== WhatsApp send ==================
def send_template_message(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": str(to),
        "type": "template",
        "template": {"name": TEMPLATE_NAME, "language": {"code": TEMPLATE_LANG}},
    }
    print(f"[client {to}]: Sending {TEMPLATE_NAME}", flush=True)
    r = requests.post(url, headers=headers, json=payload)
    print(f"[TEMPLATE RESPONSE] {r.status_code}: {r.text}", flush=True)

def send_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": str(to), "type": "text", "text": {"body": text}}
    print(f"[client {to}]: {text}", flush=True)  # OUTGOING
    r = requests.post(url, headers=headers, json=payload)
    print(f"[MESSAGE RESPONSE] {r.status_code}: {r.text}", flush=True)

# ================== Bulk send ==================
def send_bulk_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        phone = row["phone"]
        send_template_message(phone)

# ================== Webhook verify ==================
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        print("[WEBHOOK] Verified", flush=True)
        return challenge
    return "Invalid token", 403

# ================== Webhook POST ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    threading.Thread(target=process_incoming, args=(data,), daemon=True).start()
    return jsonify(status="ok"), 200

# ================== Incoming processing ==================
def extract_user_text(msg: dict) -> str:
    t = msg.get("type")
    if t == "text" and "text" in msg:
        return msg["text"].get("body", "")
    if t == "interactive" and "interactive" in msg:
        it = msg["interactive"]; itype = it.get("type")
        if itype == "button_reply":
            br = it.get("button_reply", {}); return br.get("title") or br.get("id") or ""
        if itype == "list_reply":
            lr = it.get("list_reply", {});  return lr.get("title")  or lr.get("id") or ""
    return f"[{t or 'unknown'}]"

def process_incoming(data):
    try:
        value = data["entry"][0]["changes"][0]["value"]

        # Handle messages FIRST (even if statuses also present)
        if "messages" in value:
            msg = value["messages"][0]
            sender = msg.get("from")
            user_text = extract_user_text(msg)

            # INCOMING
            print(f"[customer {sender}]: {user_text}", flush=True)

            # Generate reply and send
            reply = generate_reply(sender, user_text)
            send_message(sender, reply)

        # (Optionally inspect statuses afterward; no early return)
        # if "statuses" in value:
        #     print("[WEBHOOK] status update", flush=True)

    except Exception as e:
        print("[ERROR]", e, flush=True)

# ================== Main ==================
if __name__ == "__main__":
    # Step 1: Send initial messages from Excel (runs ONCE)
    send_bulk_from_excel("contacts.xlsx")

    # Step 2: Start webhook — IMPORTANT: disable reloader to prevent double sends
    print("[SERVER] Starting webhook on port 5000...", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
''