from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from .models import Avance, InteretAvance, EmpruntBanque, InteretEmprunt


def calculer_interets_quotidiens(date_calcul=None):
    """
    Calculer les intérêts quotidiens pour toutes les avances actives
    
    Args:
        date_calcul: Date pour laquelle calculer les intérêts (par défaut aujourd'hui)
    
    Returns:
        dict: Résultats du calcul avec le nombre d'avances traitées et le total des intérêts
    """
    if date_calcul is None:
        date_calcul = timezone.now().date()
    
    avances_actives = Avance.objects.filter(
        statut='active',
        date_debut__lte=date_calcul
    )
    
    total_interets = Decimal('0.00')
    avances_traitees = 0
    
    with transaction.atomic():
        for avance in avances_actives:
            # Vérifier si le calcul n'a pas déjà été fait pour cette date
            if InteretAvance.objects.filter(
                avance=avance,
                date_calcul=date_calcul
            ).exists():
                continue
            
            # Calculer le taux quotidien (base 365 jours)
            taux_quotidien = avance.taux_interet / Decimal('365.0')
            
            # Intérêt du jour = capital × taux_quotidien / 100
            interet_jour = (avance.montant_principal * taux_quotidien) / Decimal('100.0')
            
            # Obtenir les intérêts cumulés jusqu'à hier
            dernier_calcul = InteretAvance.objects.filter(
                avance=avance,
                date_calcul__lt=date_calcul
            ).order_by('-date_calcul').first()
            
            if dernier_calcul:
                interets_cumules = dernier_calcul.interets_cumules + interet_jour
            else:
                interets_cumules = interet_jour
            
            # Créer l'enregistrement du calcul
            InteretAvance.objects.create(
                avance=avance,
                date_calcul=date_calcul,
                solde_jour=avance.montant_principal,
                taux_quotidien=taux_quotidien / Decimal('100.0'),
                interet_jour=interet_jour,
                interets_cumules=interets_cumules
            )
            
            # Mettre à jour l'avance
            avance.interets_courus = interets_cumules
            avance.derniere_maj_interets = date_calcul
            avance.save(update_fields=['interets_courus', 'derniere_maj_interets'])
            
            total_interets += interet_jour
            avances_traitees += 1
    
    return {
        'avances_traitees': avances_traitees,
        'interets_total': total_interets,
        'date_calcul': date_calcul
    }


def calculer_interets_emprunts(date_calcul=None):
    """
    Calculer les intérêts quotidiens pour tous les emprunts actifs
    
    Args:
        date_calcul: Date pour laquelle calculer les intérêts
    
    Returns:
        dict: Résultats du calcul
    """
    if date_calcul is None:
        date_calcul = timezone.now().date()
    
    emprunts_actifs = EmpruntBanque.objects.filter(
        statut='active',
        date_debut__lte=date_calcul,
        date_echeance__gte=date_calcul
    )
    
    total_interets = Decimal('0.00')
    emprunts_traites = 0
    
    with transaction.atomic():
        for emprunt in emprunts_actifs:
            # Vérifier si le calcul n'a pas déjà été fait
            if InteretEmprunt.objects.filter(
                emprunt=emprunt,
                date_calcul=date_calcul
            ).exists():
                continue
            
            # Calculer le taux quotidien
            taux_quotidien = emprunt.taux_interet / Decimal('365.0')
            
            # Intérêt du jour
            interet_jour = (emprunt.montant * taux_quotidien) / Decimal('100.0')
            
            # Intérêts cumulés
            dernier_calcul = InteretEmprunt.objects.filter(
                emprunt=emprunt,
                date_calcul__lt=date_calcul
            ).order_by('-date_calcul').first()
            
            if dernier_calcul:
                interets_cumules = dernier_calcul.interets_cumules + interet_jour
            else:
                interets_cumules = interet_jour
            
            # Créer l'enregistrement
            InteretEmprunt.objects.create(
                emprunt=emprunt,
                date_calcul=date_calcul,
                solde_jour=emprunt.montant,
                taux_quotidien=taux_quotidien / Decimal('100.0'),
                interet_jour=interet_jour,
                interets_cumules=interets_cumules
            )
            
            # Mettre à jour l'emprunt
            emprunt.interets_courus = interets_cumules
            emprunt.save(update_fields=['interets_courus'])
            
            total_interets += interet_jour
            emprunts_traites += 1
    
    return {
        'emprunts_traites': emprunts_traites,
        'interets_total': total_interets,
        'date_calcul': date_calcul
    }


def calculer_marge_css(css, date_debut=None, date_fin=None):
    """
    Calculer la marge (profit) générée par une CSS sur une période
    
    Args:
        css: Instance de CSS
        date_debut: Date de début de la période
        date_fin: Date de fin de la période
    
    Returns:
        dict: Détails de la marge avec revenus et coûts
    """
    if date_fin is None:
        date_fin = timezone.now().date()
    
    if date_debut is None:
        # Par défaut, dernier mois
        date_debut = date_fin - timedelta(days=30)
    
    # Obtenir toutes les avances de la CSS actives pendant la période
    avances = Avance.objects.filter(
        css=css,
        date_debut__lte=date_fin
    ).filter(
        models.Q(date_fin_reelle__gte=date_debut) | 
        models.Q(date_fin_reelle__isnull=True, statut='active')
    )
    
    # Intérêts facturés (revenus)
    interets_factures = InteretAvance.objects.filter(
        avance__in=avances,
        date_calcul__gte=date_debut,
        date_calcul__lte=date_fin
    ).aggregate(
        total=models.Sum('interet_jour')
    )['total'] or Decimal('0.00')
    
    # Pour calculer les coûts, il faudrait lier chaque avance à un emprunt spécifique
    # Pour l'instant, on fait une approximation avec le taux moyen des emprunts
    
    # Taux moyen des emprunts actifs
    emprunts_actifs = EmpruntBanque.objects.filter(
        statut='active',
        date_debut__lte=date_fin,
        date_echeance__gte=date_debut
    )
    
    if emprunts_actifs.exists():
        taux_moyen_emprunt = emprunts_actifs.aggregate(
            avg_taux=models.Avg('taux_interet')
        )['avg_taux'] or Decimal('0.00')
    else:
        taux_moyen_emprunt = Decimal('0.00')
    
    # Calculer le coût estimé basé sur le capital moyen de la CSS
    capital_moyen = avances.aggregate(
        avg_capital=models.Avg('montant_principal')
    )['avg_capital'] or Decimal('0.00')
    
    nb_jours = (date_fin - date_debut).days + 1
    cout_estime = (capital_moyen * taux_moyen_emprunt * Decimal(nb_jours)) / (Decimal('365.0') * Decimal('100.0'))
    
    # Marge nette
    marge_nette = interets_factures - cout_estime
    
    # Taux de marge
    if interets_factures > 0:
        taux_marge = (marge_nette / interets_factures) * Decimal('100.0')
    else:
        taux_marge = Decimal('0.00')
    
    return {
        'css_code': css.code,
        'css_name': css.name,
        'periode': {
            'debut': date_debut,
            'fin': date_fin,
            'jours': nb_jours
        },
        'revenus': {
            'interets_factures': float(interets_factures),
        },
        'couts': {
            'cout_financement_estime': float(cout_estime),
            'taux_moyen_emprunt': float(taux_moyen_emprunt)
        },
        'marge': {
            'marge_nette': float(marge_nette),
            'taux_marge': float(taux_marge)
        }
    }


def calculer_besoin_liquidites(jours=7):
    """
    Calculer le besoin de liquidités pour les N prochains jours
    
    Args:
        jours: Nombre de jours à prévoir
    
    Returns:
        dict: Détail des besoins de liquidités
    """
    from .models import DemandeFonds, SoldeQuotidien, CompteBancaire
    
    today = timezone.now().date()
    date_limite = today + timedelta(days=jours)
    
    # Décaissements prévus (demandes approuvées)
    demandes_approuvees = DemandeFonds.objects.filter(
        statut='approved',
        date_besoins__gte=today,
        date_besoins__lte=date_limite
    )
    
    decaissements_par_jour = {}
    total_decaissements = Decimal('0.00')
    
    for demande in demandes_approuvees:
        date_str = demande.date_besoins.isoformat()
        if date_str not in decaissements_par_jour:
            decaissements_par_jour[date_str] = {
                'date': demande.date_besoins,
                'montant': Decimal('0.00'),
                'demandes': []
            }
        
        decaissements_par_jour[date_str]['montant'] += demande.montant
        decaissements_par_jour[date_str]['demandes'].append({
            'reference': demande.reference,
            'css': demande.css.name,
            'montant': float(demande.montant)
        })
        
        total_decaissements += demande.montant
    
    # Soldes actuels des comptes
    soldes_today = SoldeQuotidien.objects.filter(
        date_solde=today,
        compte__is_active=True
    )
    
    solde_total = soldes_today.aggregate(
        total=models.Sum('solde_fermeture')
    )['total'] or Decimal('0.00')
    
    # Calculer le besoin
    besoin_net = total_decaissements - solde_total
    
    if besoin_net > 0:
        besoin_status = 'emprunt_necessaire'
    elif besoin_net < 0:
        besoin_status = 'excedent_disponible'
    else:
        besoin_status = 'equilibre'
    
    return {
        'periode': {
            'debut': today,
            'fin': date_limite,
            'jours': jours
        },
        'soldes': {
            'solde_total_comptes': float(solde_total)
        },
        'decaissements': {
            'total': float(total_decaissements),
            'par_jour': [
                {
                    'date': v['date'],
                    'montant': float(v['montant']),
                    'demandes': v['demandes']
                }
                for v in sorted(decaissements_par_jour.values(), key=lambda x: x['date'])
            ]
        },
        'besoin': {
            'montant': float(abs(besoin_net)),
            'status': besoin_status
        }
    }


# Import nécessaire pour les fonctions
from django.db import models
