import networkx as nx

from fronts.utils.build_citation import build_local_citation_sets
from fronts.utils.calculate_similarity import calculate_similarity
from fronts.utils.clasterization import build_clasterization_time_window, fast_greedy_clustering_on_Sgraph
from fronts.utils.key_words import top_k_keywords



def build_similarity_graph(docs):
    Ccite, Ccited = build_local_citation_sets(docs)
    doc_ids = list(docs.keys())

    G = nx.Graph()
    G.add_nodes_from(doc_ids)

    for i in range(len(doc_ids)):
        for j in range(i+1, len(doc_ids)):
            A = doc_ids[i]
            B = doc_ids[j]

            s = calculate_similarity(A, B, Ccite, Ccited)
            if s > 0:
                G.add_edge(A, B, weight=s)

    return G, Ccite, Ccited


def build_multi_time_citation_graph(time_windows, theme_index, K=5, min_cluster_size=2):
    """
    Строит временной граф кластеров с направленными ребрами между окнами

    Args:
        time_windows: список дат для временных окон
        K: количество топовых ключевых слов для каждого кластера
        min_cluster_size: минимальный размер кластера для отображения
    """

    time_intervals = list(zip(time_windows[:-1], time_windows[1:]))

    all_clusters_by_window = []
    citation_matrices_by_window = []
    top_keywords_by_cluster = {}  # (window_idx, cluster_id) -> top_k keywords

    print(f"Всего временных окон: {len(time_intervals)}")

    for window_idx, (start_date, end_date) in enumerate(time_intervals):
        print(f"Временное окно {window_idx+1}: {start_date} - {end_date}")

        citation_matrix_for_window = build_clasterization_time_window(start_date, end_date, theme_index=theme_index)

        print(f"Количество работ: {len(citation_matrix_for_window)}")

        if len(citation_matrix_for_window) < min_cluster_size:
            print("Мало данных для этого окна, пропускаем...")
            all_clusters_by_window.append({})
            citation_matrices_by_window.append({})
            continue


        sim_G, Ccite, Ccited = build_similarity_graph(citation_matrix_for_window)
        clusters = fast_greedy_clustering_on_Sgraph(sim_G)

        print(f"Найдено кластеров в окне {window_idx+1}: {len(clusters)}")

        all_clusters_by_window.append(clusters)
        citation_matrices_by_window.append(citation_matrix_for_window)

        for cluster_id, members in clusters.items():
            if len(members) >= min_cluster_size:
                all_keywords = []
                for doc_id in members:
                    key_words = citation_matrix_for_window[doc_id].get('key_words', [])
                    all_keywords.extend(key_words)

                top_k = top_k_keywords(all_keywords, K)
                top_keywords_by_cluster[(window_idx, cluster_id)] = top_k

                print(f"\nКластер {cluster_id} (окно {window_idx+1}, размер: {len(members)}):")
                print(f"Топ-{K} ключевых слов:")
                for i, (keyword, score, count) in enumerate(top_k):
                    print(f"  {i+1}. {keyword} (score: {score:.3f}, статей: {count})")


    time_graph = nx.DiGraph()
    for window_idx in range(len(all_clusters_by_window)):
        clusters = all_clusters_by_window[window_idx]
        citation_matrix = citation_matrices_by_window[window_idx]

        for cluster_id, members in clusters.items():
            if len(members) >= min_cluster_size:
                node_uid = f"W{window_idx}_C{cluster_id}"
                total_citations = sum(
                    citation_matrix[doc_id].get('citation_count', 0)
                    for doc_id in members
                )
                top_kw = top_keywords_by_cluster.get((window_idx, cluster_id), [])
                keywords_str = ", ".join([kw[0] for kw in top_kw[:3]])

                time_graph.add_node(node_uid,
                                   cluster_size=len(members),
                                   total_citations=total_citations,
                                   window=window_idx,
                                   original_cluster_id=cluster_id,
                                   keywords=keywords_str,
                                   full_keywords=top_kw)

    for window_idx in range(len(all_clusters_by_window) - 1):
        current_clusters = all_clusters_by_window[window_idx]
        next_clusters = all_clusters_by_window[window_idx + 1]

        next_citation_matrix = citation_matrices_by_window[window_idx+1]

        current_filtered = {cid: members for cid, members in current_clusters.items()
                          if len(members) >= min_cluster_size}
        next_filtered = {cid: members for cid, members in next_clusters.items()
                        if len(members) >= min_cluster_size}

        current_pairs = list(current_filtered.items())
        next_pairs = list(next_filtered.items())

        for i in range(len(current_pairs)):
            for j in range(len(next_pairs)):
                curr_cluster_id, curr_members = current_pairs[i]
                next_cluster_id, next_members = next_pairs[j]

                N_ci = 0

                for doc_p in curr_members:
                    for doc_q in next_members:
                        if doc_q in next_citation_matrix:
                            cites_list = next_citation_matrix[doc_q].get('cites', [])
                            if doc_p in cites_list:
                                N_ci += 1

                p_size = len(curr_members)
                q_size = len(next_members)

                if p_size > 0 and q_size > 0:
                    cluster_similarity = N_ci / (0.5 * (p_size + q_size))
                    print(f"p_size: {p_size}, q_size: {q_size}, N_ci: {N_ci}")

                    if cluster_similarity > 0.0:
                        source_node = f"W{window_idx}_C{curr_cluster_id}"
                        target_node = f"W{window_idx+1}_C{next_cluster_id}"

                        time_graph.add_edge(source_node, target_node,
                                           weight=cluster_similarity,
                                           citation_count=N_ci,
                                           label=f"{cluster_similarity:.3f}",
                                           size_p=p_size,
                                           size_q=q_size)

    return time_graph, all_clusters_by_window, citation_matrices_by_window