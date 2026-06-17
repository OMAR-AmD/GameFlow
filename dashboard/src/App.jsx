import { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import './index.css';

const API_BASE = 'http://localhost:8000/api';

const CHART_COLORS = ['#6366f1', '#ec4899', '#8b5cf6', '#06b6d4', '#f59e0b'];

function App() {
  const [activeTab, setActiveTab] = useState('cold');
  const [gamesList, setGamesList] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [selectedGames, setSelectedGames] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedCard, setExpandedCard] = useState(null);
  const [personaLabel, setPersonaLabel] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  
  const [searchGame, setSearchGame] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const gamesRes = await axios.get(`${API_BASE}/games`);
        setGamesList(gamesRes.data.games);
        
        const usersRes = await axios.get(`${API_BASE}/users`);
        setUsersList(usersRes.data.users);
        if (usersRes.data.users.length > 0) {
          setSelectedUser(usersRes.data.users[0]);
        }
      } catch (err) {
        console.error(err);
        setError("Erreur de connexion à l'API Backend.");
      }
    };
    fetchData();
  }, []);

  const fetchAnalytics = async () => {
    if (analytics) return; // already loaded
    try {
      const res = await axios.get(`${API_BASE}/analytics`);
      setAnalytics(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleColdStart = async () => {
    if (selectedGames.length === 0) return;
    setLoading(true);
    setError(null);
    setExpandedCard(null);
    setPersonaLabel(null);
    try {
      const res = await axios.post(`${API_BASE}/recommend/cold-start`, { games: selectedGames });
      setRecommendations(res.data.recommendations);
      if (res.data.persona) setPersonaLabel(res.data.persona);
    } catch (err) {
      setError("Erreur lors de la recommandation Cold Start.");
    } finally {
      setLoading(false);
    }
  };

  const handleWarmStart = async () => {
    if (!selectedUser) return;
    setLoading(true);
    setError(null);
    setExpandedCard(null);
    setPersonaLabel(null);
    try {
      const res = await axios.post(`${API_BASE}/recommend/hybrid`, { user_id: selectedUser });
      setRecommendations(res.data.recommendations);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Erreur lors de la recommandation Hybride.");
      }
    } finally {
      setLoading(false);
    }
  };

  const addGame = (game) => {
    if (selectedGames.length < 5 && !selectedGames.includes(game)) {
      setSelectedGames([...selectedGames, game]);
      setSearchGame('');
    }
  };

  const removeGame = (game) => {
    setSelectedGames(selectedGames.filter(g => g !== game));
  };

  const filteredGames = gamesList.filter(g => 
    g.toLowerCase().includes(searchGame.toLowerCase()) && !selectedGames.includes(g)
  ).slice(0, 10);

  const toggleCard = (i) => {
    setExpandedCard(expandedCard === i ? null : i);
  };

  const switchTab = (tab) => {
    setActiveTab(tab);
    setRecommendations([]);
    setExpandedCard(null);
    setPersonaLabel(null);
    if (tab === 'admin') fetchAnalytics();
  };

  return (
    <div className="app-container">
      <div className="bg-glow"></div>
      
      <header className="header">
        <h1>🎮 GameFlow AI</h1>
        <p>Moteur de Recommandation Hybride & Personas</p>
      </header>

      <main className="main-content">
        <div className="tabs">
          <button className={`tab-btn ${activeTab === 'cold' ? 'active' : ''}`} onClick={() => switchTab('cold')}>
            🆕 Nouveau Joueur
          </button>
          <button className={`tab-btn ${activeTab === 'warm' ? 'active' : ''}`} onClick={() => switchTab('warm')}>
            🧠 Joueur Actif
          </button>
          <button className={`tab-btn ${activeTab === 'admin' ? 'active' : ''}`} onClick={() => switchTab('admin')}>
            📈 Analytics
          </button>
        </div>

        <div className="glass-panel">
          {error && <div className="error-banner">{error}</div>}
          
          {activeTab === 'cold' && (
            <div className="tab-content">
              <h2>Simulation d'un Nouveau Profil</h2>
              <p className="subtitle">Sélectionnez jusqu'à 5 jeux. L'IA va deviner votre Persona (K-Means).</p>
              
              <div className="input-group">
                <input 
                  type="text" 
                  className="game-search"
                  placeholder="Rechercher un jeu (ex: Skyrim)..." 
                  value={searchGame}
                  onChange={(e) => setSearchGame(e.target.value)}
                />
                {searchGame && (
                  <ul className="autocomplete">
                    {filteredGames.map(g => (
                      <li key={g} onClick={() => addGame(g)}>{g}</li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="selected-pills">
                {selectedGames.map(g => (
                  <span key={g} className="pill">
                    {g} <button onClick={() => removeGame(g)}>×</button>
                  </span>
                ))}
              </div>

              <button 
                className="action-btn" 
                onClick={handleColdStart}
                disabled={selectedGames.length === 0 || loading}
              >
                {loading ? 'Analyse en cours...' : 'Générer les recommandations'}
              </button>
            </div>
          )}

          {activeTab === 'warm' && (
            <div className="tab-content">
              <h2>Filtrage Collaboratif Hybride</h2>
              <p className="subtitle">Entrez un ID de joueur actif. L'IA utilisera la matrice SVD.</p>
              
              <input 
                type="text"
                className="user-select"
                placeholder="Entrez un Steam ID..."
                list="user-suggestions"
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
              />
              <datalist id="user-suggestions">
                {usersList.map(u => (
                  <option key={u} value={u} />
                ))}
              </datalist>

              <button 
                className="action-btn" 
                onClick={handleWarmStart}
                disabled={!selectedUser || loading}
              >
                {loading ? 'Calcul Matriciel...' : 'Générer les recommandations'}
              </button>
            </div>
          )}

          {activeTab === 'admin' && (
            <div className="tab-content">
              <h2>📊 Dashboard Analytique</h2>
              <p className="subtitle">Vue d'ensemble du moteur de recommandation GameFlow AI.</p>

              {analytics ? (
                <div className="analytics-content">
                  {/* Summary Stats */}
                  <div className="stats-row">
                    <div className="stat-card">
                      <div className="stat-number">{analytics.stats.total_users.toLocaleString()}</div>
                      <div className="stat-label">Joueurs</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{analytics.stats.total_games.toLocaleString()}</div>
                      <div className="stat-label">Jeux</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{analytics.stats.total_interactions.toLocaleString()}</div>
                      <div className="stat-label">Interactions</div>
                    </div>
                  </div>

                  {/* Charts Row */}
                  <div className="charts-row">
                    <div className="chart-card">
                      <h3>Répartition des Personas</h3>
                      <ResponsiveContainer width="100%" height={320}>
                        <PieChart>
                          <Pie
                            data={analytics.persona_distribution}
                            dataKey="count"
                            nameKey="name"
                            cx="50%"
                            cy="45%"
                            outerRadius={90}
                            label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                          >
                            {analytics.persona_distribution.map((_, idx) => (
                              <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }} 
                            formatter={(value) => [value + ' joueurs', 'Total']}
                          />
                          <Legend 
                            verticalAlign="bottom" 
                            iconType="circle"
                            wrapperStyle={{ fontSize: '12px', color: '#94a3b8', paddingTop: '10px' }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="chart-card">
                      <h3>Temps de Jeu Moyen par Persona</h3>
                      <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={analytics.playtime_by_persona} layout="vertical">
                          <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                          <YAxis dataKey="name" type="category" width={130} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                          <Tooltip 
                            contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                            formatter={(value) => [value + 'h', 'Moyenne']}
                          />
                          <Bar dataKey="hours" radius={[0, 6, 6, 0]}>
                            {analytics.playtime_by_persona.map((_, idx) => (
                              <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Genre Chart */}
                  <div className="chart-card chart-full">
                    <h3>🏆 Top 10 Genres les Plus Populaires</h3>
                    <ResponsiveContainer width="100%" height={320}>
                      <BarChart data={analytics.top_genres}>
                        <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} angle={-25} textAnchor="end" height={70} />
                        <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <Tooltip 
                          contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                          formatter={(value) => [value.toLocaleString() + ' heures', 'Temps total']}
                        />
                        <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                          {analytics.top_genres.map((_, idx) => (
                            <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ) : (
                <p style={{ textAlign: 'center', color: '#94a3b8' }}>Chargement des données analytiques...</p>
              )}
            </div>
          )}
        </div>

        {recommendations.length > 0 && (
          <div className="results-container">
            <h3>Vos Recommandations</h3>
            {personaLabel && (
              <div className="persona-badge">
                🎭 Persona détectée : <strong>{personaLabel}</strong>
              </div>
            )}
            <p className="click-hint">Cliquez sur un jeu pour voir l'explication de l'IA</p>
            <div className="cards-grid">
              {recommendations.map((game, i) => (
                <div 
                  key={i} 
                  className={`game-card ${expandedCard === i ? 'expanded' : ''}`} 
                  style={{ animationDelay: `${i * 0.05}s` }}
                  onClick={() => toggleCard(i)}
                >
                  <div className="card-header">
                    <div className="card-rank">#{i + 1}</div>
                    <div className="card-content">
                      {game.image && (
                        <img 
                          src={game.image} 
                          alt={game.name} 
                          className="game-image" 
                          onError={(e) => e.target.style.display = 'none'}
                        />
                      )}
                      <div className="card-title">{game.name}</div>
                    </div>
                  </div>
                  {expandedCard === i && (
                    <div className="card-details">
                      <div className="detail-row">
                        <span className="detail-label">🏷️ Genres</span>
                        <span className="detail-value">{game.genres ? game.genres.replace(/;/g, ' · ') : 'N/A'}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">🛠️ Développeur</span>
                        <span className="detail-value">{game.developer || 'N/A'}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">📦 Éditeur</span>
                        <span className="detail-value">{game.publisher || 'N/A'}</span>
                      </div>
                      <div className="ai-reason">
                        <div className="reason-title">💡 Pourquoi l'IA a choisi ce jeu :</div>
                        <p>{game.reason}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
