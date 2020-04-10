from rest_framework.permissions import BasePermission, SAFE_METHODS
from ApiRequesters.Auth.permissions import IsAuthenticated, IsSuperuser, IsModerator


class WriteOnlyByAuthenticated(BasePermission):
    """
    Пермишн на запись только зареганным
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsAuthenticated().has_permission(request, view)


class WriteOnlyByModerator(BasePermission):
    """
    Пермишн на запись только модератором
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsModerator().has_permission(request, view)


class WriteOnlyBySuperuser(BasePermission):
    """
    Пермишн на запись только суперюзером
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsSuperuser().has_permission(request, view)


class AddNewImagePermission(BasePermission):
    """
    Пермишн на добавление (фотку места модератор и выше а пины и ачивки только суперющер, а аватарка все)
    """
    def has_permission(self, request, view):
        try:
            object_type = request.data['object_type']
        except KeyError:
            object_type = None
        if object_type in ('achievement', 'gpin', 'ppin'):
            return IsSuperuser().has_permission(request, view)
        elif object_type == 'place':
            return IsModerator().has_permission(request, view)
        elif object_type == 'user':
            return IsAuthenticated().has_permission(request, view)
        else:
            return True
