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

Tambahkan screenshot aplikasi di sini.

---

## Cara Menjalankan

### Backend

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
