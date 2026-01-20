# Ajoute cette vue à la fin de ton fichier cgtsim/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Récupérer les informations de l'utilisateur connecté"""
    user = request.user
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'css': {
            'id': user.css.id,
            'code': user.css.code,
            'name': user.css.name,
        } if user.css else None,
    })
