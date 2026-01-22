import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Activity,
    Server,
    Database,
    Cpu,
    HardDrive,
    Wifi,
    WifiOff,
    RefreshCw,
    Terminal,
    Clock,
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    Zap,
    Globe,
    BarChart3
} from 'lucide-react';

// API Service
const FINANCEX_URL = 'http://127.0.0.1:8000';

function ExecutionMonitor() {
    const [serverStatus, setServerStatus] = useState('checking');
    const [systemMetrics, setSystemMetrics] = useState(null);
    const [marketOverview, setMarketOverview] = useState(null);
    const [engines, setEngines] = useState(null);
    const [events, setEvents] = useState(null);
    const [indiaMarket, setIndiaMarket] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const [activeTab, setActiveTab] = useState('overview');

    const checkServer = async () => {
        try {
            // Fetch enhanced Jarvis status
            const response = await fetch(`${FINANCEX_URL}/api/jarvis/status`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            if (response.ok) {
                const data = await response.json();
                setServerStatus('online');
                setSystemMetrics(data);

                // Fetch additional data in parallel
                fetchAdditionalData();
            } else {
                // Fallback to basic status
                const fallbackResponse = await fetch(`${FINANCEX_URL}/status`, {
                    signal: AbortSignal.timeout(3000)
                });
                if (fallbackResponse.ok) {
                    const data = await fallbackResponse.json();
                    setServerStatus('online');
                    setSystemMetrics(data);
                } else {
                    setServerStatus('offline');
                }
            }
        } catch {
            setServerStatus('offline');
        }
        setLastUpdate(new Date());
    };

    const fetchAdditionalData = async () => {
        // Fetch market overview
        try {
            const marketRes = await fetch(`${FINANCEX_URL}/api/jarvis/market-overview`);
            if (marketRes.ok) setMarketOverview(await marketRes.json());
        } catch { }

        // Fetch engines status
        try {
            const enginesRes = await fetch(`${FINANCEX_URL}/api/jarvis/engines`);
            if (enginesRes.ok) setEngines(await enginesRes.json());
        } catch { }

        // Fetch events
        try {
            const eventsRes = await fetch(`${FINANCEX_URL}/api/jarvis/events`);
            if (eventsRes.ok) setEvents(await eventsRes.json());
        } catch { }
    };

    const fetchIndiaMarket = async () => {
        try {
            const response = await fetch(`${FINANCEX_URL}/api/jarvis/india`, {
                signal: AbortSignal.timeout(15000)
            });
            if (response.ok) {
                setIndiaMarket(await response.json());
            }
        } catch (e) {
            console.log('India market fetch failed:', e);
        }
    };

    useEffect(() => {
        checkServer();
        const interval = setInterval(checkServer, 10000);
        return () => clearInterval(interval);
    }, []);

    const getStateColor = (state) => {
        switch (state) {
            case 'STABLE': return 'var(--accent-green)';
            case 'HIGH_VOLATILITY': return 'var(--accent-orange)';
            case 'CRASH': return 'var(--accent-red)';
            default: return 'var(--text-muted)';
        }
    };

    const getStateBadgeClass = (state) => {
        switch (state) {
            case 'STABLE': return 'stable';
            case 'HIGH_VOLATILITY': return 'high-vol';
            case 'CRASH': return 'crash';
            default: return '';
        }
    };

    const getHealthColor = (health) => {
        switch (health) {
            case 'HEALTHY': return 'var(--accent-green)';
            case 'STRESSED': return 'var(--accent-orange)';
            case 'CRITICAL': return 'var(--accent-red)';
            default: return 'var(--text-muted)';
        }
    };

    return (
        <div>
            {/* Server Connection Status */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px 20px',
                background: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                marginBottom: '24px',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {serverStatus === 'online' ? (
                        <Wifi size={20} style={{ color: 'var(--accent-green)' }} />
                    ) : serverStatus === 'offline' ? (
                        <WifiOff size={20} style={{ color: 'var(--accent-red)' }} />
                    ) : (
                        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                            <RefreshCw size={20} style={{ color: 'var(--accent-blue)' }} />
                        </motion.div>
                    )}
                    <div>
                        <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                            Finance-X Server
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                            {FINANCEX_URL}
                        </div>
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    {systemMetrics?.marketHealth && (
                        <div style={{
                            padding: '4px 12px',
                            borderRadius: '20px',
                            background: `${getHealthColor(systemMetrics.marketHealth)}20`,
                            color: getHealthColor(systemMetrics.marketHealth),
                            fontSize: '11px',
                            fontWeight: '600',
                        }}>
                            {systemMetrics.marketHealth}
                        </div>
                    )}
                    <div style={{ textAlign: 'right' }}>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '4px 12px',
                            borderRadius: '20px',
                            background: serverStatus === 'online' ? 'rgba(34,197,94,0.2)' :
                                serverStatus === 'offline' ? 'rgba(239,68,68,0.2)' :
                                    'rgba(59,130,246,0.2)',
                            color: serverStatus === 'online' ? 'var(--accent-green)' :
                                serverStatus === 'offline' ? 'var(--accent-red)' :
                                    'var(--accent-blue)',
                            fontSize: '12px',
                            fontWeight: '500',
                        }}>
                            <div style={{
                                width: '6px',
                                height: '6px',
                                borderRadius: '50%',
                                background: 'currentColor',
                            }} />
                            {serverStatus === 'online' ? 'Connected' :
                                serverStatus === 'offline' ? 'Offline' : 'Checking...'}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                            Last checked: {lastUpdate.toLocaleTimeString()}
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={() => {
                            setServerStatus('checking');
                            checkServer();
                        }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '8px 16px',
                            background: 'var(--bg-tertiary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '8px',
                            color: 'var(--text-secondary)',
                            fontSize: '13px',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'var(--accent-blue)';
                            e.currentTarget.style.color = 'white';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'var(--bg-tertiary)';
                            e.currentTarget.style.color = 'var(--text-secondary)';
                        }}
                    >
                        <RefreshCw size={14} style={{
                            animation: serverStatus === 'checking' ? 'spin 1s linear infinite' : 'none'
                        }} />
                        {serverStatus === 'checking' ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
            </div>

            {/* Tab Navigation */}
            <div style={{
                display: 'flex',
                gap: '8px',
                marginBottom: '20px',
                padding: '4px',
                background: 'var(--bg-secondary)',
                borderRadius: '10px',
                border: '1px solid var(--border-color)',
            }}>
                {[
                    { id: 'overview', label: 'Overview', icon: Activity },
                    { id: 'engines', label: 'Engines', icon: Cpu },
                    { id: 'india', label: 'India Market', icon: Globe },
                    { id: 'api', label: 'API Endpoints', icon: Server },
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => {
                            setActiveTab(tab.id);
                            if (tab.id === 'india' && !indiaMarket) fetchIndiaMarket();
                        }}
                        style={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            padding: '10px 16px',
                            background: activeTab === tab.id ? 'var(--accent-blue)' : 'transparent',
                            border: 'none',
                            borderRadius: '8px',
                            color: activeTab === tab.id ? 'white' : 'var(--text-secondary)',
                            fontSize: '13px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                        }}
                    >
                        <tab.icon size={16} />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Overview Tab */}
            {
                activeTab === 'overview' && (
                    <>
                        {/* Status Cards */}
                        <div className="monitor-grid">
                            {/* System State */}
                            <div className="monitor-card">
                                <div className="monitor-card-header">
                                    <div className="monitor-card-icon blue">
                                        <Activity size={20} />
                                    </div>
                                    <div>
                                        <div className="monitor-card-title">System State</div>
                                        <div className="monitor-card-subtitle">Current market condition</div>
                                    </div>
                                </div>
                                {serverStatus === 'online' && systemMetrics ? (
                                    <>
                                        <div className={`status-badge ${getStateBadgeClass(systemMetrics.state)}`}>
                                            <div style={{
                                                width: '8px',
                                                height: '8px',
                                                borderRadius: '50%',
                                                background: 'currentColor',
                                            }} />
                                            {systemMetrics.state}
                                        </div>
                                        <div style={{ marginTop: '12px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                                            Risk Score: <strong>{systemMetrics.risk?.toFixed(2) || 'N/A'}</strong>
                                        </div>
                                    </>
                                ) : (
                                    <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                                        {serverStatus === 'offline' ? 'Server offline' : 'Loading...'}
                                    </div>
                                )}
                            </div>

                            {/* Market Overview */}
                            <div className="monitor-card">
                                <div className="monitor-card-header">
                                    <div className="monitor-card-icon green">
                                        <BarChart3 size={20} />
                                    </div>
                                    <div>
                                        <div className="monitor-card-title">Market Overview</div>
                                        <div className="monitor-card-subtitle">Gainers vs Losers</div>
                                    </div>
                                </div>
                                {serverStatus === 'online' && systemMetrics ? (
                                    <div style={{ display: 'flex', gap: '20px', marginTop: '8px' }}>
                                        <div style={{ textAlign: 'center' }}>
                                            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-green)' }}>
                                                <TrendingUp size={16} style={{ marginRight: '4px' }} />
                                                {systemMetrics.gainers || 0}
                                            </div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Gainers</div>
                                        </div>
                                        <div style={{ textAlign: 'center' }}>
                                            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-red)' }}>
                                                <TrendingDown size={16} style={{ marginRight: '4px' }} />
                                                {systemMetrics.losers || 0}
                                            </div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Losers</div>
                                        </div>
                                    </div>
                                ) : (
                                    <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                                        {serverStatus === 'offline' ? 'Server offline' : 'Loading...'}
                                    </div>
                                )}
                            </div>

                            {/* Active Events */}
                            <div className="monitor-card">
                                <div className="monitor-card-header">
                                    <div className="monitor-card-icon orange">
                                        <AlertTriangle size={20} />
                                    </div>
                                    <div>
                                        <div className="monitor-card-title">Active Events</div>
                                        <div className="monitor-card-subtitle">Market drivers</div>
                                    </div>
                                </div>
                                {serverStatus === 'online' && systemMetrics ? (
                                    <>
                                        <div style={{ fontSize: '28px', fontWeight: '700' }}>
                                            {systemMetrics.activeEvents || 0}
                                        </div>
                                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                            Events being tracked
                                        </div>
                                    </>
                                ) : (
                                    <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                                        {serverStatus === 'offline' ? 'Server offline' : 'Loading...'}
                                    </div>
                                )}
                            </div>

                            {/* Market Regime */}
                            <div className="monitor-card">
                                <div className="monitor-card-header">
                                    <div className="monitor-card-icon purple">
                                        <TrendingUp size={20} />
                                    </div>
                                    <div>
                                        <div className="monitor-card-title">Market Regime</div>
                                        <div className="monitor-card-subtitle">Volatility classification</div>
                                    </div>
                                </div>
                                {serverStatus === 'online' && systemMetrics ? (
                                    <>
                                        <div style={{
                                            fontSize: '20px',
                                            fontWeight: '600',
                                            color: systemMetrics.regime?.includes('HIGH') ? 'var(--accent-orange)' : 'var(--accent-green)'
                                        }}>
                                            {systemMetrics.regime || 'NORMAL'}
                                        </div>
                                        <div className="monitor-label" style={{ marginTop: '8px' }}>Current volatility level</div>
                                    </>
                                ) : (
                                    <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                                        {serverStatus === 'offline' ? 'Server offline' : 'Loading...'}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Top Movers */}
                        {marketOverview?.topMovers && (
                            <div style={{ marginTop: '24px' }}>
                                <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Top Movers</h3>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                                    gap: '12px',
                                }}>
                                    {marketOverview.topMovers.map((ticker, idx) => (
                                        <div key={idx} style={{
                                            padding: '16px',
                                            background: 'var(--bg-secondary)',
                                            borderRadius: '10px',
                                            border: '1px solid var(--border-color)',
                                        }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <span style={{ fontWeight: '600' }}>{ticker.symbol}</span>
                                                <span style={{
                                                    color: ticker.change > 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                                                    fontSize: '13px',
                                                    fontWeight: '500',
                                                }}>
                                                    {ticker.change > 0 ? '+' : ''}{ticker.change?.toFixed(2)}%
                                                </span>
                                            </div>
                                            <div style={{ fontSize: '18px', fontWeight: '700', marginTop: '8px' }}>
                                                ${ticker.price?.toFixed(2)}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </>
                )
            }

            {/* Engines Tab */}
            {
                activeTab === 'engines' && (
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                        gap: '16px',
                    }}>
                        {engines?.engines?.map((eng, idx) => (
                            <div key={idx} style={{
                                padding: '20px',
                                background: 'var(--bg-secondary)',
                                borderRadius: '12px',
                                border: '1px solid var(--border-color)',
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                                    <div style={{
                                        width: '40px',
                                        height: '40px',
                                        borderRadius: '10px',
                                        background: eng.status === 'ACTIVE' ? 'rgba(34,197,94,0.2)' : 'rgba(156,163,175,0.2)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}>
                                        <Zap size={20} style={{ color: eng.status === 'ACTIVE' ? 'var(--accent-green)' : 'var(--text-muted)' }} />
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: '600' }}>{eng.name}</div>
                                        <div style={{
                                            fontSize: '11px',
                                            color: eng.status === 'ACTIVE' ? 'var(--accent-green)' : 'var(--text-muted)',
                                        }}>
                                            {eng.status}
                                        </div>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                    {eng.eventCount !== undefined && (
                                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                                            Events: <strong>{eng.eventCount}</strong>
                                        </div>
                                    )}
                                    {eng.tickerCount !== undefined && (
                                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                                            Tickers: <strong>{eng.tickerCount}</strong>
                                        </div>
                                    )}
                                    {eng.indicators && (
                                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                                            Indicators: <strong>{eng.indicators.length}</strong>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )) || (
                                <div style={{ color: 'var(--text-muted)', padding: '40px', textAlign: 'center' }}>
                                    {serverStatus === 'offline' ? 'Server offline' : 'Loading engines...'}
                                </div>
                            )}
                    </div>
                )
            }

            {/* India Market Tab */}
            {
                activeTab === 'india' && (
                    <div>
                        {indiaMarket ? (
                            <>
                                <div style={{
                                    padding: '16px 20px',
                                    background: 'linear-gradient(135deg, rgba(255,153,51,0.1), rgba(19,136,8,0.1))',
                                    borderRadius: '12px',
                                    border: '1px solid rgba(255,153,51,0.3)',
                                    marginBottom: '20px',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}>
                                    <div>
                                        <div style={{ fontWeight: '600', fontSize: '18px' }}>NSE - NIFTY 50</div>
                                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                            {indiaMarket.tickerCount} stocks tracked
                                        </div>
                                    </div>
                                    <button
                                        onClick={fetchIndiaMarket}
                                        style={{
                                            padding: '8px 16px',
                                            background: 'var(--bg-tertiary)',
                                            border: '1px solid var(--border-color)',
                                            borderRadius: '8px',
                                            cursor: 'pointer',
                                            color: 'var(--text-secondary)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '6px',
                                        }}
                                    >
                                        <RefreshCw size={14} />
                                        Refresh India Data
                                    </button>
                                </div>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                                    gap: '12px',
                                }}>
                                    {indiaMarket.tickers?.slice(0, 12).map((stock, idx) => (
                                        <div key={idx} style={{
                                            padding: '16px',
                                            background: 'var(--bg-secondary)',
                                            borderRadius: '10px',
                                            border: '1px solid var(--border-color)',
                                        }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <span style={{ fontWeight: '600' }}>{stock.symbol}</span>
                                                <span style={{
                                                    padding: '2px 8px',
                                                    borderRadius: '4px',
                                                    background: stock.trend === 'BULLISH' ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)',
                                                    color: stock.trend === 'BULLISH' ? 'var(--accent-green)' : 'var(--accent-red)',
                                                    fontSize: '10px',
                                                    fontWeight: '600',
                                                }}>
                                                    {stock.trend}
                                                </span>
                                            </div>
                                            <div style={{ fontSize: '20px', fontWeight: '700', marginTop: '8px' }}>
                                                ₹{stock.price?.toFixed(2)}
                                            </div>
                                            <div style={{
                                                fontSize: '13px',
                                                color: stock.change_pct > 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                                            }}>
                                                {stock.change_pct > 0 ? '+' : ''}{stock.change_pct?.toFixed(2)}%
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div style={{
                                padding: '60px',
                                textAlign: 'center',
                                color: 'var(--text-muted)',
                            }}>
                                <Globe size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                                <div>Loading India market data...</div>
                                <div style={{ fontSize: '12px', marginTop: '8px' }}>This may take a few seconds</div>
                            </div>
                        )}
                    </div>
                )
            }

            {/* API Endpoints Tab */}
            {
                activeTab === 'api' && (
                    <div style={{
                        background: 'var(--bg-secondary)',
                        borderRadius: '12px',
                        border: '1px solid var(--border-color)',
                        overflow: 'hidden',
                    }}>
                        {[
                            { method: 'GET', path: '/api/jarvis/status', description: 'Enhanced system status with market health' },
                            { method: 'GET', path: '/api/jarvis/market-overview', description: 'Complete market overview with sectors' },
                            { method: 'GET', path: '/api/jarvis/analysis/{symbol}', description: 'Quantitative analysis (8 indicators)' },
                            { method: 'GET', path: '/api/jarvis/events', description: 'Active market events with decay weights' },
                            { method: 'GET', path: '/api/jarvis/engines', description: 'All engine statuses' },
                            { method: 'GET', path: '/api/jarvis/charts/{symbol}', description: 'Chart data for a symbol' },
                            { method: 'GET', path: '/api/jarvis/india', description: 'India NSE market snapshot' },
                            { method: 'GET', path: '/api/jarvis/india/analysis/{symbol}', description: 'Quantitative analysis for Indian stock' },
                            { method: 'GET', path: '/api/jarvis/india/sector/{sector}', description: 'Indian sector analysis' },
                            { method: 'POST', path: '/command', description: 'Execute terminal commands' },
                            { method: 'GET', path: '/status', description: 'Basic system state' },
                            { method: 'GET', path: '/market', description: 'All ticker data' },
                        ].map((endpoint, idx) => (
                            <div
                                key={idx}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '16px',
                                    padding: '12px 16px',
                                    borderBottom: idx < 11 ? '1px solid var(--border-color)' : 'none',
                                }}
                            >
                                <span style={{
                                    padding: '4px 10px',
                                    background: endpoint.method === 'GET' ? 'rgba(34,197,94,0.2)' : 'rgba(59,130,246,0.2)',
                                    color: endpoint.method === 'GET' ? 'var(--accent-green)' : 'var(--accent-blue)',
                                    borderRadius: '4px',
                                    fontSize: '11px',
                                    fontWeight: '600',
                                    minWidth: '50px',
                                    textAlign: 'center',
                                }}>
                                    {endpoint.method}
                                </span>
                                <code style={{ color: 'var(--accent-cyan)', fontSize: '13px', minWidth: '280px' }}>
                                    :8000{endpoint.path}
                                </code>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                                    {endpoint.description}
                                </span>
                            </div>
                        ))}
                    </div>
                )
            }

            {/* Info Banner */}
            <div style={{
                marginTop: '24px',
                padding: '16px 20px',
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
            }}>
                <Server size={20} style={{ color: 'var(--accent-blue)', marginTop: '2px' }} />
                <div>
                    <div style={{ fontWeight: '500', marginBottom: '4px' }}>Start the Finance-X Server</div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        Run <code style={{
                            padding: '2px 8px',
                            background: 'var(--bg-tertiary)',
                            borderRadius: '4px'
                        }}>cd ~/FinanceX && python server.py</code> to enable real-time monitoring.
                    </div>
                </div>
            </div>
        </div >
    );
}

export default ExecutionMonitor;

