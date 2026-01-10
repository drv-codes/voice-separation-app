# 🎧 Voice Separation Web Application

A web application that allows users to upload a multi-speaker audio file, select a specific speaker, and extract only the chosen voice using AI-based speaker diarization.

This project focuses on building a **real-world AI system** by integrating open-source machine learning models into a full-stack application.

---

## 🚀 Project Overview

Many audio recordings such as interviews, meetings, podcasts, or calls contain multiple speakers. Extracting only one speaker’s voice manually is time-consuming.

This application automates that process by:
1. Detecting multiple speakers in an audio file
2. Allowing the user to choose a speaker
3. Returning a clean audio file containing only the selected voice

---

## 🧠 How It Works

1. **User uploads audio** via the frontend
2. **Backend processes the audio** using speaker diarization
3. Short **speaker preview clips** are generated
4. User selects the desired speaker
5. Backend **extracts only that speaker’s voice**
6. Final cleaned audio is returned to the user

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- pyannote.audio (speaker diarization)
- pydub / FFmpeg (audio processing)

### Frontend
- HTML, CSS, JavaScript *(or React – planned)*

---

## 📦 Project Structure

voice-separation-app/
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── diarization.py
│ │ ├── audio_utils.py
│ └── requirements.txt
├── frontend/
└── README.md

---

## 🔍 Speaker Diarization

This project uses the open-source **pyannote.audio** library for speaker diarization.

> ⚠️ Note:  
> The diarization model itself is **not developed by me**.  
> My contribution lies in **system design, backend APIs, audio processing logic, and frontend integration**.

---

## 🔐 Privacy & Security

- No API keys or tokens are stored in the repository
- Environment variables are used for sensitive credentials
- Uploaded files are processed temporarily and not retained

---

## 📈 Use Cases

- Podcast editing
- Interview cleanup
- Call recording analysis
- Dataset preparation for voice models

---

## 🧪 Current Status

- [x] Project structure created
- [x] Backend planning completed
- [ ] FastAPI backend implementation
- [ ] Frontend interface
- [ ] Deployment

---

## 📌 Future Improvements

- Real-time audio processing
- Support for more than two speakers
- Noise reduction & enhancement
- Cloud deployment (Render / Hugging Face Spaces)

---

## 👤 Author

Built by **[Dhruv Sharma]**

LinkedIn: *(www.linkedin.com/in/dhruv-sharma-4a9501393)*  
GitHub: *(this profile)*

---

## 📜 License

This project is licensed under the **MIT License**.


