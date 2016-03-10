# enable Django logging for this module
import logging
from django.http.request import HttpRequest
import warnings

logger = logging.getLogger(__name__)

ALERT_SUCCESS = "alert-success"
ALERT_DANGER = "alert-danger"
ALERT_WARNING = "alert-warning"
ALERT_INFO = "alert-info"

SUCCESS_LOG = "Success"
ERROR_LOG = "Error"

ALERT_TYPES = (ALERT_SUCCESS, ALERT_DANGER, ALERT_WARNING, ALERT_INFO)
LOG_TYPES = (SUCCESS_LOG, ERROR_LOG)


def set_notification(session, message, alert_type):

    """ Set notification that will be displayed in {% notifications %} templatetag when page is rendered

    This function should be call in a Django view. Session object is normally available as request.session
    (provided that sessions are enabled in your Django project).
    Bootstrap alert class is used (<div class="alert {{ notification.type }}">)

    :param session: Django session object (request.session) or HttpRequest object
    :param message: Message to be show
    :type message: str
    :param alert_type: alert class - alert-cuess
    :type alert_type: "alert-success", "alert-danger", "alert", "alert-info"
    """

    if alert_type not in ALERT_TYPES:
        raise ValueError("Invalid alert type of " + str(alert_type))

    # Preparing for switching to Django HttpRequest
    if isinstance(session, HttpRequest):
        session = session.session
    else:
        warnings.warn("Using Django session variable is depricated, pass HttpRequest object to set_notification function instead", RuntimeWarning)  # noqa

    if not session.__contains__("notifications"):
        session["notifications"] = []
    session["notifications"].append({"message": message, "type": alert_type})
    logger.debug("Webpage notification: [%s] %s" % (alert_type, message))


set_notification.SUCCESS = "alert-success"
set_notification.DANGER = "alert-danger"
set_notification.WARNING = "alert-warning"
set_notification.INFO = "alert-info"


def create_notification_log(log, log_id, log_type):
    if log_type not in LOG_TYPES:
        raise ValueError("Invalid log type of " + str(log_type))

    if log_type == ERROR_LOG:
        button_type = "btn-danger"
    elif log_type == SUCCESS_LOG:
        button_type = "btn-success"
    else:
        raise ValueError("button_type for log_type of " + str(log_type) + " has not been implemented yet.")

    button_html_code = \
        '<button type="button" class="accordion-toggle btn ' + str(button_type) + '" data-toggle="collapse" \
            data-target="#log-' + str(log_id) + '-accordion"> ' + \
            str(log_type) + ' Log (click to show) \
        </button>'

    log_html_code = ""

    for message in log:
        log_html_code += str(message) + "<br>"

    accordion_html_code = \
        '<div class="accordion-body collapse" id="log-' + str(log_id) + '-accordion"> \
            <div class="accordion-inner"> ' + \
                str(log_html_code) + ' \
            </div> \
        </div>'

    html_code = button_html_code + accordion_html_code

    return html_code