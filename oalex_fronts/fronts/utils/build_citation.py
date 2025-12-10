import time

import requests
from django.conf import settings


def build_citation_matrix(all_results):
  citation_matrix = {}
  works_by_id = {work["id"]: work for work in all_results}

  for work in all_results:
      citation_matrix[work["id"]] = {
          "cnt": 0,
          "works": set(),
          "title": work.get("title"),
          "publication_year": work.get("publication_year"),
          "key_words": {(word["id"], word["display_name"], word["score"]) for word in work.get("keywords", [])},
          "cited_by": set(),  # ДОБАВЛЕНО: кто цитирует эту работу
          "cites": set(work.get("referenced_works", []))  # ДОБАВЛЕНО: кого цитирует эта работа
      }

  # for work in all_results: #ДОБАВЛЕНО: вынес в цикл выше
      citing_work_id = work["id"]
      next_params = {
        "mailto": settings.MAIL_TO,
        "filter": f"cited_by:{citing_work_id}",
        "per-page": settings.PER_PAGE,
        "select": "id",
      }

      response = requests.get(settings.URL, params=next_params)
      time.sleep(0.2)
      if response.status_code == 200:
        this_page_results = response.json()['results']
        citation_matrix.get(citing_work_id)['citation_count'] = len(this_page_results)
        citation_matrix.get(citing_work_id)['citing_works'] = {el["id"] for el in this_page_results}
      else:
        print(f"Непредвиденная ошибка {response}")

  print("Обрабатываем связи цитирования...")

  # ДОБАВЛЕНО: Обновляем данные о цитированиях для PageRank
  for work in all_results:
      work_id = work["id"]

      # Заполняем cited_by (кто цитирует эту работу)
      if 'citing_works' in citation_matrix[work_id]:
          for citing_work in citation_matrix[work_id]['citing_works']:
              if citing_work in citation_matrix:
                  citation_matrix[citing_work]['cited_by'].add(work_id)


  print(f"Обработано связей цитирования для {len(all_results)} работ")

  print(citation_matrix.__len__())


  for work_id in citation_matrix:
    citation_matrix[work_id]['citing_works'] = list(citation_matrix[work_id]['citing_works'])

  return citation_matrix


def build_local_citation_sets(docs):
    keys = set(docs.keys())
    Ccited = {k: set([r for r in docs[k].get("cites", []) if r in keys]) for k in keys}
    Ccite = {k: set([r for r in docs[k].get("cited_by", []) if r in keys]) for k in keys}

    return Ccite, Ccited