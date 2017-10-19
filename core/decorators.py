"""
Created on May 31, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.shortcuts import render
# import functools


class Render(object):

    """
    Render the request with the given template.
    """

    def __init__(self, template):
        self.template = template

    def __call__(self, func):
        # @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            res = func(request, *args, **kwargs)
            ## render it only if the response is a context dictionary
            if isinstance(res, dict):
                return render(request, self.template, res)
            else:
                return res
        return wrapper

