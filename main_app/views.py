from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView

from .filters import PostFilter
from .forms import PostForm
from .models import Post


class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_in_page'] = self.paginate_by
        return context


class NewsItem(DetailView):
    model = Post
    template_name = 'news_item.html'
    context_object_name = 'news_item'


class Search(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'post_search'
    ordering = ['-dateCreation']
    filter_class = PostFilter  # Для вывода фильтра не через форму
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=queryset)
        return self.filter.qs.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) # Если выводить фильтр только через формы
        context['filter'] = self.filter  # Если выводить фильтр не через формы
        context['list_in_page'] = self.paginate_by  # Для отображения кол-ва выведенных публикаций на странице
        context['all_posts'] = Post.objects.all()  # Для отображения общего кол-ва публикаций на сайте
        return context


class CreatePost(PermissionRequiredMixin, CreateView):
    permission_required = ('main_app.add_post',)
    model = Post
    template_name = 'create_post.html'
    form_class = PostForm


class EditPost(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('main_app.change_post',)
    template_name = 'edit_post.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class DeletePost(DeleteView):
    template_name = 'delete_post.html'
    queryset = Post.objects.all()
    success_url = '/news/'
