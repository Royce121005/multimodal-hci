# 🖐️ Multimodal HCI Gesture Interface

A free, offline, open-source desktop control system using hand gestures, eye tracking, and voice commands — built for accessibility.

**Target Users:** Motor-impaired users  
**Publication Target:** ACM ASSETS / IEEE SMC  
**Hardware Required:** Standard laptop webcam + microphone

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10 | Core language |
| MediaPipe | 0.10.9 | Hand landmarks + Eye tracking |
| OpenCV | Latest | Webcam feed processing |
| PyAutoGUI | Latest | Mouse/keyboard control |
| faster-whisper | Latest | Local voice recognition (Week 2) |
| scikit-learn | Latest | Gesture classifier MLP (Week 5) |
| Electron + React | Latest | UI dashboard (Week 6) |

---

## ✋ Gesture Reference

| # | Gesture | Hand Shape | Action | Trigger |
|---|---|---|---|---|
| 1 | ☝️ Index only | Index finger up, others down | Move cursor | Instant |
| 2 | ✌️ Peace (brief) | Index + middle up | Scroll up | Instant |
| 3 | 🤟 Three fingers | Index + middle + ring up | Scroll down | Instant |
| 4 | ✊ Fist | All fingers curled, no pinch | Left click | Hold 3 frames + 1.0s cooldown |
| 5 | 👋 Open hand | All 4 fingers extended | Drag mode | Hold 3 frames |
| 6 | 👌 Pinch | Thumb + index tips close (<0.07), others curled | Right click | Hold 3 frames + 1.0s cooldown |
| 7 | ✌️ Peace (held) | Index + middle up, sustained | Double click | Hold 3 frames + 1.2s cooldown |
| 8 | 🤙 Pinky only | Pinky up, all others down | Press ESC | Hold 3 frames + 1.5s cooldown |

> **Note:** Gestures 2 and 7 use the same hand shape — brief = scroll up, sustained 3 frames = double click.  
> **Note:** Gestures 4 and 6 are both closed fists — pinch distance `< 0.07` = right click, otherwise = left click.

---

## ⚙️ Performance Settings

| Setting | Value |
|---|---|
| Resolution | 640 × 480 |
| MediaPipe frame skip | Every 2nd frame |
| Camera buffer size | 1 (eliminates stale lag) |
| Cursor smoothing | EMA, factor 0.2 |
| Scroll speed | 40 units |
| Detection confidence | 0.8 |
| Tracking confidence | 0.8 |
| Known FPS limit | 10–11 FPS (hardware cap) |

---

## 🚀 Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/Royce121005/multimodal-hci.git
cd multimodal-hci
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install mediapipe==0.10.9
pip install opencv-python
pip install pyautogui
pip install numpy
```

### 4. Run
```bash
python gesture_module.py
```

Press `q` to quit.

---

## 📅 6-Week Roadmap

| Week | Module | Status |
|---|---|---|
| Week 1 | Gesture Module | ✅ Complete |
| Week 2 | Voice Module | 🔲 Upcoming |
| Week 3 | Eye Tracking Module | 🔲 Upcoming |
| Week 4 | Fusion Engine | 🔲 Upcoming |
| Week 5 | Custom Gesture Training | 🔲 Upcoming |
| Week 6 | Evaluation + Demo + Report | 🔲 Upcoming |

---

## 📁 Project Structure

```
multimodal-hci/
├── gesture_module.py     # Week 1 — Hand gesture control
├── voice_module.py       # Week 2 — Voice command control (coming)
├── eye_module.py         # Week 3 — Eye tracking control (coming)
├── fusion_engine.py      # Week 4 — Multimodal fusion (coming)
├── README.md
└── .gitignore
```

---

## 📊 Progress

```
Week 1  ██████████████████████  100% ✅
Week 2  ░░░░░░░░░░░░░░░░░░░░░░    0%
Week 3  ░░░░░░░░░░░░░░░░░░░░░░    0%
Week 4  ░░░░░░░░░░░░░░░░░░░░░░    0%
Week 5  ░░░░░░░░░░░░░░░░░░░░░░    0%
Week 6  ░░░░░░░░░░░░░░░░░░░░░░    0%
Overall ████░░░░░░░░░░░░░░░░░░  ~17%
```

---

## 👤 Author

**Royce D'monte**  
GitHub: [@Royce121005](https://github.com/Royce121005)

---

## 📄 License

MIT License — free to use, modify, and distribute.
