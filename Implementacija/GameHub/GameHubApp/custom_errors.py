# Author: Tadija Goljic 0272/2021

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404


class MyHttp404(Http404):
    pass


class MyPermissionDenied(PermissionDenied):
    pass


class MySuspiciousOperation(SuspiciousOperation):
    pass

