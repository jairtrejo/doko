from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static


# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
    patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )
)
