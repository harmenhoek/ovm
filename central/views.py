from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, Planning


class PostListView(ListView):
    model = Post
    template_name = 'central/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-postslug']



    # def get_queryset(self):
    #     from datetime import datetime, timedelta
    #     from django.db.models import Count, F
    #     datetimenow = datetime.now()
    #     return Planning.objects.filter(shift__shiftstart__lt=datetimenow, shift__shiftend__lt=datetimenow).values('post').annotate(dcount=Count('post'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # load status for map
        from datetime import datetime, timedelta
        from django.db.models import Count, F
        datetimenow = datetime.now()

        # now + overdue

        status_orange = Planning.objects.filter(remove=False, confirmed=True, shift__shiftstart__lt=datetimenow,
                                                shift__shiftend__lt=datetimenow). \
            values('post').distinct()
            # values('post', 'post__postslug', 'shift').annotate(dcount=Count('post')).order_by()

        # now + not confirmed (planning)
        status_blue = Planning.objects.filter(remove=False, confirmed=False, shift__shiftstart__lt=datetimenow,
                                              shift__shiftend__gt=datetimenow). \
            exclude(pk__in=status_orange).values('post').distinct()

        # now + confirmed
        status_green = Planning.objects.filter(remove=False, confirmed=True, shift__shiftstart__lt=datetimenow,
                                               shift__shiftend__gt=datetimenow).\
            exclude(pk__in=status_orange | status_blue).values('post').distinct()

        # TODO in near future
        # TODO include extra time from shift

        status_orange_2 = [{i['post']: 'warning'} for i in status_orange]
        status_blue_2 = [{i['post']: 'primary'} for i in status_blue]
        status_green_2 = [{i['post']: 'success'} for i in status_green]
        context['status'] = {k: v for element in status_orange_2 + status_blue_2 + status_green_2 for k, v in element.items()}

        context['status_green'] = status_green
        context['status_orange'] = status_orange
        context['status_blue'] = status_blue

        # get all post information for map
        context['current_post'] = Post.objects.filter(postslug=self.kwargs.get('postslug')).first()  # must first since no pk is used

        occ_orange = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), remove=False, confirmed=True,
                                             shift__shiftstart__lt=datetimenow, shift__shiftend__lt=datetimenow)
        occ_blue = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), remove=False, confirmed=False,
                                           shift__shiftstart__lt=datetimenow, shift__shiftend__gt=datetimenow)
        occ_green = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), remove=False, confirmed=True,
                                            shift__shiftstart__lt=datetimenow,shift__shiftend__gt=datetimenow)
        occ = occ_orange | occ_blue | occ_green
        occ_color = ["warning" for i in range(occ_orange.count())] + \
                    ["primary" for i in range(occ_blue.count())] + \
                    ["success" for i in range(occ_green.count())]
        context['current_occupation'] = zip(occ, occ_color)

        return context

# class PostDetailView(LoginRequiredMixin, DetailView):
#     model = Post
#     slug_url_kwarg = 'postslug'
#     slug_field = 'postslug'
#     template_name = 'central/home.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['posts'] = Post.objects.all().filter(active=True)
#         return context
#
#     def get_object(self):
#         return get_object_or_404(Post, pk=1)

def about(request):
    return render(request, 'central/about.html', {'title': 'About'})
