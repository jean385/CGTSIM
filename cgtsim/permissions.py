from rest_framework import permissions


class IsAdminCGTSIM(permissions.BasePermission):
    """
    Permission pour vérifier si l'utilisateur est un admin CGTSIM
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin_cgtsim'
        )


class IsCSSUser(permissions.BasePermission):
    """
    Permission pour vérifier si l'utilisateur est un utilisateur CSS
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'user_css' and
            request.user.css is not None
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission pour vérifier si l'utilisateur est le propriétaire ou un admin
    """
    def has_object_permission(self, request, view, obj):
        # Admin a tous les droits
        if request.user.role == 'admin_cgtsim':
            return True
        
        # Utilisateur CSS peut voir uniquement ses objets
        if request.user.role == 'user_css':
            # Pour les demandes
            if hasattr(obj, 'css'):
                return obj.css == request.user.css
            # Pour les CSS elles-mêmes
            if hasattr(obj, 'users'):
                return request.user.css == obj
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    Permission en lecture seule
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
