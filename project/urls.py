"""URL configuration for the application. Maps URLs to Views."""

from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

from rest_framework_swagger.views import get_swagger_view

from weather import urls as api_urls

urls_documented = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_urls.urlpatterns)),
    url(r'^$', RedirectView.as_view(url='/api/schema/', permanent=False), name='index')
]

schema_view = get_swagger_view(title='Weather API documentation', patterns=urls_documented)

urlpatterns = urls_documented + [url(r'^api/schema/$', schema_view)]
