import matplotlib.pyplot as plt
import networkx as nx

def visualize_time_graph(time_graph): #альтернативный метод, чтобы отрисовывать единый граф для всех временных окон


    # Создаем позиции для узлов (временные окна по горизонтали)
    pos = {}
    node_colors = []
    node_sizes = []

    # Размер узлов пропорционален размеру кластера
    max_cluster_size = max([data.get('cluster_size', 1)
                          for _, data in time_graph.nodes(data=True)])

    for node, data in time_graph.nodes(data=True):
        window = data.get('window', 0)
        cluster_size = data.get('cluster_size', 1)

        # Располагаем окна по горизонтали, кластеры по вертикали
        pos[node] = (window * 2, hash(node) % 100 / 100.0)

        # Цвет в зависимости от окна
        node_colors.append(window)

        # Размер в зависимости от размера кластера
        node_sizes.append(500 + 2000 * (cluster_size / max_cluster_size))

    # Рисуем граф
    plt.figure(figsize=(14, 8))

    # Рисуем узлы
    nx.draw_networkx_nodes(time_graph, pos,
                          node_size=node_sizes,
                          node_color=node_colors,
                          cmap=plt.cm.viridis,
                          alpha=0.8)




    print(time_graph.edges)

    # nx.draw_networkx_edges(
    #     time_graph, pos,
    #     edgelist=weak_edges,
    #     width=[1.0*5 for el in weak_edges],
    #     style='dashed',
    #     alpha=0.5,
    #     edge_color='gray',
    #     arrows=True,
    #     arrowstyle='-|>',
    #     arrowsize=20
    # )
    # nx.draw_networkx_edges(
    #     time_graph, pos,
    #     edgelist=medium_edges,
    #     width=[1.5*5 for el in medium_edges],
    #     style='solid',
    #     alpha=0.5,
    #     edge_color='blue',
    #     arrows=True,
    #     arrowstyle='-|>',
    #     arrowsize=20
    # )
    # nx.draw_networkx_edges(
    #     time_graph, pos,
    #     edgelist=strong_edges,
    #     width=[3.0*5 for el in strong_edges],
    #     style='solid',
    #     alpha=0.5,
    #     edge_color='red',
    #     arrows=True,
    #     arrowstyle='-|>',
    #     arrowsize=20
    # )

    # Рисуем ребра с толщиной, пропорциональной весу
    edge_widths = [2 + 3 * data.get('weight', 0)
                  for _, _, data in time_graph.edges(data=True)]

    nx.draw_networkx_edges(time_graph, pos,
                          width=edge_widths,
                          alpha=0.5,
                          edge_color='gray',
                          arrows=True,
                          arrowstyle='-|>',
                          arrowsize=20)

    # Рисуем подписи
    labels = {}
    for node, data in time_graph.nodes(data=True):
        window = data.get('window', 0)
        cluster_id = data.get('original_cluster_id', '?')
        size = data.get('cluster_size', 0)
        labels[node] = f"W{window}C{cluster_id}\n({size})"

    nx.draw_networkx_labels(time_graph, pos, labels, font_size=9)

    # Добавляем подписи к ребрам
    edge_labels = {(u, v): f"{d.get('citation_count', 0)}"
                  for u, v, d in time_graph.edges(data=True)}
    nx.draw_networkx_edge_labels(time_graph, pos, edge_labels, font_size=8)

    plt.title("Временная динамика кластеров исследований")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    return plt.gcf()

def visualize_citation_graph(citation_matrix, clusters, G, min_cluster_size=5, window_sim_threshold=(0.0, 0.3, 0.5)): #старый метод общего графа(без ранжирования по окнам)
  cluster_graph = nx.Graph()
  for cluster_id in clusters.keys():
    cluster_graph.add_node(cluster_id)
  cluster_metrics = {}

  top_clusters = {k: v for k, v in clusters.items()
                        if len(v) >= min_cluster_size}

  cluster_pairs = list(top_clusters.keys())



  for cluster_id, doc_ids in top_clusters.items():
    cluster_graph.add_node(cluster_id)
    total_citations = sum(citation_matrix[doc_id].get('citation_count', 0) for doc_id in doc_ids)
    cluster_graph.nodes[cluster_id]["total_citations"] = total_citations

  weak_threshold, medium_threshold, strong_threshold = window_sim_threshold

  for i in range(len(cluster_pairs)):
    for j in range(i + 1, len(cluster_pairs)):
      cluster_p = cluster_pairs[i]
      cluster_q = cluster_pairs[j]
      N_ci = 0
      for doc_p in top_clusters[cluster_p]:
        for doc_q in top_clusters[cluster_q]:
          if doc_q in citation_matrix[doc_p].get('cites', []):
            N_ci += 1
          if doc_p in citation_matrix[doc_q].get('cites', []):
            N_ci += 1
      p_size = len(top_clusters[cluster_p])
      q_size = len(top_clusters[cluster_q])
      cluster_similarity = N_ci/(0.5*(p_size+q_size))



      if cluster_similarity > weak_threshold:

        if cluster_similarity >= strong_threshold:
          edge_type = "strong"
        elif cluster_similarity >= medium_threshold:
          edge_type = "medium"
        elif cluster_similarity >= weak_threshold:
          edge_type = "weak"
        else:
          continue

        edge_attrs = {
            "weight": cluster_similarity,
            "citation_count": N_ci,
            "label": cluster_similarity,
            "size_p": p_size,
            "size_q": q_size,
            "edge_type": edge_type
        }

        cluster_graph.add_edge(cluster_p, cluster_q, **edge_attrs)

  print(clusters)
  return cluster_graph