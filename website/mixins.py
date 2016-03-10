# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django.contrib.auth.decorators import login_required
from website.notification import set_notification as set_website_notification


class LoginRequiredMixin(object):
    """ This works: class InterviewListView(LoginRequiredMixin, ListView)
    This DOES NOT work: class InterviewListView(ListView, LoginRequiredMixin)
    I'm not 100% sure that wrapping as_view function using Mixin is a good idea though, but whatever
    """
    @classmethod
    def as_view(cls, **initkwargs):
        # Ignore PyCharm warning below, this is a Mixin class after all
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class NotificationMixin(object):
    SUCCESS = "alert-success"
    ERROR = "alert-danger"
    WARNING = "alert-warning"
    INFO = "alert-info"

    def set_notification(self, message, alert_type=None):
        if alert_type is None:
            alert_type = NotificationMixin.INFO
        # Ignore PyCharm warning below, this is a Mixin class after all
        set_website_notification(self.request.session, message, alert_type)
