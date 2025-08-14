# 📲 WhatsApp Bulk Sender & AI Chatbot (OpenAI + WhatsApp Cloud API)

This project allows you to:

1. **Send bulk WhatsApp messages** to contacts from an Excel file using the WhatsApp Cloud API.
2. **Automatically reply to incoming messages** using an AI assistant powered by OpenAI GPT.
3. Maintain ongoing conversations with contacts who reply to your initial message.

---

## 🚀 Features
- Read phone numbers from an Excel file (`contacts.xlsx`).
- Send an approved WhatsApp **template message** to all contacts.
- Listen for incoming replies via a Flask **webhook**.
- Generate responses using **OpenAI GPT**.
- Send GPT replies back to the user in real-time.

---

## 📂 Project Structure
```
app.py             # Main application file (bulk sender + webhook)
contacts.xlsx      # Excel file with your contact list
.env               # Environment variables (API keys, tokens, IDs)
requirements.txt   # Python dependencies
README.md          # Documentation
```

---

## 📋 Requirements

### 1️⃣ WhatsApp Cloud API Setup
- Create a [Meta for Developers](https://developers.facebook.com/) account.
- Create a WhatsApp Business App.
- Get your **Phone Number ID** and **Permanent Access Token** from the dashboard.
- Ensure you have an **approved template** (e.g., `hello_world`).
- If your app is in **Development Mode**:
  - Add all recipient numbers in **API Setup → Add Recipients**.
  - Verify them by entering the 6-digit code received on WhatsApp.

### 2️⃣ OpenAI API Key
- Create an account at [OpenAI](https://platform.openai.com/).
- Generate an **API Key**.

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```
META_TOKEN=your_meta_access_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_webhook_verify_token
OPENAI_API_KEY=your_openai_api_key
```

---

## 📊 Excel File Format

Name the file `contacts.xlsx` and include a `phone` column:

| name   | phone        |
|--------|--------------|
| Sachin | 918004466229 |
| John   | 14151234567  |

**Notes:**
- Numbers must be in international format without `+`.
- In development mode, numbers must be added to your allowed test list.

---

## ▶️ Running the App

### Step 1: Start Ngrok (for Webhook)
```bash
ngrok http 5000
```
Copy the HTTPS forwarding URL from Ngrok.

### Step 2: Set Webhook in Meta Dashboard
- Go to **WhatsApp → Configuration** in the Meta dashboard.
- Set the webhook URL:  
  ```
  https://<ngrok-id>.ngrok-free.app/webhook
  ```
- Use the **Verify Token** from `.env`.
- Subscribe to the `messages` field for `whatsapp_business_account`.

### Step 3: Run the Application
```bash
python app.py
```

---

## 💬 How It Works
1. On startup, the bot reads `contacts.xlsx` and sends your approved template (`hello_world`) to each number.
2. When a contact replies, Meta forwards the message to your webhook.
3. The webhook sends the message to OpenAI GPT for processing.
4. GPT’s reply is sent back to the contact via WhatsApp.

---

## 🛠 requirements.txt
```
flask
requests
python-dotenv
pandas
openpyxl
openai
```

---

## 📌 Important Notes
- **Development Mode**: You can only message numbers added to your allowed list.
- **24-Hour Rule**: You can send free-form messages only within 24 hours of the user's last message. Outside this window, you must use a template.
- **Template Approval**: All templates must be approved before use.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing
Pull requests are welcome! If you find a bug or have a feature request, please open an issue.

---

## 📧 Support
- [Meta for Developers Support](https://developers.facebook.com/support/)
- [OpenAI Help Center](https://help.openai.com/)
