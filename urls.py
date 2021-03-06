from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       # Example:
                       # (r'^npo/', include('npo.foo.urls')),
                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
		       (r'^survey/',include('survey.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),

                       (r'^$','npo_main.views.index'),
                       (r'^bulk/$','npo_main.views.bulk'),
                       (r'^case/(?P<id>\d+)/$','npo_main.views.case',{},"view-case"),
                       (r'^case/(?P<id>\d+)/debug/$','npo_main.views.debug_case',{},"debug-case"),
                       (r'^case/(?P<id>\d+)/recalc/$','npo_main.views.recalc',{}),
                       (r'^case/(?P<id>\d+)/fetch/$','npo_main.views.fetch_case',{},"fetch-case"),
                       (r'^case/(?P<id>\d+)/email/$','npo_main.views.email_case',{},"email-case"),
                       (r'^api/case/(?P<id>\d+)/$','npo_main.views.case_callback',{},"case-callback"),
                       (r'^case/(?P<id>\d+)/delete/$','npo_main.views.delete_case'),

                       (r'^case/recalc/$','npo_main.views.recalc',{}),
                       (r'^case/create/$','npo_main.views.create_case'),
                       (r'^compare/(?P<ids>[\d\,]+)/$','npo_main.views.compare_cases'),
                       (r'^run/$','npo_main.views.run'),
)
