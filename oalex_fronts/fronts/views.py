from django.shortcuts import render
from django.views import View

from fronts.utils import build_multi_time_citation_graph
from fronts.utils.visualization import visualize_time_graph


# Create your views here.
class HomepageFormView(View):
    template_name = 'homepage.html'

    def get(self, request):
        # Отображаем пустую форму
        return render(request, self.template_name, {
            'time_windows': ["2023-01-01", "2023-12-31", "2024-12-31"]
        })

    def post(self, request):
        # Получаем идентификатор темы из формы
        theme_id = request.POST.get('theme_id')

        # Фиксированные временные окна (как в примере)
        time_windows_list = ["2023-01-01", "2023-12-31", "2024-12-31"]

        # Вызов вашей функции (замените на реальный импорт)
        time_graph, all_clusters, citation_matrices = build_multi_time_citation_graph(
            time_windows_list, theme_id, K=5, min_cluster_size=2
        )

        # Визуализация
        visualize_time_graph(time_graph)



        # Передача данных в шаблон
        return render(request, 'homepage_results.html', {
            'theme_id': theme_id,
            'clusters_info': time_graph,
            'num_clusters': len(all_clusters),
            'citation_matrices_shape': [matrix.shape for matrix in citation_matrices] if citation_matrices else [],
            'time_windows': time_windows_list
        })