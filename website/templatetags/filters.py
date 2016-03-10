# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django import template

register = template.Library()


@register.filter(name="phone")
def phone(value):
    if value is None or value == "":
        return ""
    value += "           "
    return "(" + value[0:3] + ")" + value[3:6] + "-" + value[6:10]


@register.filter()
def create_function_string(function_name, function_parameters):
    function_parameters = function_parameters.split(",")
    function_string = str(function_name) + "("

    for i in range(len(function_parameters)):
        function_string += "'" + str(function_parameters[i]) + "',"

    function_string = function_string[:-1] + ")"

    return function_string


# Needed for easier use with with statements
@register.filter(name="not_it")
def not_it(boolean_value):
    return not boolean_value


@register.filter(name="replace_spaces_with_underscores")
def replace_spaces_with_underscores(string):
    return string.replace(" ", "_")