const API_URL = 'http://localhost:8000/api';

// Fonction helper pour gérer le refresh token
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  const response = await fetch(`${API_URL}/auth/refresh/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!response.ok) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
    throw new Error('Session expirée');
  }

  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data.access;
}

// Fonction helper pour faire des requêtes avec gestion auto du token
async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem('access_token');

  const makeRequest = async (authToken) => {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.status === 401) {
      try {
        const newToken = await refreshAccessToken();
        return await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${newToken}`,
          },
        });
      } catch (error) {
        throw new Error('Session expirée');
      }
    }

    return response;
  };

  return makeRequest(token);
}

const apiService = {
  // Authentification
  async login(username, password) {
    const response = await fetch(`${API_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Identifiants invalides');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);

    const userResponse = await fetch(`${API_URL}/auth/me/`, {
      headers: {
        'Authorization': `Bearer ${data.access}`,
      },
    });

    if (userResponse.ok) {
      const userData = await userResponse.json();
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    }

    throw new Error('Erreur lors de la récupération des informations utilisateur');
  },

  // Demandes de fonds
  async createDemande(demandeData) {
    const response = await fetchWithAuth(`${API_URL}/demandes/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(demandeData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(JSON.stringify(error));
    }

    return await response.json();
  },

  async getMesDemandes() {
    const response = await fetchWithAuth(`${API_URL}/demandes/mes_demandes/`);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des demandes');
    }

    return await response.json();
  },

  async getAllDemandes() {
    const response = await fetchWithAuth(`${API_URL}/demandes/`);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des demandes');
    }

    return await response.json();
  },

  async getDemandeDetail(id) {
    const response = await fetchWithAuth(`${API_URL}/demandes/${id}/`);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération de la demande');
    }

    return await response.json();
  },

  async approveDemande(id, statut, notes_revision = '') {
    const response = await fetchWithAuth(`${API_URL}/demandes/${id}/approve/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ statut, notes_revision }),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de l\'approbation');
    }

    return await response.json();
  },

  async marquerVerse(id, date_versement) {
    const response = await fetchWithAuth(`${API_URL}/demandes/${id}/marquer_verse/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ date_versement }),
    });

    if (!response.ok) {
      throw new Error('Erreur lors du marquage');
    }

    return await response.json();
  },

  // Dashboard
  async getDashboardStats() {
    const response = await fetchWithAuth(`${API_URL}/dashboard/stats_css/`);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des stats');
    }

    return await response.json();
  },

  async getDashboardStatsAdmin() {
    const response = await fetchWithAuth(`${API_URL}/dashboard/stats_cgtsim/`);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des stats');
    }

    return await response.json();
  },

  // Transactions (Subventions)
  async createTransaction(transactionData) {
    const response = await fetchWithAuth(`${API_URL}/transactions/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(transactionData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erreur lors de la création de la transaction');
    }

    return await response.json();
  },

  async getTransactions() {
    const response = await fetchWithAuth(`${API_URL}/transactions/`);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des transactions');
    }

    return await response.json();
  },
};

export default apiService;
