# 📚 Smart Study Assistant AI

An AI-powered web application that helps students learn faster by generating summaries, key points, quizzes, flashcards, and study plans from any text.

---

## 🚀 Features

- 📝 AI-generated summaries (Easy / Medium / Hard)
- 🎯 Key points extraction
- ❓ Revision questions
- 💡 Study tips
- 🔗 Related topics
- 📊 Confidence score & readability analysis
- 📅 Personalized study plan
- 🧠 Flashcards generation
- 📝 Quiz generation
- 📊 Dashboard with study sessions

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **AI Model:** Google Gemini API
- **Deployment:** Render / Railway

---

smart-study-assistant/
│
├── app/
│ ├── main.py
│ ├── utils.py
│ ├── templates/
│ │ ├── index.html
│ │ ├── advanced.html
│ │ └── dashboard.html
│
├── advanced_features.py
├── requirements.txt
├── .env
├── Dockerfile
└── README.md


---

## ⚙️ Installation (Local Setup)

### 1. Clone the repository

git clone https://github.com/YaparlaBhargavi/smart-study-assistant.git

cd smart-study-assistant


### 2. Create virtual environment

python -m venv venv
venv\Scripts\activate # Windows


### 3. Install dependencies

pip install -r requirements.txt


### 4. Add Environment Variables
Create `.env` file:


GEMINI_API_KEY=your_api_key_here
PORT=8080
DEBUG=True


---

## ▶️ Run the App


python app/main.py


Open:

http://127.0.0.1:8080


---

## 🌐 Deployment (Render)

1. Push code to GitHub  
2. Go to https://render.com  
3. Create Web Service  
4. Use:


Build Command: pip install -r requirements.txt
Start Command: python app/main.py


5. Add environment variable:

GEMINI_API_KEY=your_api_key


---

## ⚠️ Security Note

- Never expose your API key in code
- Always store it in `.env`
- Regenerate key if leaked

---

## 📸 Screenshots

- Study Page
- Advanced Features
- Dashboard

<img width="1904" height="871" alt="image" src="https://github.com/user-attachments/assets/f4fca03c-784f-4afb-ae03-582656f78338" />
<img width="1883" height="857" alt="image" src="https://github.com/user-attachments/assets/ee87f6a8-1509-4755-b2a9-e5674d061832" />
<img width="1897" height="863" alt="image" src="https://github.com/user-attachments/assets/9a14457b-ea98-4c05-bdc3-45ee113a88f7" />
<img width="1902" height="858" alt="image" src="https://github.com/user-attachments/assets/21847e2f-f8c1-4450-9e8d-d3727263c09b" />
<img width="1313" height="857" alt="image" src="https://github.com/user-attachments/assets/d2ec62d2-9a99-496c-80fc-b272608f8533" />



---

## 📂 Project Structure
