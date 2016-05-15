from django.conf.urls import url

from .views import HotClubWizard

urlpatterns = [
    url(r'^wizard/(?:(?P<step>.+)/)?$', HotClubWizard.as_view(),
        name='hotclub_wizard'),
]
