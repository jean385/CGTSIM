import React, { useState, useEffect } from 'react';
import { 
  CreditCard, TrendingUp, FileText, Users, Menu, X, LogOut, 
  Bell, Check, XCircle, CheckCircle, Clock, Loader, Gift, Plus, Save
} from 'lucide-react';
import apiService from './apiService';

export default function PortailAdmin({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [demandes, setDemandes] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatut, setFilterStatut] = useState('all');
  const [showSubventionForm, setShowSubventionForm] = useState(false);
  const [cssList, setCssList] = useState([]);
  
  const [subventionForm, setSubventionForm] = useState({
    css: '',
    montant: '',
    date_transaction: new Date().toISOString().split('T')[0],
    reference: '',
    description: ''
  });

  useEffect(() => {
    loadDemandes();
    loadTransactions();
    loadCssList();
  }, []);

  const loadDemandes = async () => {
    setLoading(true);
    try {
      const data = await apiService.getAllDemandes();
      setDemandes(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setDemandes([]);
    } finally {
      setLoading(false);
    }
  };

  const loadTransactions = async () => {
    try {
      const data = await apiService.getTransactions();
      setTransactions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadCssList = async () => {
    try {
      const data = await apiService.getAllDemandes();
      const demandesData = Array.isArray(data) ? data : [];
      const uniqueCss = [...new Map(demandesData.map(d => [d.css, { id: d.css, code: d.css_code, name: d.css_name }])).values()];
      setCssList(uniqueCss);
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprouver = async (demandeId) => {
    if (!window.confirm('Voulez-vous approuver cette demande ?')) return;
    try {
      await apiService.approveDemande(demandeId, 'approved', '');
      alert('Demande approuvée avec succès !');
      loadDemandes();
    } catch (err) {
      alert('Erreur : ' + err.message);
    }
  };

  const handleRejeter = async (demandeId) => {
    const motif = prompt('Motif du rejet (optionnel) :');
    if (motif === null) return;
    try {
      await apiService.approveDemande(demandeId, 'rejected', motif);
      alert('Demande rejetée');
      loadDemandes();
    } catch (err) {
      alert('Erreur : ' + err.message);
    }
  };

  const handleMarquerVerse = async (demandeId) => {
    if (!window.confirm('Marquer cette demande comme versée ?')) return;
    try {
      await apiService.marquerVerse(demandeId, new Date().toISOString().split('T')[0]);
      alert('Demande marquée comme versée !');
      loadDemandes();
    } catch (err) {
      alert('Erreur : ' + err.message);
    }
  };

  const handleSubmitSubvention = async (e) => {
    e.preventDefault();
    
    if (!subventionForm.css || !subventionForm.montant) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      const montant = parseFloat(subventionForm.montant);
      
      const result = await apiService.createTransaction({
        css: subventionForm.css,
        type_transaction: 'subvention',
        montant: -Math.abs(montant),
        date_transaction: subventionForm.date_transaction,
        reference: subventionForm.reference || '',
        description: subventionForm.description || ''
      });

      alert(`Subvention enregistrée avec succès !\nRéférence: ${result.reference}`);
      setSubventionForm({
        css: '',
        montant: '',
        date_transaction: new Date().toISOString().split('T')[0],
        reference: '',
        description: ''
      });
      setShowSubventionForm(false);
      loadTransactions();
    } catch (err) {
      alert('Erreur: ' + err.message);
    }
  };

  const formatMontant = (montant) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency', currency: 'CAD', minimumFractionDigits: 2
    }).format(montant);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-CA', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  };

  const getStatutBadge = (statut) => {
    const config = {
      pending: { icon: Clock, color: 'orange', label: 'En révision', bgClass: 'bg-orange-100', textClass: 'text-orange-700' },
      approved: { icon: CheckCircle, color: 'green', label: 'Approuvée', bgClass: 'bg-green-100', textClass: 'text-green-700' },
      versed: { icon: CheckCircle, color: 'blue', label: 'Versé', bgClass: 'bg-blue-100', textClass: 'text-blue-700' },
      rejected: { icon: XCircle, color: 'red', label: 'Rejetée', bgClass: 'bg-red-100', textClass: 'text-red-700' },
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
          <h1 className="text-2xl font-bold text-gray-900">Admin CGTSIM</h1>
          <p className="text-sm text-gray-500">Gestion des demandes de fonds</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-gray-100 rounded-lg relative">
          <Bell size={20} />
        </button>
        <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-gray-500">Administrateur CGTSIM</p>
          </div>
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold">
            {user?.first_name?.[0]}{user?.last_name?.[0]}
          </div>
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
            <p className="text-xs text-purple-200">Administration</p>
          </div>
        </div>
      </div>
      <nav className="p-4 space-y-2">
        {[
          { id: 'dashboard', icon: TrendingUp, label: 'Tableau de bord' },
          { id: 'demandes', icon: FileText, label: 'Demandes de fonds' },
          { id: 'subventions', icon: Gift, label: 'Subventions' },
          { id: 'css', icon: Users, label: 'Gestion CSS' }
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

    const demandesRecentes = demandes.filter(d => d.statut === 'pending').slice(0, 5);

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: 'Demandes totales', value: stats.total, icon: FileText, color: 'purple' },
            { label: 'En attente', value: stats.pending, icon: Clock, color: 'orange' },
            { label: 'Approuvées', value: stats.approved, icon: CheckCircle, color: 'green' },
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

        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Demandes en attente de révision</h2>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="animate-spin text-purple-600" size={32} />
              </div>
            ) : demandesRecentes.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Aucune demande en attente</p>
            ) : (
              <div className="space-y-4">
                {demandesRecentes.map(demande => (
                  <DemandeCard key={demande.id} demande={demande} onApprouver={handleApprouver} onRejeter={handleRejeter} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const DemandeCard = ({ demande, onApprouver, onRejeter, showActions = true }) => {
    const badge = getStatutBadge(demande.statut);
    const StatutIcon = badge.icon;

    return (
      <div className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-xl font-bold text-gray-900">{formatMontant(demande.montant_total)}</h3>
              <span className={`px-3 py-1.5 ${badge.bgClass} ${badge.textClass} text-sm font-medium rounded-full flex items-center gap-1.5`}>
                <StatutIcon size={16} />
                {badge.label}
              </span>
            </div>
            <p className="text-sm font-medium text-gray-700 mb-1">CSS : {demande.css_name || 'N/A'}</p>
            {demande.description && <p className="text-sm text-gray-600 mb-3">{demande.description}</p>}
            
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>{demande.nb_jours} jour(s)</span>
              <span>{demande.nb_items} ligne(s)</span>
              <span>Demandé le {formatDate(demande.date_demande)}</span>
            </div>
          </div>
          <span className="text-xs text-gray-400 ml-4">{demande.reference}</span>
        </div>

        {showActions && demande.statut === 'pending' && (
          <div className="flex gap-3 pt-4 border-t">
            <button
              onClick={() => onApprouver(demande.id)}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
            >
              <Check size={18} />
              Approuver
            </button>
            <button
              onClick={() => onRejeter(demande.id)}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center justify-center gap-2"
            >
              <XCircle size={18} />
              Rejeter
            </button>
          </div>
        )}

        {demande.statut === 'approved' && (
          <div className="pt-4 border-t">
            <button
              onClick={() => handleMarquerVerse(demande.id)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
            >
              <CheckCircle size={18} />
              Marquer comme versé
            </button>
          </div>
        )}
      </div>
    );
  };

  const ListeDemandes = () => {
    const demandesFiltrees = filterStatut === 'all' 
      ? demandes 
      : demandes.filter(d => d.statut === filterStatut);

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-4">
            <select
              value={filterStatut}
              onChange={(e) => setFilterStatut(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">Toutes les demandes</option>
              <option value="pending">En attente</option>
              <option value="approved">Approuvées</option>
              <option value="versed">Versées</option>
              <option value="rejected">Rejetées</option>
            </select>
            <span className="text-sm text-gray-600">
              {demandesFiltrees.length} demande(s)
            </span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader className="animate-spin text-purple-600" size={40} />
              </div>
            ) : demandesFiltrees.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Aucune demande trouvée</p>
            ) : (
              <div className="space-y-4">
                {demandesFiltrees.map(demande => (
                  <DemandeCard 
                    key={demande.id} 
                    demande={demande} 
                    onApprouver={handleApprouver} 
                    onRejeter={handleRejeter}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const Subventions = () => {
    const subventions = transactions.filter(t => t.type_transaction === 'subvention');

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Gestion des Subventions</h2>
          <button
            onClick={() => setShowSubventionForm(!showSubventionForm)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
          >
            <Plus size={20} />
            Nouvelle subvention
          </button>
        </div>

        {showSubventionForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Nouvelle Subvention</h3>
            <form onSubmit={handleSubmitSubvention} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    CSS <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={subventionForm.css}
                    onChange={(e) => setSubventionForm({...subventionForm, css: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Sélectionner un CSS</option>
                    {cssList.map(css => (
                      <option key={css.id} value={css.id}>{css.code} - {css.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    required
                    value={subventionForm.date_transaction}
                    onChange={(e) => setSubventionForm({...subventionForm, date_transaction: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Montant (positif) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={subventionForm.montant}
                    onChange={(e) => setSubventionForm({...subventionForm, montant: e.target.value})}
                    placeholder="500000.00"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Référence (optionnel)
                  </label>
                  <input
                    type="text"
                    value={subventionForm.reference}
                    onChange={(e) => setSubventionForm({...subventionForm, reference: e.target.value})}
                    placeholder="SUB-MIN-2025-Q4"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  rows="3"
                  value={subventionForm.description}
                  onChange={(e) => setSubventionForm({...subventionForm, description: e.target.value})}
                  placeholder="Subvention trimestrielle Q4 2025"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowSubventionForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center justify-center gap-2"
                >
                  <Save size={18} />
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Historique des subventions</h3>
            <p className="text-sm text-gray-500 mt-1">{subventions.length} subvention(s) enregistrée(s)</p>
          </div>
          <div className="p-6">
            {subventions.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Aucune subvention enregistrée</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CSS</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Référence</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Montant</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {subventions.map(sub => (
                      <tr key={sub.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{formatDate(sub.date_transaction)}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{sub.css_code} - {sub.css_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{sub.reference}</td>
                        <td className="px-4 py-3 text-sm font-semibold text-red-600 text-right">{formatMontant(sub.montant)}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{sub.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const GestionCSS = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Gestion des CSS</h2>
      <p className="text-gray-600">Fonctionnalité à venir...</p>
    </div>
  );

  if (loading && demandes.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin text-purple-600 mx-auto mb-4" size={48} />
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 p-6 overflow-auto">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'demandes' && <ListeDemandes />}
          {activeTab === 'subventions' && <Subventions />}
          {activeTab === 'css' && <GestionCSS />}
        </main>
      </div>
    </div>
  );
}
