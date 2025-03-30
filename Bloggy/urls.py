from django.contrib import admin
from django.urls import path, include, reverse
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from Bloggy import settings
from web_user.models import Web_post
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap



class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Web_post.objects.select_related('post_author', 'post_category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('web_post', kwargs={'category': obj.post_category.catSlug, 'post': obj.post_slug})


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_box/', include('admin_box.urls')),
    path('', include('web_user.urls')),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
