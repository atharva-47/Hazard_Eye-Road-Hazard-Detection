# 🚧 Hazard_Eye – Real-Time Road Hazard Detection System

Hazard_Eye is a smart road safety system that detects real-time hazards such as potholes, speed bumps, and animals using computer vision. It integrates AI with modern web technologies to alert users and auto-report danger zones to local authorities. Designed for smart cities and intelligent transport systems, this project leverages FastAPI, React.js, and YOLOv5.

---

![Hazard_Eye Banner](assets/banner.jpg) <!-- Replace with actual banner path -->

---

## 🧠 Overview

- **Live Hazard Detection** using YOLOv5
- **Real-time Alerts** through UI and automated notifications
- **Smart Braking Simulation** logic based on object proximity
- **Map Integration** using TomTom API to visualize hazard zones
- **Automated Reporting** with email alerts and geo-tagged locations

---

## 🔧 Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Frontend    | React.js, HTML, CSS, JavaScript   |
| Backend     | FastAPI (Python)                  |
| AI Model    | YOLOv5 (PyTorch)                  |
| Mapping     | TomTom Maps API                   |
| Deployment  | Uvicorn, GitHub, Localhost        |
| Extras      | SMTP Email, Geolocation, JSON APIs|

---

## 📁 Project Structure

```bash
Hazard_Eye/
├── backend/
│   ├── main.py              # FastAPI server logic
│   ├── detect.py            # Object detection integration
│   ├── utils/               # Helper methods
│   └── config.py            # API keys, credentials
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Views
│   │   └── App.js           # Main app logic
├── media/                   # Screenshots / video samples
├── assets/                  # Images, banner, icons
├── README.md
└── requirements.txt
