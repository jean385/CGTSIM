from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CSS, DemandeFonds, DemandeJour, DemandeItem, Avance, Transaction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'css', 'is_active']
    list_filter = ['role', 'is_active', 'css']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations CGTSIM', {
            'fields': ('role', 'css', 'phone', 'two_fa_enabled')
        }),
    )


@admin.register(CSS)
class CSSAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'contact_email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'contact_person']
    ordering = ['code']


class DemandeItemInline(admin.TabularInline):
    model = DemandeItem
    extra = 0
    fields = [
        'ordre', 'montant', 'categorie', 
        'type_paiement', 'description'
    ]
    ordering = ['ordre']


class DemandeJourInline(admin.TabularInline):
    model = DemandeJour
    extra = 0
    readonly_fields = ['montant_jour']
    fields = ['date_besoin', 'montant_jour']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('items')


@admin.register(DemandeFonds)
class DemandeAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'css', 'montant_total', 
        'nb_jours', 'nb_items', 'statut', 'date_demande'
    ]
    list_filter = ['statut', 'css', 'date_demande']
    search_fields = ['reference', 'css__name', 'css__code', 'description']
    readonly_fields = [
        'reference', 'montant_total', 'date_demande', 
        'created_at', 'updated_at'
    ]
    
    inlines = [DemandeJourInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('reference', 'css', 'description', 'document_justificatif')
        }),
        ('Total et Workflow', {
            'fields': ('montant_total', 'statut', 'demande_par', 'date_demande')
        }),
        ('Révision', {
            'fields': ('revise_par', 'date_revision', 'notes_revision')
        }),
        ('Versement', {
            'fields': ('date_versement',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def nb_jours(self, obj):
        return obj.jours.count()
    nb_jours.short_description = 'Nb jours'
    
    def nb_items(self, obj):
        total = 0
        for jour in obj.jours.all():
            total += jour.items.count()
        return total
    nb_items.short_description = 'Nb lignes'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle demande
            obj.demande_par = request.user
        super().save_model(request, obj, form, change)


@admin.register(DemandeJour)
class DemandeJourAdmin(admin.ModelAdmin):
    list_display = ['demande', 'date_besoin', 'montant_jour', 'nb_items']
    list_filter = ['date_besoin']
    search_fields = ['demande__reference']
    readonly_fields = ['montant_jour']
    date_hierarchy = 'date_besoin'
    
    inlines = [DemandeItemInline]
    
    def nb_items(self, obj):
        return obj.items.count()
    nb_items.short_description = 'Nb lignes'


@admin.register(DemandeItem)
class DemandeItemAdmin(admin.ModelAdmin):
    list_display = [
        'jour', 'ordre', 'montant', 'categorie', 
        'type_paiement', 'description'
    ]
    list_filter = ['categorie', 'type_paiement']
    search_fields = ['description', 'jour__demande__reference']
    ordering = ['jour__date_besoin', 'ordre']


@admin.register(Avance)
class AvanceAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'css', 'montant_principal', 
        'taux_interet', 'statut', 'date_debut'
    ]
    list_filter = ['statut', 'css']
    search_fields = ['reference', 'css__name', 'css__code']
    readonly_fields = ['reference', 'interets_courus', 'created_at', 'updated_at']
    date_hierarchy = 'date_debut'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('reference', 'css', 'demande')
        }),
        ('Montants et taux', {
            'fields': ('montant_principal', 'taux_interet', 'interets_courus')
        }),
        ('Dates', {
            'fields': (
                'date_debut', 'date_fin_prevue', 
                'date_fin_reelle', 'derniere_maj_interets'
            )
        }),
        ('Statut et notes', {
            'fields': ('statut', 'notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'css', 'type_transaction', 
        'montant', 'date_transaction', 'creee_par'
    ]
    list_filter = ['type_transaction', 'css', 'date_transaction']
    search_fields = ['reference', 'css__name', 'css__code', 'description']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'creee_par']
    date_hierarchy = 'date_transaction'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('reference', 'css', 'type_transaction', 'date_transaction')
        }),
        ('Montant et description', {
            'fields': ('montant', 'description')
        }),
        ('Liens optionnels', {
            'fields': ('demande', 'avance')
        }),
        ('Audit', {
            'fields': ('creee_par', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle transaction
            obj.creee_par = request.user
        super().save_model(request, obj, form, change)
