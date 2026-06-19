# SyntaxErr

AI-Powered Programming Error Analyzer

## Deskripsi

SyntaxErr adalah sistem berbasis NLP/LLM yang membantu mahasiswa Teknik informatika Universitas Islam Riau terutama angkatan baru untuk memahami error pemrograman dan memperbaiki source code secara otomatis.

Sistem dapat:

- Mendeteksi jenis input (Error Message atau Source Code)
- Mendeteksi bahasa pemrograman
- Menjelaskan error dalam Bahasa Indonesia
- Memberikan solusi
- Memberikan perbaikan kode otomatis

---

## Teknologi

### Frontend

- Vue.js 3
- Axios
- Iconify

### Backend

- FastAPI
- Gemini 2.5 Flash

### AI Framework

- LangChain
- LangGraph
- LangSmith

---

## Arsitektur Sistem

User

↓

Vue.js Frontend

↓

FastAPI Backend

↓

LangGraph Workflow

↓

LangChain Prompt Pipeline

↓

Gemini LLM

↓

JSON Response

↓

Frontend

---

## Fitur

- Error Analysis
- Source Code Analysis
- Error Translation
- Solution Recommendation
- Fixed Code Generation
- Analysis History
- Copy Fixed Code

---

## Screenshot

Home :
<img width="1365" height="715" alt="image" src="https://github.com/user-attachments/assets/bb07b197-c3f4-4324-bcc7-2cfc337d6a8f" />

Result: 
<img width="1365" height="643" alt="image" src="https://github.com/user-attachments/assets/8a12609b-af18-49c2-b338-1cf62cc10c94" />

<img width="1360" height="595" alt="image" src="https://github.com/user-attachments/assets/97118996-e6f3-424d-a5e2-a0ea91272cd8" />

Trancing Langsmith :
<img width="1365" height="720" alt="image" src="https://github.com/user-attachments/assets/d9a35c11-e659-4648-aade-dffde59b5bd8" />


---

## Cara Menjalankan

### Backend
silahkan isi bagian .env.exanple untuk API dari model dan Langsmith nya.

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

---

## Author

Muhammad Aidil

Teknik Informatika

Universitas Islam Riau
