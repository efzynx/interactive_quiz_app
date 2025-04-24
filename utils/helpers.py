# File: utils/helpers.py

# Import library standar Python untuk URL parsing
import urllib.parse
# Import html juga tidak apa-apa jika ingin digabungkan,
# tapi untuk masalah ini, urllib lebih tepat.
import html

def decode_text(text: str) -> str:
    """
    Membersihkan teks dari URL encoding (%20, %3A, dll.)
    dan juga HTML entities (&quot;, &amp;, dll.).
    """
    # Langkah 1: Decode URL percent-encoding
    decoded_url = urllib.parse.unquote(text)
    # Langkah 2: Decode HTML entities (jika ada sisa atau kasus lain)
    decoded_html = html.unescape(decoded_url)
    return decoded_html

# --- Catatan ---
# Kita mengganti nama fungsi agar lebih umum (decode_text)
# Jika Anda tetap ingin menggunakan nama decode_html_entities,
# ubah saja isi fungsinya seperti di atas.
# Pastikan file lain (opentdb_api.py) memanggil nama fungsi yang benar.
# Untuk konsistensi dengan kode sebelumnya, mari kita tetap gunakan nama lama
# tapi dengan implementasi baru:

def decode_html_entities(text: str) -> str:
    """
    Membersihkan teks dari URL encoding (%20, %3A, dll.)
    dan juga HTML entities (&quot;, &amp;, dll.).
    Versi ini MENGGANTIKAN implementasi lama.
    """
    # Langkah 1: Decode URL percent-encoding
    decoded_url = urllib.parse.unquote(text)
    # Langkah 2: Decode HTML entities (untuk kasus lain atau sisa)
    decoded_html = html.unescape(decoded_url)
    return decoded_html