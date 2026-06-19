import os
import json

from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "SyntaxErr"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

prompt_template = PromptTemplate.from_template(
"""
Kamu adalah AI Programming Assistant untuk mahasiswa Indonesia.

Analisis input berikut:

{content}

Tugas:

1. Tentukan apakah input adalah:
   - error_message
   - source_code

2. Deteksi bahasa pemrograman.

3. Identifikasi nama error.

4. Terjemahkan error ke Bahasa Indonesia.

5. Berikan penjelasan dalam Bahasa Indonesia yang mudah dipahami mahasiswa.

6. Berikan solusi dalam Bahasa Indonesia.

7. Jika memungkinkan, berikan kode yang sudah diperbaiki.

ATURAN:

- Semua output WAJIB menggunakan Bahasa Indonesia.
- Jangan gunakan Bahasa Inggris kecuali nama error.
- explanation maksimal 3 kalimat.
- solution WAJIB berupa array string.
- Jangan gunakan object JSON di dalam solution.
- Jangan gunakan field step atau description.
- fixed_code berisi kode yang telah diperbaiki jika memungkinkan.

Contoh yang BENAR:

"solution": [
    "Tambahkan tanda titik dua (:).",
    "Perbaiki indentasi kode."
]

Contoh yang SALAH:

"solution": [
    {{
        "step": 1,
        "description": "Tambahkan titik dua."
    }}
]

Kembalikan HANYA JSON valid.

Format:

{{
    "input_type": "",
    "language": "",
    "error_name": "",
    "translation": "",
    "explanation": "",
    "solution": [],
    "fixed_code": ""
}}
"""
)

chain = prompt_template | llm


def analyze_content(content: str):

    response = chain.invoke({
        "content": content
    })

    raw_text = response.content.strip()

    # Membersihkan markdown Gemini
    raw_text = raw_text.replace("```json", "")
    raw_text = raw_text.replace("```", "")
    raw_text = raw_text.strip()

    try:

        parsed = json.loads(raw_text)

        # Jika solution berupa string
        if isinstance(parsed.get("solution"), str):
            parsed["solution"] = [parsed["solution"]]

        # Jika Gemini mengirim object dalam solution
        if isinstance(parsed.get("solution"), list):

            cleaned_solution = []

            for item in parsed["solution"]:

                if isinstance(item, dict):
                    cleaned_solution.append(
                        item.get("description", str(item))
                    )
                else:
                    cleaned_solution.append(
                        str(item)
                    )

            parsed["solution"] = cleaned_solution

        return parsed

    except Exception as e:

        return {
            "input_type": "unknown",
            "language": "",
            "error_name": "ParsingError",
            "translation": "Gagal memproses respons AI",
            "explanation": str(e),
            "solution": [
                "Periksa format respons yang dikembalikan AI."
            ],
            "fixed_code": "",
            "raw_response": raw_text
        }