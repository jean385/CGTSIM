from rest_framework import serializers
from decimal import Decimal
from datetime import datetime, timedelta
from .models import (
    DemandeFonds, DemandeJour, DemandeItem, 
    Transaction, Avance, CSS
)


class DemandeItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items (lignes) de demande"""
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    type_paiement_display = serializers.CharField(source='get_type_paiement_display', read_only=True)
    
    class Meta:
        model = DemandeItem
        fields = [
            'id', 'montant', 'categorie', 'categorie_display',
            'type_paiement', 'type_paiement_display', 
            'description', 'ordre'
        ]


class DemandeJourSerializer(serializers.ModelSerializer):
    """Serializer pour les jours de demande"""
    items = DemandeItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = DemandeJour
        fields = ['id', 'date_besoin', 'montant_jour', 'items']
        read_only_fields = ['montant_jour']


class DemandeJourCreateSerializer(serializers.Serializer):
    """Serializer pour la création d'un jour avec validation"""
    date_besoin = serializers.DateField()
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=20
    )
    
    def validate_date_besoin(self, value):
        """Valider que la date est un jour ouvrable et dans les limites"""
        today = datetime.now().date()
        
        # Date minimum : prochain jour ouvrable
        next_day = today + timedelta(days=1)
        while next_day.weekday() >= 5:  # 5=samedi, 6=dimanche
            next_day += timedelta(days=1)
        
        if value < next_day:
            raise serializers.ValidationError(
                f"La date doit être au minimum le {next_day.strftime('%Y-%m-%d')} (prochain jour ouvrable)"
            )
        
        # Date maximum : 30 jours dans le futur
        max_date = today + timedelta(days=30)
        if value > max_date:
            raise serializers.ValidationError(
                f"La date ne peut pas dépasser {max_date.strftime('%Y-%m-%d')} (30 jours maximum)"
            )
        
        # Pas de weekends
        if value.weekday() >= 5:
            raise serializers.ValidationError(
                "La date ne peut pas être un samedi ou un dimanche"
            )
        
        return value
    
    def validate_items(self, value):
        """Valider les items (lignes) du jour"""
        if not value:
            raise serializers.ValidationError("Au moins une ligne est requise")
        
        if len(value) > 20:
            raise serializers.ValidationError("Maximum 20 lignes par jour")
        
        for idx, item in enumerate(value):
            # Vérifier les champs requis
            if 'montant' not in item:
                raise serializers.ValidationError(f"Ligne {idx+1}: Le montant est requis")
            if 'categorie' not in item:
                raise serializers.ValidationError(f"Ligne {idx+1}: La catégorie est requise")
            if 'type_paiement' not in item:
                raise serializers.ValidationError(f"Ligne {idx+1}: Le type de paiement est requis")
            
            # Valider le montant (PEUT ÊTRE NÉGATIF maintenant)
            try:
                montant = Decimal(str(item['montant']))
                # Plus de validation montant > 0 - on accepte les négatifs
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Ligne {idx+1}: Montant invalide")
            
            # Valider la catégorie
            categories_valides = ['fonctionnement', 'investissement', 'sqi', 'ebi']
            if item['categorie'] not in categories_valides:
                raise serializers.ValidationError(
                    f"Ligne {idx+1}: Catégorie invalide. Choix: {', '.join(categories_valides)}"
                )
            
            # Valider le type de paiement
            types_valides = ['fournisseurs_dd', 'fournisseurs_cheque', 'salaires_dd', 'salaires_cheque']
            if item['type_paiement'] not in types_valides:
                raise serializers.ValidationError(
                    f"Ligne {idx+1}: Type de paiement invalide. Choix: {', '.join(types_valides)}"
                )
        
        return value


class DemandeCreateSerializer(serializers.Serializer):
    """Serializer pour la création d'une demande complète"""
    description = serializers.CharField(required=False, allow_blank=True, max_length=500)
    jours = DemandeJourCreateSerializer(many=True)
    
    def validate_jours(self, value):
        """Valider les jours de la demande"""
        if not value:
            raise serializers.ValidationError("Au moins une date est requise")
        
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 dates par demande")
        
        # Vérifier qu'il n'y a pas de dates en double
        dates = [jour['date_besoin'] for jour in value]
        if len(dates) != len(set(dates)):
            raise serializers.ValidationError("Dates en double détectées")
        
        # Vérifier qu'au moins un item a un montant non-nul
        has_amount = False
        for jour in value:
            for item in jour['items']:
                if Decimal(str(item['montant'])) != 0:
                    has_amount = True
                    break
            if has_amount:
                break
        
        if not has_amount:
            raise serializers.ValidationError("Au moins un montant non-nul est requis")
        
        return value
    
    def create(self, validated_data):
        """Créer la demande avec ses jours et items"""
        jours_data = validated_data.pop('jours')
        user = self.context['request'].user
        
        # Créer la demande principale
        demande = DemandeFonds.objects.create(
            css=user.css,
            demande_par=user,
            description=validated_data.get('description', ''),
            statut='pending'
        )
        
        # Créer les jours et items
        for jour_data in jours_data:
            items_data = jour_data.pop('items')
            
            jour = DemandeJour.objects.create(
                demande=demande,
                date_besoin=jour_data['date_besoin']
            )
            
            for idx, item_data in enumerate(items_data):
                DemandeItem.objects.create(
                    jour=jour,
                    montant=Decimal(str(item_data['montant'])),
                    categorie=item_data['categorie'],
                    type_paiement=item_data['type_paiement'],
                    description=item_data.get('description', ''),
                    ordre=idx
                )
        
        # Les montants se calculent automatiquement via les signals/méthodes
        demande.refresh_from_db()
        return demande
    
    def to_representation(self, instance):
        """
        Utiliser DemandeDetailSerializer pour la représentation
        AVEC prefetch des relations pour éviter l'erreur 'RelatedManager not iterable'
        """
        # Recharger l'instance avec les relations prefetch
        demande = DemandeFonds.objects.prefetch_related(
            'jours__items'
        ).get(pk=instance.pk)
        
        return DemandeDetailSerializer(demande, context=self.context).data


class DemandeListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des demandes"""
    css_code = serializers.CharField(source='css.code', read_only=True)
    css_name = serializers.CharField(source='css.name', read_only=True)
    nb_jours = serializers.SerializerMethodField()
    nb_items = serializers.SerializerMethodField()
    dates_besoins = serializers.SerializerMethodField()
    
    class Meta:
        model = DemandeFonds
        fields = [
            'id', 'reference', 'css', 'css_code', 'css_name',
            'description', 'montant_total', 'statut',
            'date_demande', 'nb_jours', 'nb_items', 'dates_besoins'
        ]
    
    def get_nb_jours(self, obj):
        return obj.jours.count()
    
    def get_nb_items(self, obj):
        total = 0
        for jour in obj.jours.all():
            total += jour.items.count()
        return total
    
    def get_dates_besoins(self, obj):
        return [jour.date_besoin.isoformat() for jour in obj.jours.all().order_by('date_besoin')]


class DemandeDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une demande"""
    css_code = serializers.CharField(source='css.code', read_only=True)
    css_name = serializers.CharField(source='css.name', read_only=True)
    demande_par_name = serializers.SerializerMethodField()
    revise_par_name = serializers.SerializerMethodField()
    jours = DemandeJourSerializer(many=True, read_only=True)
    total_par_categorie = serializers.SerializerMethodField()
    
    class Meta:
        model = DemandeFonds
        fields = [
            'id', 'reference', 'css', 'css_code', 'css_name',
            'description', 'montant_total', 'statut',
            'date_demande', 'demande_par', 'demande_par_name',
            'date_revision', 'revise_par', 'revise_par_name',
            'notes_revision', 'date_versement',
            'jours', 'total_par_categorie'
        ]
    
    def get_demande_par_name(self, obj):
        if obj.demande_par:
            return f"{obj.demande_par.first_name} {obj.demande_par.last_name}"
        return None
    
    def get_revise_par_name(self, obj):
        if obj.revise_par:
            return f"{obj.revise_par.first_name} {obj.revise_par.last_name}"
        return None
    
    def get_total_par_categorie(self, obj):
        """Calculer le total par catégorie"""
        totaux = {
            'fonctionnement': Decimal('0.00'),
            'investissement': Decimal('0.00'),
            'sqi': Decimal('0.00'),
            'ebi': Decimal('0.00')
        }
        
        for jour in obj.jours.all():
            for item in jour.items.all():
                totaux[item.categorie] += item.montant
        
        return {k: float(v) for k, v in totaux.items()}


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer pour les transactions"""
    css_code = serializers.CharField(source='css.code', read_only=True)
    css_name = serializers.CharField(source='css.name', read_only=True)
    type_transaction_display = serializers.CharField(source='get_type_transaction_display', read_only=True)
    creee_par_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'css', 'css_code', 'css_name',
            'type_transaction', 'type_transaction_display',
            'montant', 'date_transaction', 'description',
            'demande', 'avance', 'creee_par', 'creee_par_name',
            'created_at'
        ]
    
    def get_creee_par_name(self, obj):
        if obj.creee_par:
            return f"{obj.creee_par.first_name} {obj.creee_par.last_name}"
        return None


class TransactionCreateSerializer(serializers.Serializer):
    """Serializer pour créer une transaction (subvention)"""
    css = serializers.UUIDField()
    type_transaction = serializers.ChoiceField(choices=['subvention'])
    montant = serializers.DecimalField(max_digits=12, decimal_places=2)
    date_transaction = serializers.DateField()
    reference = serializers.CharField(max_length=50, required=False, allow_blank=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_css(self, value):
        """Vérifier que le CSS existe"""
        try:
            css = CSS.objects.get(id=value)
            return css
        except CSS.DoesNotExist:
            raise serializers.ValidationError("CSS introuvable")
    
    def validate_montant(self, value):
        """Le montant doit être négatif pour une subvention"""
        if value >= 0:
            raise serializers.ValidationError(
                "Le montant d'une subvention doit être négatif (entrez un nombre positif, il sera converti automatiquement)"
            )
        return value
    
    def create(self, validated_data):
        """Créer la transaction"""
        css = validated_data['css']
        user = self.context['request'].user
        
        transaction = Transaction.objects.create(
            css=css,
            type_transaction='subvention',
            montant=validated_data['montant'],
            date_transaction=validated_data['date_transaction'],
            reference=validated_data.get('reference', ''),
            description=validated_data.get('description', ''),
            creee_par=user
        )
        
        return transaction
