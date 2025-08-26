from api.models import Library
from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the author of a story to edit/delete it.
    """ 

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are read-only (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True 
        # Only the author can update or delete
        return obj.author == request.user





class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    this permission allows the owner to update/delete obj ,else it's read only, intented for model like 'Library' where ownership is stored in 'user' field  
    """
    def has_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS:
            return True 
        return request.user == obj.user 
