import React, { useState, useEffect } from 'react';
import { 
  CreditCard, TrendingUp, FileText, Calendar, Clock, 
  Menu, X, LogOut, Plus, Trash2, Loader
} from 'lucide-react';
import apiService from './apiService';

export default function PortailCSS({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [demandes, setDemandes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // État pour le formulaire de nouvelle demande
  const [showNewDemandeForm, setShowNewDemandeForm] = useState(false);
  const [formData, setFormData] = useState({
    description: '',
    jours: []
  });

  useEffect(() => {
    loadDemandes();
  }, []);

  const loadDemandes = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getMesDemandes();
      setDemandes(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
      setDemandes([]);
    } finally {
      setLoading(false);
    }
  };

  const formatMontant = (montant) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency', currency: 'CAD', minimumFractionDigits: 2
    }).format(montant);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-CA', {
      year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
    });
  };

  const getStatutBadge = (statut) => {
    const config = {
      pending: { color: 'orange', label: 'En révision', bgClass: 'bg-orange-100', textClass: 'text-orange-700' },
      approved: { color: 'green', label: 'Approuvée', bgClass: 'bg-green-100', textClass: 'text-green-700' },
      versed: { color: 'blue', label: 'Versé', bgClass: 'bg-blue-100', textClass: 'text-blue-700' },
      rejected: { color: 'red', label: 'Rejetée', bgClass: 'bg-red-100', textClass: 'text-red-700' },
    };
    return config[statut] || config.pending;
  };

  const Header = () => (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden p-2 hover:bg-gray-100 rounded-lg">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portail CSS</h1>
          <p className="text-sm text-gray-500">{user?.css?.name}</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
          <p className="text-xs text-gray-500">{user?.css?.code}</p>
        </div>
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold">
          {user?.first_name?.[0]}{user?.last_name?.[0]}
        </div>
      </div>
    </header>
  );

  const Sidebar = () => (
    <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:relative inset-y-0 left-0 z-20 w-64 bg-gradient-to-b from-purple-600 to-purple-800 text-white transition-transform duration-300 ease-in-out flex flex-col`}>
      <div className="p-6 border-b border-purple-500">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
            <CreditCard className="text-purple-600" size={24} />
          </div>
          <div>
            <h2 className="font-bold text-lg">CGTSIM</h2>
            <p className="text-xs text-purple-200">Portail CSS</p>
          </div>
        </div>
      </div>
      <nav className="p-4 space-y-2">
        {[
          { id: 'dashboard', icon: TrendingUp, label: 'Tableau de bord' },
          { id: 'demandes', icon: FileText, label: 'Mes demandes' },
          { id: 'nouvelle', icon: Plus, label: 'Nouvelle demande' }
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === item.id ? 'bg-white text-purple-600 font-medium' : 'hover:bg-purple-700 text-white'
            }`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </button>
        ))}
        
        <div className="pt-2 mt-2 border-t border-purple-500">
          <button 
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-purple-700 text-white transition-colors"
          >
            <LogOut size={20} />
            <span>Déconnexion</span>
          </button>
        </div>
      </nav>
    </aside>
  );

  const Dashboard = () => {
    const stats = {
      total: demandes.length,
      pending: demandes.filter(d => d.statut === 'pending').length,
      approved: demandes.filter(d => d.statut === 'approved').length,
      versed: demandes.filter(d => d.statut === 'versed').length,
      montantTotal: demandes.reduce((acc, d) => acc + parseFloat(d.montant_total), 0),
    };

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: 'Demandes totales', value: stats.total, icon: FileText, color: 'purple' },
            { label: 'En révision', value: stats.pending, icon: Clock, color: 'orange' },
            { label: 'Approuvées', value: stats.approved, icon: Calendar, color: 'green' },
            { label: 'Montant total', value: formatMontant(stats.montantTotal), icon: TrendingUp, color: 'blue' }
          ].map((stat, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center`}>
                  <stat.icon className={`text-${stat.color}-600`} size={24} />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{stat.value}</h3>
              <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Demandes récentes</h2>
          {demandes.slice(0, 5).map(demande => (
            <DemandeCard key={demande.id} demande={demande} />
          ))}
        </div>
      </div>
    );
  };

  const DemandeCard = ({ demande }) => {
    const badge = getStatutBadge(demande.statut);

    return (
      <div className="border border-gray-200 rounded-lg p-4 mb-3 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-xl font-bold text-gray-900">{formatMontant(demande.montant_total)}</h3>
              <span className={`px-3 py-1 ${badge.bgClass} ${badge.textClass} text-sm font-medium rounded-full`}>
                {badge.label}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-2">{demande.description || 'Aucune description'}</p>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>{demande.nb_jours} jour(s)</span>
              <span>{demande.nb_items} ligne(s)</span>
              <span>Demandé le {formatDate(demande.date_demande)}</span>
            </div>
          </div>
          <span className="text-xs text-gray-400">{demande.reference}</span>
        </div>
      </div>
    );
  };

  const MesDemandes = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Toutes mes demandes</h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <Loader className="animate-spin text-purple-600" size={32} />
          </div>
        ) : demandes.length === 0 ? (
          <p className="text-center text-gray-500 py-8">Aucune demande</p>
        ) : (
          demandes.map(demande => <DemandeCard key={demande.id} demande={demande} />)
        )}
      </div>
    </div>
  );

  const NouvelleDemande = () => {
    const [jours, setJours] = useState([]);
    const [description, setDescription] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const ajouterJour = () => {
      if (jours.length >= 10) {
        alert('Maximum 10 dates par demande');
        return;
      }

      const today = new Date();
      let nextDay = new Date(today);
      nextDay.setDate(nextDay.getDate() + 1);
      
      while (nextDay.getDay() === 0 || nextDay.getDay() === 6) {
        nextDay.setDate(nextDay.getDate() + 1);
      }

      setJours([...jours, {
        id: Date.now(),
        date_besoin: nextDay.toISOString().split('T')[0],
        items: []
      }]);
    };

    const retirerJour = (jourId) => {
      setJours(jours.filter(j => j.id !== jourId));
    };

    const updateDateJour = (jourId, newDate) => {
      setJours(jours.map(jour => {
        if (jour.id === jourId) {
          return { ...jour, date_besoin: newDate };
        }
        return jour;
      }));
    };

    const ajouterLigne = (jourId) => {
      setJours(jours.map(jour => {
        if (jour.id === jourId) {
          if (jour.items.length >= 20) {
            alert('Maximum 20 lignes par jour');
            return jour;
          }
          return {
            ...jour,
            items: [...jour.items, {
              id: Date.now(),
              montant: '',
              categorie: 'fonctionnement',
              type_paiement: 'fournisseurs_dd',
              description: ''
            }]
          };
        }
        return jour;
      }));
    };

    const retirerLigne = (jourId, itemId) => {
      setJours(jours.map(jour => {
        if (jour.id === jourId) {
          return {
            ...jour,
            items: jour.items.filter(item => item.id !== itemId)
          };
        }
        return jour;
      }));
    };

    const updateLigne = (jourId, itemId, field, value) => {
      setJours(jours.map(jour => {
        if (jour.id === jourId) {
          return {
            ...jour,
            items: jour.items.map(item => {
              if (item.id === itemId) {
                return { ...item, [field]: value };
              }
              return item;
            })
          };
        }
        return jour;
      }));
    };

    const calculerTotalJour = (jour) => {
      return jour.items.reduce((sum, item) => sum + (parseFloat(item.montant) || 0), 0);
    };

    const calculerTotalGeneral = () => {
      return jours.reduce((sum, jour) => sum + calculerTotalJour(jour), 0);
    };

    const calculerTotalParCategorie = () => {
      const totaux = {
        fonctionnement: 0,
        investissement: 0,
        sqi: 0,
        ebi: 0
      };

      jours.forEach(jour => {
        jour.items.forEach(item => {
          totaux[item.categorie] += parseFloat(item.montant) || 0;
        });
      });

      return totaux;
    };

    const handleSubmit = async () => {
      if (jours.length === 0) {
        alert('Ajoutez au moins une date');
        return;
      }

      let hasItems = false;
      jours.forEach(jour => {
        if (jour.items.length > 0) hasItems = true;
      });

      if (!hasItems) {
        alert('Ajoutez au moins une ligne');
        return;
      }

      setSubmitting(true);

      try {
        const payload = {
          description: description,
          jours: jours.map(jour => ({
            date_besoin: jour.date_besoin,
            items: jour.items.map((item, index) => ({
              montant: parseFloat(item.montant) || 0,
              categorie: item.categorie,
              type_paiement: item.type_paiement,
              description: item.description,
              ordre: index
            }))
          }))
        };

        const result = await apiService.createDemande(payload);
        alert(`Demande créée avec succès !\nRéférence: ${result.reference}`);
        setJours([]);
        setDescription('');
        setActiveTab('demandes');
        loadDemandes();
      } catch (err) {
        alert('Erreur: ' + err.message);
      } finally {
        setSubmitting(false);
      }
    };

    const totauxCategories = calculerTotalParCategorie();

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Nouvelle demande de fonds</h2>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description générale (optionnel)
            </label>
            <textarea 
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              rows="2"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Demande de fonds pour..."
            />
          </div>

          <button 
            onClick={ajouterJour}
            className="mb-6 px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 flex items-center gap-2"
          >
            <Plus size={20} /> Ajouter une date
            <span className="text-xs bg-purple-500 px-2 py-1 rounded-full ml-2">max 10 dates</span>
          </button>

          {jours.map((jour, jourIndex) => (
            <JourCard 
              key={jour.id}
              jour={jour}
              jourIndex={jourIndex}
              retirerJour={retirerJour}
              updateDateJour={updateDateJour}
              ajouterLigne={ajouterLigne}
              retirerLigne={retirerLigne}
              updateLigne={updateLigne}
              calculerTotalJour={calculerTotalJour}
            />
          ))}

          {jours.length > 0 && (
            <>
              <div className="bg-gradient-to-br from-purple-600 to-pink-600 text-white rounded-xl p-6 mb-6">
                <h3 className="text-xl font-bold mb-4">📊 Récapitulatif par catégorie</h3>
                <div className="grid grid-cols-4 gap-4 mb-4">
                  {[
                    { cat: 'fonctionnement', label: 'Fonctionnement' },
                    { cat: 'investissement', label: 'Investissement' },
                    { cat: 'sqi', label: 'SQI' },
                    { cat: 'ebi', label: 'EBI' }
                  ].map(({cat, label}) => (
                    <div key={cat} className="bg-white/10 rounded-lg p-3">
                      <div className="text-sm opacity-90">{label}</div>
                      <div className="text-2xl font-bold">{formatMontant(totauxCategories[cat])}</div>
                    </div>
                  ))}
                </div>
                <div className="border-t-2 border-white/30 pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-medium">TOTAL GÉNÉRAL</span>
                    <span className="text-4xl font-bold">{formatMontant(calculerTotalGeneral())}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 justify-end">
                <button 
                  onClick={() => { setJours([]); setDescription(''); }}
                  className="px-8 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button 
                  onClick={handleSubmit}
                  disabled={submitting}
                  className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 shadow-lg disabled:opacity-50 flex items-center gap-2"
                >
                  {submitting && <Loader className="animate-spin" size={18} />}
                  {submitting ? 'Envoi...' : 'Soumettre la demande'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  };

  const JourCard = ({ jour, jourIndex, retirerJour, updateDateJour, ajouterLigne, retirerLigne, updateLigne, calculerTotalJour }) => {
    const today = new Date();
    const minDate = new Date(today.getTime() + 86400000).toISOString().split('T')[0];
    const maxDate = new Date(today.getTime() + 30*86400000).toISOString().split('T')[0];

    return (
      <div className="mb-6 border-2 border-purple-200 rounded-xl overflow-hidden">
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 flex items-center justify-between border-b-2 border-purple-200">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📅</span>
            <input 
              type="date"
              value={jour.date_besoin}
              onChange={(e) => updateDateJour(jour.id, e.target.value)}
              min={minDate}
              max={maxDate}
              className="text-lg font-bold text-gray-900 uppercase bg-white border-2 border-purple-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
          <button 
            onClick={() => retirerJour(jour.id)}
            className="px-3 py-1 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600"
          >
            ❌ Retirer
          </button>
        </div>
        
        <div className="p-6">
          {jour.items.length > 0 && (
            <>
              {/* HEADERS DES COLONNES */}
              <div className="grid grid-cols-12 gap-2 items-center mb-3 pb-2 border-b-2 border-gray-200">
                <div className="col-span-1"></div>
                <div className="col-span-2 text-xs font-bold text-gray-600 uppercase">Montant</div>
                <div className="col-span-3 text-xs font-bold text-gray-600 uppercase">Catégorie</div>
                <div className="col-span-3 text-xs font-bold text-gray-600 uppercase">Type de paiement</div>
                <div className="col-span-2 text-xs font-bold text-gray-600 uppercase">Description</div>
                <div className="col-span-1"></div>
              </div>

              <div className="space-y-2">
                {jour.items.map((item, itemIndex) => (
                  <LigneItem 
                    key={item.id}
                    item={item}
                    itemIndex={itemIndex}
                    jourId={jour.id}
                    retirerLigne={retirerLigne}
                    updateLigne={updateLigne}
                  />
                ))}
              </div>
            </>
          )}

          <button 
            onClick={() => ajouterLigne(jour.id)}
            className="w-full mt-4 px-4 py-2 border-2 border-dashed border-purple-300 text-purple-600 rounded-lg font-medium hover:bg-purple-50 flex items-center justify-center gap-2 text-sm"
          >
            <Plus size={18} /> Ajouter une ligne
            <span className="text-xs bg-purple-100 px-2 py-1 rounded-full ml-2">max 20 lignes</span>
          </button>

          <div className="bg-purple-50 border-t-2 border-purple-200 -mx-6 -mb-6 mt-4 p-4">
            <div className="text-right">
              <span className="text-sm text-gray-600">Sous-total du jour :</span>
              <span className="text-2xl font-bold text-purple-600 ml-2">{formatMontant(calculerTotalJour(jour))}</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const LigneItem = ({ item, itemIndex, jourId, retirerLigne, updateLigne }) => {
    const montant = parseFloat(item.montant) || 0;
    const isNegatif = montant < 0;

    return (
      <div className={`p-3 rounded-lg border transition-colors ${
        isNegatif 
          ? 'bg-red-50 border-red-200 hover:bg-red-100' 
          : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
      }`}>
        <div className="grid grid-cols-12 gap-2 items-center">
          <div className="col-span-1">
            <span className={`font-semibold text-sm ${isNegatif ? 'text-red-600' : 'text-purple-600'}`}>
              {isNegatif ? '🔻' : '💰'} #{itemIndex + 1}
            </span>
          </div>
          
          <div className="col-span-2 flex items-center gap-1">
            <input 
              type="number" 
              step="0.01"
              value={item.montant}
              onChange={(e) => updateLigne(jourId, item.id, 'montant', e.target.value)}
              className={`w-full px-2 py-1.5 text-sm border rounded focus:ring-2 ${
                isNegatif 
                  ? 'border-red-300 focus:ring-red-500 text-red-700 font-semibold' 
                  : 'border-gray-300 focus:ring-purple-500'
              }`}
              placeholder="0 ou -1000"
            />
            <span className="text-xs text-gray-500">$</span>
          </div>
          
          <div className="col-span-3">
            <select 
              value={item.categorie}
              onChange={(e) => updateLigne(jourId, item.id, 'categorie', e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500"
            >
              <option value="fonctionnement">Fonctionnement</option>
              <option value="investissement">Investissement</option>
              <option value="sqi">SQI</option>
              <option value="ebi">EBI</option>
            </select>
          </div>
          
          <div className="col-span-3">
            <select 
              value={item.type_paiement}
              onChange={(e) => updateLigne(jourId, item.id, 'type_paiement', e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500"
            >
              <option value="fournisseurs_dd">Fournisseurs DD</option>
              <option value="fournisseurs_cheque">Fournisseurs Chèque</option>
              <option value="salaires_dd">Salaires DD</option>
              <option value="salaires_cheque">Salaires Chèque</option>
            </select>
          </div>
          
          <div className="col-span-2">
            <input 
              type="text" 
              value={item.description}
              onChange={(e) => updateLigne(jourId, item.id, 'description', e.target.value)}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500"
              placeholder={isNegatif ? "Ajustement/correction" : "Optionnel"}
            />
          </div>

          <div className="col-span-1 text-right">
            <button 
              onClick={() => retirerLigne(jourId, item.id)}
              className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>
        
        {isNegatif && (
          <div className="mt-2 text-xs text-red-600 font-medium pl-1">
            ⚠️ Montant négatif - Ajustement/correction
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 p-6 overflow-auto">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'demandes' && <MesDemandes />}
          {activeTab === 'nouvelle' && <NouvelleDemande />}
        </main>
      </div>
    </div>
  );
}
