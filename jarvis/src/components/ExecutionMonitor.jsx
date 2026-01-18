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
    TrendingUp
} from 'lucide-react';

function ExecutionMonitor() {
    const [serverStatus, setServerStatus] = useState('checking');
    const [systemMetrics, setSystemMetrics] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(new Date());

    const checkServer = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/status', {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            if (response.ok) {
                const data = await response.json();
                setServerStatus('online');
                setSystemMetrics(data);
            } else {
                setServerStatus('offline');
            }
        } catch {
            setServerStatus('offline');
        }
        setLastUpdate(new Date());
    };

    useEffect(() => {
        checkServer();
        const interval = setInterval(checkServer, 10000);
        return () => clearInterval(interval);
    }, []);

    const getStateColor = (state) => {
        switch (state) {
            case 'STABLE': return 'var(--accent-green)';
            case 'HIGH_VOL': return 'var(--accent-orange)';
            case 'CRASH': return 'var(--accent-red)';
            default: return 'var(--text-muted)';
        }
    };

    const getStateBadgeClass = (state) => {
        switch (state) {
            case 'STABLE': return 'stable';
            case 'HIGH_VOL': return 'high-vol';
            case 'CRASH': return 'crash';
            default: return '';
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
                            http://localhost:8000
                        </div>
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
                        onClick={checkServer}
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
                        }}
                    >
                        <RefreshCw size={14} />
                        Refresh
                    </button>
                </div>
            </div>

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

                {/* Simulation Time */}
                <div className="monitor-card">
                    <div className="monitor-card-header">
                        <div className="monitor-card-icon green">
                            <Clock size={20} />
                        </div>
                        <div>
                            <div className="monitor-card-title">Simulation Time</div>
                            <div className="monitor-card-subtitle">Virtual market clock</div>
                        </div>
                    </div>
                    {serverStatus === 'online' && systemMetrics ? (
                        <>
                            <div className="monitor-value" style={{ fontSize: '24px' }}>
                                {new Date(systemMetrics.time).toLocaleDateString('en-US', {
                                    month: 'short',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </div>
                            <div className="monitor-label">Virtual timestamp</div>
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
                        <div className="monitor-card-icon orange">
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

                {/* Last User Command */}
                <div className="monitor-card">
                    <div className="monitor-card-header">
                        <div className="monitor-card-icon purple">
                            <Terminal size={20} />
                        </div>
                        <div>
                            <div className="monitor-card-title">User Activity</div>
                            <div className="monitor-card-subtitle">Last executed command</div>
                        </div>
                    </div>
                    {serverStatus === 'online' && systemMetrics?.lastCommand ? (
                        <>
                            <div style={{
                                fontFamily: 'monospace',
                                fontSize: '16px',
                                background: 'rgba(0,0,0,0.3)',
                                padding: '8px',
                                borderRadius: '6px',
                                border: '1px solid var(--border-color)',
                                color: 'var(--accent-cyan)'
                            }}>
                                > {systemMetrics.lastCommand.cmd}
                            </div>
                            <div style={{
                                marginTop: '8px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                fontSize: '11px',
                                color: 'var(--text-secondary)'
                            }}>
                                <span>{systemMetrics.lastCommand.status}</span>
                                <span>{systemMetrics.lastCommand.time}</span>
                            </div>
                        </>
                    ) : (
                        <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                            Waiting for input...
                        </div>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="monitor-card">
                    <div className="monitor-card-header">
                        <div className="monitor-card-icon red">
                            <Terminal size={20} />
                        </div>
                        <div>
                            <div className="monitor-card-title">Quick Actions</div>
                            <div className="monitor-card-subtitle">Server commands</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <button
                            onClick={() => window.open('http://localhost:8000', '_blank')}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '10px 16px',
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '8px',
                                color: 'var(--text-primary)',
                                fontSize: '13px',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                            }}
                        >
                            <Server size={14} />
                            Open Finance-X Terminal
                        </button>
                        <button
                            onClick={() => window.open('http://localhost:8001/health', '_blank')}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '10px 16px',
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '8px',
                                color: 'var(--text-primary)',
                                fontSize: '13px',
                                cursor: 'pointer',
                            }}
                        >
                            <Activity size={14} />
                            Bloomberg Service Health
                        </button>
                    </div>
                </div>
            </div>

            {/* API Endpoints */}
            <div style={{ marginTop: '24px' }}>
                <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Available API Endpoints</h3>
                <div style={{
                    background: 'var(--bg-secondary)',
                    borderRadius: '12px',
                    border: '1px solid var(--border-color)',
                    overflow: 'hidden',
                }}>
                    {[
                        { method: 'POST', path: '/command', description: 'Execute terminal commands' },
                        { method: 'GET', path: '/status', description: 'Get system state' },
                        { method: 'GET', path: '/market', description: 'Get all ticker data' },
                        { method: 'GET', path: '/system/diagnostics', description: 'Hardware metrics' },
                        { method: 'GET', path: '/health', description: 'Bloomberg service health', port: 8001 },
                        { method: 'GET', path: '/fx-rates', description: 'Live FX rates', port: 8001 },
                        { method: 'GET', path: '/sectors', description: 'Sector performance', port: 8001 },
                    ].map((endpoint, idx) => (
                        <div
                            key={idx}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '16px',
                                padding: '12px 16px',
                                borderBottom: idx < 6 ? '1px solid var(--border-color)' : 'none',
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
                            <code style={{ color: 'var(--accent-cyan)', fontSize: '13px', minWidth: '200px' }}>
                                :{endpoint.port || 8000}{endpoint.path}
                            </code>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                                {endpoint.description}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

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
                        }}>cd ~/Finance-X- && python server.py</code> to enable real-time monitoring.
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ExecutionMonitor;
