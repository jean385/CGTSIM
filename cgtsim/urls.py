from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import (
    DemandeViewSet, 
    DashboardViewSet, 
    TransactionViewSet,
    get_current_user
)

router = DefaultRouter()
router.register(r'demandes', DemandeViewSet, basename='demande')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/me/', get_current_user, name='current_user'),
    path('', include(router.urls)),
]
