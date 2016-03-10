from django.conf.urls import include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView

from django.contrib.auth import views

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^$", TemplateView.as_view(template_name="index.html"), name="index"),
    url(r"^credits/$", TemplateView.as_view(template_name="credits.html"), name="credits"),
    # robots.txt is implemented as a template because Django can't seem to serve a static file from urls.py
    url(r"^robots.txt$", TemplateView.as_view(template_name="robots.txt")),

    # url(r"^auth/login/$", views.login, name="login"),
    # url(r"^auth/logout/$", views.logout, name="logout"),
    # Using post_change_redirect to reset teammember.generated_password after the first login
    # (in website.save_team_member view)
    url(r"^auth/password_change/$", views.password_change, name="password_change",
                kwargs={"post_change_redirect": reverse_lazy("website.save_team_member")}),
    url(r"^password_change/done/$", views.password_change_done, name="password_change_done"),
    url(r"^password_reset/$", views.password_reset, name="password_reset"),
    url(r"^password_reset/done/$", views.password_reset_done, name="password_reset_done"),
    url(r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.password_reset_confirm, name="password_reset_confirm"),
    url(r"^reset/done/$", views.password_reset_complete, name="password_reset_complete"),

    # django-registration-redux URLs
    # https://django-registration-redux.readthedocs.org/en/latest/quickstart.html#setting-up-urls
#    url(r"^accounts/", include("registration.backends.default.urls")),

    # url(r"^subject_manager/", include("website.apps.subject_manager.urls")),
]

# handler404 = TemplateView.as_view(template_name="404.html")
