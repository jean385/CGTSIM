from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour gérer les comptes CSS et CGTSIM
    """
    ROLE_CHOICES = [
        ('admin_cgtsim', 'Administrateur CGTSIM'),
        ('user_css', 'Utilisateur CSS'),
        ('viewer', 'Observateur'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user_css')
    css = models.ForeignKey('CSS', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    phone = models.CharField(max_length=20, blank=True)
    two_fa_enabled = models.BooleanField(default=False)
    two_fa_secret = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"


class CSS(models.Model):
    """
    Modèle pour les Caisses de Sécurité Sociale
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True, help_text="Ex: CSS001, CSSDM")
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Personne contact")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'css'
        verbose_name = 'CSS'
        verbose_name_plural = 'CSS'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class DemandeFonds(models.Model):
    """
    Modèle pour les demandes de fonds des CSS
    Une demande peut contenir plusieurs jours
    """
    STATUT_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
        ('versed', 'Fonds versés'),
        ('cancelled', 'Annulée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=20, unique=True, editable=False)
    css = models.ForeignKey(CSS, on_delete=models.CASCADE, related_name='demandes')
    
    # Informations générales
    description = models.TextField(verbose_name="Description générale", blank=True)
    document_justificatif = models.FileField(
        upload_to='demandes/justificatifs/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Montant total (calculé automatiquement depuis DemandeJour)
    montant_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant total",
        editable=False
    )
    
    # Workflow et statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='pending')
    date_demande = models.DateTimeField(auto_now_add=True)
    demande_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='demandes_creees'
    )
    
    # Révision
    revise_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_revisees'
    )
    date_revision = models.DateTimeField(null=True, blank=True)
    notes_revision = models.TextField(blank=True)
    
    # Versement
    date_versement = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'demandes_fonds'
        verbose_name = 'Demande de fonds'
        verbose_name_plural = 'Demandes de fonds'
        ordering = ['-date_demande']
        indexes = [
            models.Index(fields=['css', 'statut']),
            models.Index(fields=['reference']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.css.code} - {self.montant_total} CAD"
    
    def save(self, *args, **kwargs):
        # Générer la référence si elle n'existe pas
        if not self.reference:
            from django.db.models import Max
            import datetime
            
            year = datetime.datetime.now().year
            last_ref = DemandeFonds.objects.filter(
                reference__startswith=f'DEM-{year}-'
            ).aggregate(Max('reference'))['reference__max']
            
            if last_ref:
                last_num = int(last_ref.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.reference = f'DEM-{year}-{new_num:03d}'
        
        super().save(*args, **kwargs)
    
    def calculer_montant_total(self):
        """Recalculer le montant total depuis les jours associés"""
        from django.db.models import Sum
        
        total = self.jours.aggregate(
            total=Sum('montant_jour')
        )['total'] or Decimal('0.00')
        
        self.montant_total = total
        self.save(update_fields=['montant_total'])
        
        return total


class DemandeJour(models.Model):
    """
    Modèle pour un jour spécifique d'une demande de fonds
    Un jour peut contenir plusieurs lignes (items)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demande = models.ForeignKey(
        DemandeFonds, 
        on_delete=models.CASCADE, 
        related_name='jours'
    )
    date_besoin = models.DateField(verbose_name="Date où les fonds doivent être disponibles")
    
    # Montant total du jour (calculé automatiquement depuis les items)
    montant_jour = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Total du jour",
        editable=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'demandes_jours'
        verbose_name = 'Jour de demande'
        verbose_name_plural = 'Jours de demande'
        ordering = ['date_besoin']
        unique_together = ['demande', 'date_besoin']
        indexes = [
            models.Index(fields=['demande', 'date_besoin']),
            models.Index(fields=['date_besoin']),
        ]
    
    def __str__(self):
        return f"{self.demande.reference} - {self.date_besoin} - {self.montant_jour} CAD"
    
    def calculer_montant_jour(self):
        """Recalculer le montant du jour depuis les items"""
        from django.db.models import Sum
        
        total = self.items.aggregate(
            total=Sum('montant')
        )['total'] or Decimal('0.00')
        
        self.montant_jour = total
        self.save(update_fields=['montant_jour'])
        
        # Mettre à jour le montant total de la demande
        if self.demande_id:
            self.demande.calculer_montant_total()
        
        return total


class DemandeItem(models.Model):
    """
    Modèle pour une ligne de montant dans un jour
    Chaque jour peut avoir plusieurs items (lignes)
    """
    CATEGORIE_CHOICES = [
        ('fonctionnement', 'Fonctionnement'),
        ('investissement', 'Investissement'),
        ('sqi', 'SQI'),
        ('ebi', 'EBI'),
    ]
    
    TYPE_PAIEMENT_CHOICES = [
        ('fournisseurs_dd', 'Fournisseurs Dépôt Direct'),
        ('fournisseurs_cheque', 'Fournisseurs Chèques'),
        ('salaires_dd', 'Salaires Dépôt Direct'),
        ('salaires_cheque', 'Salaires Chèques'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jour = models.ForeignKey(
        DemandeJour, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    
    # Montant et catégories
    montant = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )
    categorie = models.CharField(
        max_length=20, 
        choices=CATEGORIE_CHOICES,
        verbose_name="Catégorie"
    )
    type_paiement = models.CharField(
        max_length=30, 
        choices=TYPE_PAIEMENT_CHOICES,
        verbose_name="Type de paiement"
    )
    description = models.CharField(
        max_length=500, 
        blank=True,
        verbose_name="Description"
    )
    
    # Ordre d'affichage dans le jour
    ordre = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'demandes_items'
        verbose_name = 'Ligne de demande'
        verbose_name_plural = 'Lignes de demande'
        ordering = ['ordre', 'created_at']
        indexes = [
            models.Index(fields=['jour', 'ordre']),
            models.Index(fields=['categorie']),
        ]
    
    def __str__(self):
        return f"{self.get_categorie_display()} - {self.montant} CAD - {self.jour.date_besoin}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Recalculer le montant du jour
        if self.jour_id:
            self.jour.calculer_montant_jour()


class Avance(models.Model):
    """
    Modèle pour les avances actives (une fois la demande approuvée et versée)
    """
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Clôturée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=20, unique=True, editable=False)
    css = models.ForeignKey(CSS, on_delete=models.CASCADE, related_name='avances')
    demande = models.OneToOneField(
        DemandeFonds,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='avance_liee'
    )
    
    montant_principal = models.DecimalField(max_digits=15, decimal_places=2)
    taux_interet = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        help_text="Taux annuel en pourcentage (ex: 4.500)"
    )
    date_debut = models.DateField()
    date_fin_prevue = models.DateField(null=True, blank=True)
    date_fin_reelle = models.DateField(null=True, blank=True)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    
    interets_courus = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Intérêts cumulés à ce jour"
    )
    derniere_maj_interets = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'avances'
        verbose_name = 'Avance'
        verbose_name_plural = 'Avances'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.reference} - {self.css.code} - {self.montant_principal} CAD"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            from django.db.models import Max
            import datetime
            
            year = datetime.datetime.now().year
            last_ref = Avance.objects.filter(
                reference__startswith=f'AVN-{year}-'
            ).aggregate(Max('reference'))['reference__max']
            
            if last_ref:
                last_num = int(last_ref.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.reference = f'AVN-{year}-{new_num:03d}'
        
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """
    Modèle pour toutes les transactions financières
    """
    TYPE_CHOICES = [
        ('avance', 'Avance'),
        ('subvention', 'Subvention'),
        ('interet', 'Intérêt'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    css = models.ForeignKey(CSS, on_delete=models.CASCADE, related_name='transactions')
    
    type_transaction = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Positif pour avances/intérêts, négatif pour subventions"
    )
    
    date_transaction = models.DateField(verbose_name="Date de la transaction")
    reference = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    demande = models.ForeignKey(
        'DemandeFonds',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    avance = models.ForeignKey(
        'Avance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    creee_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions_creees'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date_transaction', '-created_at']
        indexes = [
            models.Index(fields=['css', 'date_transaction']),
            models.Index(fields=['type_transaction']),
        ]
    
    def __str__(self):
        signe = '+' if self.montant >= 0 else ''
        return f"{self.css.code} - {self.get_type_transaction_display()} - {signe}{self.montant} CAD"
    
    def save(self, *args, **kwargs):
        if not self.reference and self.type_transaction == 'subvention':
            from django.db.models import Max
            import datetime
            
            year = datetime.datetime.now().year
            month = self.date_transaction.month
            
            last_ref = Transaction.objects.filter(
                type_transaction='subvention',
                reference__startswith=f'SUB-{year}-{month:02d}-'
            ).aggregate(Max('reference'))['reference__max']
            
            if last_ref:
                last_num = int(last_ref.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.reference = f'SUB-{year}-{month:02d}-{new_num:03d}'
        
        super().save(*args, **kwargs)
