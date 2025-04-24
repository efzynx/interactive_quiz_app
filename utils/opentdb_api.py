# File: utils/opentdb_api.py

import requests
import random
from typing import List, Dict, Optional
# Pastikan Anda punya file ini atau fungsi decode ada di tempat lain
from utils.helpers import decode_html_entities

OPENTDB_BASE_URL = "https://opentdb.com/api.php"
# Mapping ID Kategori OpenTDB ke Nama
OPENTDB_CATEGORIES = {
    9: "General Knowledge",
    10: "Entertainment: Books",
    11: "Entertainment: Film",
    12: "Entertainment: Music",
    13: "Entertainment: Musicals & Theatres",
    14: "Entertainment: Television",
    15: "Entertainment: Video Games",
    16: "Entertainment: Board Games",
    17: "Science & Nature",
    18: "Science: Computers",
    19: "Science: Mathematics",
    20: "Mythology",
    21: "Sports",
    22: "Geography",
    23: "History",
    24: "Politics",
    25: "Art",
    26: "Celebrities",
    27: "Animals",
    28: "Vehicles",
    29: "Entertainment: Comics",
    30: "Science: Gadgets",
    31: "Entertainment: Japanese Anime & Manga",
    32: "Entertainment: Cartoon & Animations",
}

def fetch_questions(amount: int = 10, category_id: Optional[int] = None, difficulty: Optional[str] = None) -> List[Dict]:
    """Mengambil pertanyaan dari Open Trivia Database API."""
    params = {"amount": amount, "type": "multiple", "encode": "url3986"} # Paksa tipe multiple choice & encoding URL
    if category_id and category_id in OPENTDB_CATEGORIES:
        params["category"] = category_id
    if difficulty and difficulty in ["easy", "medium", "hard"]:
        params["difficulty"] = difficulty

    print(f"Fetching from OpenTDB with params: {params}") # Logging

    try:
        response = requests.get(OPENTDB_BASE_URL, params=params, timeout=15) # Tambah timeout
        response.raise_for_status() # Raise exception untuk bad status codes (4xx atau 5xx)
        data = response.json()

        # Cek response code dari API
        if data.get("response_code") != 0:
            print(f"API Error from OpenTDB: Code {data.get('response_code')}. Params: {params}")
            return [] # Kembalikan list kosong jika ada error dari API

        processed_questions = []
        # Buat ID unik dasar untuk batch ini (akan disempurnakan di service)
        batch_prefix = f"q_{random.randint(1000,9999)}"

        # Loop melalui hasil dari API
        for idx, item in enumerate(data.get("results", [])):
            # Validasi dasar data soal
            if not all(k in item for k in ('category', 'difficulty', 'question', 'correct_answer', 'incorrect_answers')):
                 print(f"Warning: Skipping incomplete question data: {item}")
                 continue

            # --- PERBAIKAN UTAMA DI SINI ---
            # 1. Ambil NAMA Kategori Langsung dari API dan decode
            category_name_raw = item.get("category", "Unknown Category")
            decoded_category_name = decode_html_entities(str(category_name_raw))

            # 2. Decode opsi dan jawaban benar
            options_raw = item.get("incorrect_answers", []) + [item.get("correct_answer", "")]
            decoded_options = [decode_html_entities(str(opt)) for opt in options_raw]
            decoded_correct_answer = decode_html_entities(str(item.get("correct_answer")))

            # Acak urutan pilihan jawaban
            random.shuffle(decoded_options)

            # Susun dictionary soal yang sudah diproses
            processed_question = {
                # Buat ID awal yang unik dalam batch ini
                "id": f"{batch_prefix}_{idx}",
                # TIDAK menyertakan 'category_id' karena API tidak memberikannya di sini
                "category_name": decoded_category_name, # Gunakan nama yang sudah didecode
                "difficulty": item.get("difficulty", "unknown"),
                "question": decode_html_entities(str(item.get("question", ""))), # Decode pertanyaan
                "options": decoded_options, # Gunakan opsi yang sudah didecode dan diacak
                "correct_answer": decoded_correct_answer, # Gunakan jawaban yang sudah didecode
            }
            processed_questions.append(processed_question)
            # --- AKHIR PERBAIKAN ---

        print(f"Successfully fetched and processed {len(processed_questions)} questions.")
        return processed_questions

    except requests.exceptions.Timeout:
        print(f"Error: Timeout fetching questions from OpenTDB. Params: {params}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions from OpenTDB: {e}. Params: {params}")
        return []
    except Exception as e:
        # Tangkap error spesifik jika memungkinkan, atau log traceback untuk debug
        import traceback
        print(f"An unexpected error occurred during question processing: {e}")
        print(traceback.format_exc()) # Cetak traceback untuk detail error
        return []