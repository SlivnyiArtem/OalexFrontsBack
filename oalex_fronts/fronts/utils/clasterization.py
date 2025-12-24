import requests
from django.conf import settings
import igraph as ig

from fronts.utils import build_citation_matrix


def build_clasterization_time_window(start_date, end_date, mailto = "{EMAIL}", theme_index = "T11636"):
  mailto = mailto
  start_date = start_date
  end_date = end_date
  params = {
      "mailto": mailto,
      "filter": f"topics.id:https://openalex.org/{theme_index},from_publication_date:{start_date},to_publication_date:{end_date}",
      "per-page": int(settings.PER_PAGE),
  }

  cursor = "*"
  limit=25 #LIMIT
  all_results = []
  count_api_queries = 0

  while cursor and (limit is None or len(all_results) < limit):
      params["cursor"] = cursor
      response = requests.get(settings.URL, params=params, timeout=settings.TIMEOUT)
      if response.status_code != 200:
          break
      this_page_results = response.json()['results']
      for result in this_page_results:
          all_results.append(result)
          if len(all_results) == limit:
            break
      count_api_queries += 1

      cursor = response.json()['meta']['next_cursor']
  print(f"Done paging through results. We made {count_api_queries} API queries, and retrieved {len(all_results)} results.")


  citation_matrix = build_citation_matrix(all_results)
  works = list(citation_matrix.keys())
  n = len(works)
  work_to_index = {work_id: idx for idx, work_id in enumerate(works)}

  print(f"Вычисляем PageRank для {n} работ...")
  print(f"Параметры: damping={settings.DAMPING_FACTOR}, max_iterations={settings.MAX_ITERATIONS}")

  print("Создаем матрицу переходов...")
  transition_matrix = [[0.0] * n for _ in range(n)]

  for i, work_id in enumerate(works):
      print(f"ID: {i}")
      citing_works = citation_matrix[work_id].get('cited_by', set())
      out_links = citation_matrix[work_id].get('cites', set())

      for cited_by in citing_works:
          if cited_by in work_to_index:
              j = work_to_index[cited_by]
              transition_matrix[i][j] += 1

      for cites in out_links:
          if cites in work_to_index:
              j = work_to_index[cites]
              transition_matrix[j][i] += 1

  print("Нормализуем матрицу...")
  for i in range(n):
      row_sum = sum(transition_matrix[i])
      if row_sum > 0:
          for j in range(n):
              transition_matrix[i][j] /= row_sum
      else:
          for j in range(n):
              transition_matrix[i][j] = 1.0 / n

  print("Запускаем итерационный расчет...")
  pagerank = [1.0 / n] * n

  for iteration in range(int(settings.MAX_ITERATIONS)):
      new_pagerank = [0.0] * n

      for j in range(n):
          sum_val = 0.0
          for i in range(n):
              sum_val += transition_matrix[i][j] * pagerank[i]
          damping_factor = float(settings.DAMPING_FACTOR)
          new_pagerank[j] = (1 - damping_factor) / n + damping_factor * sum_val

      diff = sum(abs(new_pagerank[i] - pagerank[i]) for i in range(n))
      if diff < float(settings.TOLERANCE):
          print(f"✓ PageRank сошелся после {iteration + 1} итераций (diff: {diff:.8f})")
          break

      pagerank = new_pagerank

      if iteration % 10 == 0:
          print(f"  Итерация {iteration}: diff = {diff:.6f}")

  print("Сохраняем результаты PageRank...")
  for idx, work_id in enumerate(works):
      citation_matrix[work_id]['pagerank'] = pagerank[idx]

  print("✓ PageRank успешно вычислен!")

  return citation_matrix
def fast_greedy_clustering_on_Sgraph(G_nx, min_cluster_size=5):
    nodes = list(G_nx.nodes())
    idx = {n:i for i,n in enumerate(nodes)}

    edges = []
    weights = []
    for u, v, data in G_nx.edges(data=True):
        edges.append((idx[u], idx[v]))
        weights.append(float(data.get("weight", 1.0)))

    if len(edges) == 0:
        return {}

    G_ig = ig.Graph(n=len(nodes), edges=edges, directed=False)
    G_ig.es["weight"] = weights

    dendro = G_ig.community_fastgreedy(weights="weight")
    clustering = dendro.as_clustering()

    clusters = {}
    for cid, member_idxs in enumerate(clustering):
        clusters[cid] = [nodes[i] for i in member_idxs if len(member_idxs) >= min_cluster_size]

    return clusters