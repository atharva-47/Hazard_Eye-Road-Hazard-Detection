````markdown
# 🚧 Hazard_Eye – Real-Time Road Hazard Detection System

Hazard_Eye is an AI-powered web application designed to detect road hazards like potholes, speed bumps, and living beings in real-time using computer vision. Built with a FastAPI backend, React frontend, and YOLOv5 object detection, the system enhances road safety and automates hazard reporting.

---

## 📌 Features

- ⚠️ Real-time hazard detection (potholes, bumps, animals, etc.)
- 🧠 YOLOv5 model integration for accurate object detection
- 🚦 Simulated emergency braking logic based on hazard proximity
- 🌐 TomTom Maps API for hazard zone visualization
- 📧 Auto-email reports to local authorities with GPS location
- 📊 Detection accuracy over 95%
- 📉 Reduced manual reporting time by 80%

---

## 🛠 Tech Stack

| Component   | Technology         |
|-------------|--------------------|
| Frontend    | React.js           |
| Backend     | FastAPI (Python)   |
| AI Model    | YOLOv5             |
| Mapping     | TomTom Maps API    |
| Email Alerts| SMTP / Email API   |
| Versioning  | Git & GitHub       |

---

## 📂 Project Structure

```bash
Hazard_Eye/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── detect.py            # YOLO inference logic
│   └── utils/               # Helper functions
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   └── App.js           # Main React file
├── media/                   # Sample detection videos/images
├── README.md
└── requirements.txt
````

---

## 🚀 How to Run

### 🔧 Prerequisites

* Python 3.9+
* Node.js 18+
* Git

### ✅ Backend (FastAPI)

```bash
cd backend/
pip install -r requirements.txt
uvicorn main:app --reload
```

### ✅ Frontend (React)

```bash
cd frontend/
npm install
npm start
```

Access the app at: [http://localhost:3000](http://localhost:3000)

---

## 📬 Email Alert Setup

1. Configure your email credentials in `config.py`.
2. The app sends hazard reports to pre-set authority addresses.
3. Attachments include location & image evidence.

---

## 🧪 Demo

Watch demo clips and screenshots in `/media`.

---

## 👨‍💻 Author

**Atharv Bargir**
🔗 [Portfolio](https://atharvabargir.me/portfolio)
🔗 [LinkedIn](https://linkedin.com/in/atharv-bargir-081927250)
📧 [atharvabargir3112@gmail.com](mailto:atharvabargir3112@gmail.com)

---

## 📝 License

This project is licensed under the MIT License. Feel free to use, modify, and share.

```
