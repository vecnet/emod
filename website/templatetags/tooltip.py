# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django import template
register = template.Library()


@register.simple_tag(takes_context=False)
def tooltip(title):
    """ Put tooltip on html tag.
    Usage example: <a href="/" {% tooltip "Go Home" %}> Home Page </a>
    http://www.w3schools.com/bootstrap/bootstrap_tooltip.asp
    """

    return "data-toggle=\"tooltip\" title=\"%s\"" % title
