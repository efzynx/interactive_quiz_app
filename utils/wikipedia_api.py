import wikipedia
from typing import Optional, Dict

# Set bahasa ke Indonesia
wikipedia.set_lang("id")

def get_wikipedia_summary(topic: str, sentences: int = 3) -> Optional[Dict[str, str]]:
    """Mencari ringkasan singkat dari Wikipedia Indonesia."""
    try:
        # Coba cari halaman yang paling relevan
        search_results = wikipedia.search(topic)
        if not search_results:
            print(f"Wikipedia page not found for: {topic}")
            return None

        # Ambil halaman pertama dari hasil pencarian
        page_title = search_results[0]
        page = wikipedia.page(page_title, auto_suggest=False) # Hindari auto suggest jika judul sudah pasti

        summary = wikipedia.summary(page_title, sentences=sentences, auto_suggest=False)
        return {
            "title": page.title,
            "summary": summary,
            "url": page.url
        }
    except wikipedia.exceptions.PageError:
        print(f"Wikipedia page not found for: {topic} (PageError)")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Wikipedia disambiguation error for: {topic}. Options: {e.options[:3]}")
        # Coba ambil halaman pertama dari opsi disambiguasi
        try:
            first_option_title = e.options[0]
            page = wikipedia.page(first_option_title, auto_suggest=False)
            summary = wikipedia.summary(first_option_title, sentences=sentences, auto_suggest=False)
            return {
                "title": page.title,
                "summary": summary,
                "url": page.url
             }
        except Exception as inner_e:
             print(f"Could not resolve disambiguation for {topic}: {inner_e}")
             return None
    except Exception as e:
        print(f"An unexpected error occurred fetching Wikipedia summary for {topic}: {e}")
        return None