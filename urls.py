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
                       (r'^case/(?P<id>\d+)/fetch/$','npo_main.views.fetch_case',{},"fetch-case"),
                       (r'^case/(?P<id>\d+)/email/$','npo_main.views.email_case',{},"email-case"),
                       (r'^api/case/(?P<id>\d+)/$','npo_main.views.case_callback',{},"case-callback"),
                       (r'^case/(?P<id>\d+)/delete/$','npo_main.views.delete_case'),
                       (r'^case/create/$','npo_main.views.create_case'),
                       (r'^run/$','npo_main.views.run'),

### output views (stub)
                       (r'^case/sample/$','npo_main.views.sample_case'),

                       (r'^case/(?P<id>\d+)/pop/$','npo_main.views.pop'),
                       (r'^case/(?P<id>\d+)/demand/$','npo_main.views.demand'),
                       (r'^case/(?P<id>\d+)/count/$','npo_main.views.count'),
                       (r'^case/(?P<id>\d+)/system-count/$','npo_main.views.system_count'),

                       (r'^case/(?P<id>\d+)/component-costs/$','npo_main.views.cost_components'),

                       (r'^case/(?P<id>\d+)/system-summary/$','npo_main.views.system_summary'),

                       (r'^case/(?P<id>\d+)/cost-histograms/$','npo_main.views.cost_histograms'),

                       (r'^case/(?P<id>\d+)/summary/$','npo_main.views.summary'),
                       (r'^case/(?P<id>\d+)/household-cost/$','npo_main.views.household_average_cost'),

)
