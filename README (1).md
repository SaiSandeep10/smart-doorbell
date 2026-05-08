# 🔔 Smart Doorbell with Face Recognition

> A real-time AI-powered doorbell system that detects, recognizes, and alerts you about visitors — built entirely using Computer Vision and Deep Learning.

---

## 📸 Demo Preview

```
🟢 Known Visitor  →  Green box + Name displayed + Telegram welcome message
🔴 Unknown Visitor →  Red box + Snapshot saved + Telegram photo alert
```

---

## ✨ Features

- 🎯 **Real-time Face Detection** using OpenCV Haar Cascade Classifier
- 🧠 **Face Recognition** using DeepFace + Facenet deep learning model
- 📱 **Instant Telegram Alerts** with visitor snapshot photo
- 📝 **Automatic Visitor Logging** to CSV with name, date and timestamp
- 📸 **Unknown Visitor Snapshots** saved automatically to local storage
- ⚡ **Multithreading** for smooth real-time video performance
- 🛡️ **Stability System** to prevent false detection flickering
- 🔔 **Online/Offline Notifications** via Telegram bot

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Core language |
| OpenCV | 4.13 | Face detection + Video processing |
| DeepFace | Latest | Face recognition framework |
| Facenet | - | Recognition model (Google) |
| Telegram Bot API | - | Real-time push notifications |
| NumPy | 2.4 | Array and image processing |
| Threading | Built-in | Performance optimization |
| CSV | Built-in | Visitor data logging |

---

## 📁 Project Structure

```
smart-doorbell/
│
├── known_faces/              # Photos of known people (name.jpg)
│
├── visitor_logs/
│   └── visitor_log.csv       # Auto-generated visit records
│
├── unknown_snapshots/        # Auto-saved unknown visitor photos
│
│
├── doorbell/                 # Complete doorbell system
│   └── doorbell.py           # ← Main file
│
├── requirements.txt          # All dependencies
├── .gitignore                # Files excluded from GitHub
└── README.md                 # Project documentation
```

---

## ⚙️ Installation & Setup

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/smart-doorbell.git
cd smart-doorbell
```

### Step 2 — Create virtual environment
```bash
# Create venv
python -m venv doorbell_env

# Activate (Windows)
doorbell_env\Scripts\activate

# Activate (Mac/Linux)
source doorbell_env/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Add known faces
- Add a clear front-facing photo of each person to `known_faces/`
- Name the file as the person's name
```
known_faces/
├── john.jpg
├── sarah.jpg
└── mom.jpg
```

### Step 5 — Configure Telegram Bot
1. Open Telegram → Search **@BotFather** → Send `/newbot`
2. Copy the **API Token** given
3. Search **@userinfobot** → Send `/start` → Copy your **Chat ID**
4. Update these lines in `phase4/doorbell.py`:
```python
TELEGRAM_TOKEN   = "your_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
```

---

## ▶️ Run the System

```bash
cd doorbell
python doorbell.py
```

### Expected terminal output:
```
🔔 Smart Doorbell Started!
   Stability   : 5 frames
   Logging to  : ../visitor_logs/visitor_log.csv
   Snapshots   : ../unknown_snapshots
   Telegram    : Connected ✅
   Press Q to quit
```

---

## 📊 How It Works

```
Webcam Feed (30 FPS)
        ↓
Haar Cascade → Detect all faces in frame
        ↓
DeepFace + Facenet → Compare with known_faces/
        ↓
Stability Check → Need 4/5 consistent results
        ↓
    ┌───┴───┐
  Known   Unknown
    ↓         ↓
  Green     Red Box
  Box +       +
  Name    Snapshot
    ↓    Saved 📸
  CSV       +
  Log    Telegram
    +    Alert 🚨
Telegram
Welcome ✅
```

---

## 📱 Telegram Bot Notifications

| Event | Notification |
|---|---|
| System Online | 🔔 Smart Doorbell is now Online! |
| Known Visitor | ✅ Welcome [Name]! + Date & Time |
| Unknown Visitor | 🚨 Unknown Visitor! + Snapshot Photo |
| System Offline | 🔴 Smart Doorbell is now Offline! |

> Alerts have a **30 second cooldown** to prevent spam

---

## 📋 Visitor Log Format (CSV)

```
Name,      Date,       Time,     Status
Sandeep,   2026-05-08, 09:45:23, Known
Unknown,   2026-05-08, 09:52:11, Unknown
Sandeep,   2026-05-08, 10:01:45, Known
```

---

## 🧠 Key Technical Concepts

**Face Detection vs Recognition**
- Detection → finds WHERE a face is (Haar Cascade)
- Recognition → identifies WHO the face belongs to (DeepFace)

**Facenet Model**
- Developed by Google
- Converts any face into 128 unique numbers (embedding)
- Compares embeddings to find matches
- Same tech used in Google Photos face grouping

**Stability System**
- Stores last 5 detection results
- Only updates label when 4/5 results agree
- Prevents flickering between Known/Unknown

**Multithreading**
- Main thread → captures and displays video
- Background thread → runs face recognition
- Result: smooth video + real-time recognition

---

## 🚀 Future Improvements

- [ ] Raspberry Pi 4 edge deployment
- [ ] Pi Camera Module integration
- [ ] Auto-start on system boot
- [ ] Web dashboard for visitor history
- [ ] Night vision / IR camera support
- [ ] Multiple camera support
- [ ] WhatsApp integration
- [ ] Mobile app with live feed

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Sai Sandeep**
- 📧 Email: saisandeep1300@email.com
- 🐙 GitHub: [@yourusername](https://github.com/SaiSandeep10)


---

> ⭐ If you found this project useful, please give it a star on GitHub!
