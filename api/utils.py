from collections import OrderedDict

import django_filters
from rest_framework import pagination
from rest_framework.response import Response
import rest_framework.exceptions

class VariableResultsSetPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 10

    def paginate_queryset(self, queryset, request, view=None):
        if 'no_pagination' in request.query_params:
            return list(queryset)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        try:
            return super().get_paginated_response(data)
        except AttributeError:
            # Occurs when page_size is set to None. Still want response in same JSON format
            return Response(OrderedDict([('count', len(data)), ('results', data)]))


class RestrictedQueryMixin(object):
    """Cause view to fail on invalid filter query parameter.

    Thanks to rrauenza on Stack Overflow for their post here:
    https://stackoverflow.com/questions/27182527/how-can-i-stop-django-rest-framework-to-show-all-records-if-query-parameter-is-w/50957733#50957733
    """
    def get_queryset(self):
        non_filter_params = set(['limit', 'offset', 'page', 'page_size', 'format', 'no_pagination'])

        qs = super(RestrictedQueryMixin, self).get_queryset().order_by('id')

        if hasattr(self, 'filter_fields') and hasattr(self, 'filter_class'):
            raise RuntimeError("%s has both filter_fields and filter_class" % self)

        if hasattr(self, 'filter_class'):
            filter_class = getattr(self, 'filter_class', None)
            filters_dict = filter_class.get_filters()
            filters = set(filters_dict.keys())

            # Deal with DateFromToRangeFilters
            for filter_name, filter_inst in filters_dict.items():
                if type(filter_inst) == django_filters.filters.DateFromToRangeFilter:
                    filters.update({filter_name + '_0', filter_name + '_1'})

        elif hasattr(self, 'filter_fields'):
            filters = set(getattr(self, 'filter_fields', []))
        else:
            filters = set()

        for key in self.request.GET.keys():
            if key in non_filter_params:
                continue
            if key not in filters:
                raise rest_framework.exceptions.APIException('no filter %s' % key)

        return qs