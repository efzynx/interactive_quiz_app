from typing import List, Optional
from models.quiz_models import WeaknessAnalysis
from models.recommendation_models import Recommendation
from utils.wikipedia_api import get_wikipedia_summary

# Batas skor untuk dianggap 'lemah' (misal: di bawah 60%)
WEAKNESS_THRESHOLD_PERCENTAGE = 60.0

async def generate_recommendations(analysis: List[WeaknessAnalysis]) -> List[Recommendation]:
    """Menghasilkan rekomendasi berdasarkan analisis kelemahan."""
    recommendations: List[Recommendation] = []
    weak_categories = [
        item.category_name for item in analysis
        if item.score_percentage < WEAKNESS_THRESHOLD_PERCENTAGE and item.total_questions > 0 # Hanya jika ada soal di kategori tsb
    ]

    # Ambil 1-2 rekomendasi per kategori lemah (bisa diperbanyak)
    max_recs_per_category = 1
    for category_name in weak_categories:
        # Coba cari ringkasan Wikipedia untuk nama kategori tersebut
        summary_data = get_wikipedia_summary(topic=category_name, sentences=4)
        if summary_data:
            recommendations.append(
                Recommendation(
                    title=f"Baca tentang: {summary_data['title']}",
                    summary=summary_data['summary'],
                    url=summary_data['url']
                )
            )
            # Jika ingin lebih dari 1 rekomendasi per kategori, perlu logika
            # pencarian topik yang lebih spesifik terkait kategori tsb.

        if len(recommendations) >= max_recs_per_category * len(weak_categories):
             break # Batasi jumlah total rekomendasi (opsional)

    # Jika tidak ada kategori lemah atau tidak ada rekomendasi ditemukan
    if not recommendations:
         # Berikan rekomendasi umum atau pesan penyemangat
         general_topic = "Pengetahuan Umum" # atau ambil dari kategori dg skor terendah > threshold
         summary_data = get_wikipedia_summary(topic=general_topic, sentences=3)
         if summary_data:
              recommendations.append(
                   Recommendation(
                        title=f"Tingkatkan Wawasan: {summary_data['title']}",
                        summary=f"Skormu sudah bagus! Mungkin tertarik membaca lebih lanjut tentang {general_topic}? {summary_data['summary']}",
                        url=summary_data['url']
                   )
              )
         else:
              recommendations.append(Recommendation(title="Selamat!", summary="Skormu bagus di semua kategori yang diuji kali ini!", url=None))


    return recommendations