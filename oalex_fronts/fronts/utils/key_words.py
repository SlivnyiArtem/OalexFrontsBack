from collections import defaultdict
from math import log


def top_k_keywords(cluster_articles_keywords, k):
    word_stats = defaultdict(lambda: {"total_score": 0.0, "article_count": 0})

    for keyword, keyword_name, score in cluster_articles_keywords:
       key = keyword_name
       word_stats[keyword_name]["total_score"] += score
       word_stats[keyword_name]["article_count"] += 1

    metrics = []
    for keyword, data in word_stats.items():
        avg_score = data['total_score'] / data['article_count']
        score = avg_score * log(1+data['article_count'])
        metrics.append({
            'word': keyword,
            'score': score,
            'avg_score': avg_score,
            'article_count': data['article_count']
        })

    metrics.sort(key=lambda x: (x['article_count'], x['avg_score'], x['score']), reverse=True)

    return [(res['word'], res["score"],res["article_count"]) for res in metrics[:k]]