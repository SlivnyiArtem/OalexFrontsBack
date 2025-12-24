from django.shortcuts import render
from django.views import View
from datetime import datetime

from fronts.utils import build_multi_time_citation_graph


def _get_default_time_windows():
    return ["2023-01-01", "2023-12-31", "2024-12-31"]


class HomepageFormView(View):
    template_name = 'formreq.html'

    def get(self, request):
        default_windows = _get_default_time_windows()

        return render(request, self.template_name, {
            'time_windows': default_windows,
            'window1': default_windows[0] if len(default_windows) > 0 else '',
            'window2': default_windows[1] if len(default_windows) > 1 else '',
            'window3': default_windows[2] if len(default_windows) > 2 else ''
        })

    def post(self, request):
        theme_id = request.POST.get('theme_id')

        window1 = request.POST.get('window1', '')
        window2 = request.POST.get('window2', '')
        window3 = request.POST.get('window3', '')

        time_windows_list = []
        if window1:
            time_windows_list.append(window1)
        if window2:
            time_windows_list.append(window2)
        if window3:
            time_windows_list.append(window3)

        if not time_windows_list:
            time_windows_list = _get_default_time_windows()

        try:
            dates = [datetime.strptime(date, '%Y-%m-%d') for date in time_windows_list]
            if dates != sorted(dates):
                return render(request, self.template_name, {
                    'error': 'Даты должны быть в хронологическом порядке',
                    'theme_id': theme_id,
                    'window1': window1,
                    'window2': window2,
                    'window3': window3,
                    'time_windows': time_windows_list
                })
        except ValueError as e:
            return render(request, self.template_name, {
                'error': f'Некорректный формат даты: {str(e)}',
                'theme_id': theme_id,
                'window1': window1,
                'window2': window2,
                'window3': window3,
                'time_windows': time_windows_list
            })

        time_graph, all_clusters, citation_matrices = build_multi_time_citation_graph(
            time_windows_list, theme_id, K=5, min_cluster_size=2
        )

        nodes_data = list(time_graph.nodes(data=True))
        edges_data = []
        for source, target, data in time_graph.edges(data=True):
            edge_info = {
                'source': source,
                'target': target,
                'weight': data.get('weight', 0),
                'citation_count': data.get('citation_count', 0),
                'size_p': data.get('size_p', 0),
                'size_q': data.get('size_q', 0)
            }
            edges_data.append(edge_info)

        window_stats = {}
        for node, data in nodes_data:
            window = data.get('window', 0)
            if window not in window_stats:
                window_stats[window] = {
                    'nodes': 0,
                    'total_citations': 0,
                    'total_articles': 0
                }
            window_stats[window]['nodes'] += 1
            window_stats[window]['total_citations'] += data.get('total_citations', 0)
            window_stats[window]['total_articles'] += data.get('cluster_size', 0)
        top_edges = sorted(edges_data, key=lambda x: x['weight'], reverse=True)[:5]

        time_window_range = range(1, len(time_windows_list))

        return render(request, 'homepage_results.html', {
            'theme_id': theme_id,
            'num_clusters': len(all_clusters),
            'node_count': time_graph.number_of_nodes(),
            'edge_count': time_graph.number_of_edges(),
            'time_windows': time_windows_list,
            'nodes_data': nodes_data,
            'edges_data': edges_data,
            'window_stats': window_stats,
            'top_edges': top_edges,
            'time_window_range': time_window_range
        })