from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal

from .models import CSS, DemandeFonds, DemandeJour, DemandeItem, User, Avance, Transaction
from .serializers import (
    DemandeCreateSerializer,
    DemandeListSerializer,
    DemandeDetailSerializer,
    TransactionSerializer,
    TransactionCreateSerializer
)
from .permissions import IsAdminCGTSIM, IsCSSUser


class DemandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les demandes de fonds
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les demandes selon le rôle de l'utilisateur"""
        user = self.request.user
        
        if user.role == 'admin_cgtsim':
            # Admin voit toutes les demandes
            return DemandeFonds.objects.all().select_related(
                'css', 'demande_par'
            ).prefetch_related(
                'jours__items'
            )
        elif user.role == 'user_css' and user.css:
            # CSS voit uniquement ses propres demandes
            return DemandeFonds.objects.filter(css=user.css).select_related(
                'css', 'demande_par'
            ).prefetch_related(
                'jours__items'
            )
        else:
            return DemandeFonds.objects.none()
    
    def get_serializer_class(self):
        """Utiliser le bon serializer selon l'action"""
        if self.action == 'create':
            return DemandeCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return DemandeDetailSerializer
        else:
            return DemandeListSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsCSSUser])
    def mes_demandes(self, request):
        """Liste des demandes de l'utilisateur CSS connecté"""
        demandes = self.get_queryset().filter(css=request.user.css)
        serializer = DemandeListSerializer(demandes, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques sur les demandes"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'par_statut': dict(
                queryset.values('statut').annotate(
                    count=Count('id')
                ).values_list('statut', 'count')
            ),
            'montant_total': float(
                queryset.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
            ),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminCGTSIM])
    def approve(self, request, pk=None):
        """Approuver ou rejeter une demande (Admin uniquement)"""
        demande = self.get_object()
        
        new_statut = request.data.get('statut')
        if new_statut not in ['approved', 'rejected']:
            return Response(
                {'error': 'Le statut doit être "approved" ou "rejected"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        demande.statut = new_statut
        demande.revise_par = request.user
        demande.date_revision = datetime.now()
        demande.notes_revision = request.data.get('notes_revision', '')
        
        # Si approuvée, créer automatiquement une avance et une transaction
        if new_statut == 'approved':
            # Utiliser la première date de besoin comme date de début
            premier_jour = demande.jours.order_by('date_besoin').first()
            date_versement = premier_jour.date_besoin if premier_jour else demande.date_demande.date()
            
            # Créer l'avance
            avance = Avance.objects.create(
                css=demande.css,
                demande=demande,
                montant_principal=demande.montant_total,
                taux_interet=Decimal('4.5'),  # Taux par défaut
                date_debut=date_versement,
                statut='active'
            )
            
            # Créer une transaction d'avance
            Transaction.objects.create(
                css=demande.css,
                type_transaction='avance',
                montant=demande.montant_total,  # Positif
                date_transaction=date_versement,
                reference=demande.reference,
                description=f"Avance pour demande {demande.reference}",
                demande=demande,
                avance=avance,
                creee_par=request.user
            )
            
            demande.save()
            
            return Response({
                'message': 'Demande approuvée avec succès',
                'demande': DemandeDetailSerializer(demande, context={'request': request}).data,
                'avance_reference': avance.reference
            })
        
        demande.save()
        return Response({
            'message': 'Demande rejetée',
            'demande': DemandeDetailSerializer(demande, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminCGTSIM])
    def marquer_verse(self, request, pk=None):
        """Marquer une demande comme versée"""
        demande = self.get_object()
        
        if demande.statut != 'approved':
            return Response(
                {'error': 'Seules les demandes approuvées peuvent être marquées comme versées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        demande.statut = 'versed'
        demande.date_versement = request.data.get('date_versement', datetime.now().date())
        demande.save()
        
        return Response({
            'message': 'Demande marquée comme versée',
            'demande': DemandeDetailSerializer(demande, context={'request': request}).data
        })


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet pour les statistiques du dashboard
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsCSSUser])
    def stats_css(self, request):
        """Statistiques pour l'utilisateur CSS"""
        css = request.user.css
        
        demandes = DemandeFonds.objects.filter(css=css)
        
        stats = {
            'total_demandes': demandes.count(),
            'demandes_pending': demandes.filter(statut='pending').count(),
            'demandes_approved': demandes.filter(statut='approved').count(),
            'montant_total_demandes': float(
                demandes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
            ),
            'total_fonds_verses': demandes.filter(statut='versed').count(),
            'montant_total_verses': float(
                demandes.filter(statut='versed').aggregate(
                    Sum('montant_total')
                )['montant_total__sum'] or 0
            ),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminCGTSIM])
    def stats_cgtsim(self, request):
        """Statistiques globales pour l'admin CGTSIM"""
        
        all_demandes = DemandeFonds.objects.all()
        all_avances = Avance.objects.all()
        
        stats = {
            'demandes': {
                'total': all_demandes.count(),
                'pending': all_demandes.filter(statut='pending').count(),
                'approved': all_demandes.filter(statut='approved').count(),
                'versed': all_demandes.filter(statut='versed').count(),
                'rejected': all_demandes.filter(statut='rejected').count(),
            },
            'avances': {
                'total': all_avances.count(),
                'actives': all_avances.filter(statut='active').count(),
                'montant_total': float(
                    all_avances.aggregate(
                        Sum('montant_principal')
                    )['montant_principal__sum'] or 0
                ),
            },
            'css_actives': CSS.objects.filter(is_active=True).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminCGTSIM])
    def tresorerie(self, request):
        """Calcul des besoins de liquidités"""
        today = datetime.now().date()
        
        # Besoins pour les 7 prochains jours
        jours_7j = DemandeJour.objects.filter(
            demande__statut='approved',
            date_besoin__gte=today,
            date_besoin__lte=today + timedelta(days=7)
        ).select_related('demande', 'demande__css').order_by('date_besoin')
        
        liste_7j = [{
            'reference': jour.demande.reference,
            'css_name': jour.demande.css.name,
            'date_besoin': jour.date_besoin,
            'montant': float(jour.montant_jour)
        } for jour in jours_7j]
        
        # Total des décaissements prévus sur 30 jours
        total_30j = DemandeJour.objects.filter(
            demande__statut='approved',
            date_besoin__gte=today,
            date_besoin__lte=today + timedelta(days=30)
        ).aggregate(total=Sum('montant_jour'))['total'] or Decimal('0.00')
        
        return Response({
            'decaissements_7j': liste_7j,
            'decaissements_30j': float(total_30j),
            'date_calcul': today.isoformat(),
        })


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les transactions (principalement subventions)
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les transactions selon le rôle"""
        user = self.request.user
        
        if user.role == 'admin_cgtsim':
            queryset = Transaction.objects.all().select_related(
                'css', 'creee_par', 'demande', 'avance'
            )
        elif user.role == 'user_css' and user.css:
            queryset = Transaction.objects.filter(css=user.css).select_related(
                'css', 'creee_par', 'demande', 'avance'
            )
        else:
            queryset = Transaction.objects.none()
        
        # Filtres optionnels
        css_id = self.request.query_params.get('css', None)
        type_transaction = self.request.query_params.get('type', None)
        date_debut = self.request.query_params.get('date_debut', None)
        date_fin = self.request.query_params.get('date_fin', None)
        
        if css_id:
            queryset = queryset.filter(css_id=css_id)
        if type_transaction:
            queryset = queryset.filter(type_transaction=type_transaction)
        if date_debut:
            queryset = queryset.filter(date_transaction__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_transaction__lte=date_fin)
        
        return queryset
    
    def get_serializer_class(self):
        """Utiliser le bon serializer selon l'action"""
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        """Enregistrer l'utilisateur qui a créé la transaction"""
        serializer.save(creee_par=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def par_css(self, request):
        """Obtenir les transactions groupées par CSS avec soldes"""
        
        if request.user.role != 'admin_cgtsim':
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculer le solde pour chaque CSS
        css_list = CSS.objects.filter(is_active=True)
        resultats = []
        
        for css in css_list:
            transactions = Transaction.objects.filter(css=css)
            
            solde_total = transactions.aggregate(
                total=Sum('montant')
            )['total'] or Decimal('0.00')
            
            avances = transactions.filter(type_transaction='avance').aggregate(
                total=Sum('montant')
            )['total'] or Decimal('0.00')
            
            subventions = transactions.filter(type_transaction='subvention').aggregate(
                total=Sum('montant')
            )['total'] or Decimal('0.00')
            
            interets = transactions.filter(type_transaction='interet').aggregate(
                total=Sum('montant')
            )['total'] or Decimal('0.00')
            
            resultats.append({
                'css_id': str(css.id),
                'css_code': css.code,
                'css_name': css.name,
                'solde_actuel': float(solde_total),
                'total_avances': float(avances),
                'total_subventions': float(subventions),
                'total_interets': float(interets),
                'nb_transactions': transactions.count(),
            })
        
        # Trier par solde décroissant
        resultats.sort(key=lambda x: x['solde_actuel'], reverse=True)
        
        return Response(resultats)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques globales sur les transactions"""
        
        queryset = self.get_queryset()
        
        stats = {
            'total_transactions': queryset.count(),
            'total_avances': float(
                queryset.filter(type_transaction='avance').aggregate(
                    Sum('montant')
                )['montant__sum'] or Decimal('0.00')
            ),
            'total_subventions': float(
                queryset.filter(type_transaction='subvention').aggregate(
                    Sum('montant')
                )['montant__sum'] or Decimal('0.00')
            ),
            'total_interets': float(
                queryset.filter(type_transaction='interet').aggregate(
                    Sum('montant')
                )['montant__sum'] or Decimal('0.00')
            ),
            'par_type': dict(
                queryset.values('type_transaction').annotate(
                    count=Count('id')
                ).values_list('type_transaction', 'count')
            ),
        }
        
        return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Récupérer les informations de l'utilisateur connecté"""
    user = request.user
    
    return Response({
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'css': {
            'id': str(user.css.id),
            'code': user.css.code,
            'name': user.css.name,
        } if user.css else None,
    })
