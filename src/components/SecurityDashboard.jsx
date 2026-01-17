import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield,
    ShieldCheck,
    ShieldAlert,
    Lock,
    Key,
    UserCheck,
    Globe,
    Clock,
    LogOut,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Fingerprint,
    Eye,
    Server,
    Activity,
    RefreshCw,
    Terminal,
    Wifi,
    WifiOff,
    AlertCircle,
    User,
    Mail,
    Timer
} from 'lucide-react';

const AUTH_API = 'http://localhost:3001/api/auth';

function SecurityDashboard({ userEmail, onLogout }) {
    const authData = JSON.parse(localStorage.getItem('jarvis_auth') || '{}');
    const sessionStart = authData.timestamp ? new Date(authData.timestamp) : new Date();
    const sessionExpiry = authData.expires ? new Date(authData.expires) : new Date();

    // Real-time logs state
    const [liveLogs, setLiveLogs] = useState([]);
    const [serverStatus, setServerStatus] = useState('connecting');
    const [codeExpiry, setCodeExpiry] = useState(null);
    const [authorizedCount, setAuthorizedCount] = useState(3);
    const [isAutoRefresh, setIsAutoRefresh] = useState(true);
    const logsContainerRef = useRef(null);

    const formatDate = (date) => {
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const formatTime = (timestamp) => {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    const formatTimeRemaining = (expiryTime) => {
        const now = Date.now();
        const remaining = expiryTime - now;
        if (remaining <= 0) return 'Expired';
        const mins = Math.floor(remaining / 60000);
        const secs = Math.floor((remaining % 60000) / 1000);
        return `${mins}m ${secs}s`;
    };

    // Fetch logs from auth server
    const fetchLogs = async () => {
        try {
            const response = await fetch(`${AUTH_API}/logs`);
            const data = await response.json();
            setLiveLogs(data.logs || []);
            setCodeExpiry(data.currentCodeExpiry);
            setAuthorizedCount(data.authorizedUsers || 3);
            setServerStatus('connected');
        } catch (error) {
            setServerStatus('disconnected');
        }
    };

    // Auto-refresh logs
    useEffect(() => {
        fetchLogs();
        let interval;
        if (isAutoRefresh) {
            interval = setInterval(fetchLogs, 2000); // Refresh every 2 seconds
        }
        return () => clearInterval(interval);
    }, [isAutoRefresh]);

    // Auto-scroll logs
    useEffect(() => {
        if (logsContainerRef.current) {
            logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight;
        }
    }, [liveLogs]);

    // Update code expiry timer
    const [timeRemaining, setTimeRemaining] = useState('');
    useEffect(() => {
        const timer = setInterval(() => {
            if (codeExpiry) {
                setTimeRemaining(formatTimeRemaining(codeExpiry));
            }
        }, 1000);
        return () => clearInterval(timer);
    }, [codeExpiry]);

    const securityFeatures = [
        {
            name: 'Zero Trust Access',
            status: 'active',
            description: 'All access requests are verified before granting access',
            icon: ShieldCheck,
            color: '#22c55e',
        },
        {
            name: 'Email Verification',
            status: 'active',
            description: 'One-time password sent to verified email addresses',
            icon: UserCheck,
            color: '#22c55e',
        },
        {
            name: 'Session Management',
            status: 'active',
            description: '24-hour session tokens with automatic expiration',
            icon: Clock,
            color: '#22c55e',
        },
        {
            name: 'HTTPS Encryption',
            status: 'recommended',
            description: 'Enable HTTPS in production for encrypted connections',
            icon: Lock,
            color: '#f97316',
        },
        {
            name: 'IP Allowlisting',
            status: 'available',
            description: 'Restrict access to specific IP addresses',
            icon: Globe,
            color: '#3b82f6',
        },
        {
            name: 'Hardware Keys',
            status: 'available',
            description: 'Support for WebAuthn/FIDO2 hardware security keys',
            icon: Key,
            color: '#3b82f6',
        },
    ];

    const getLogIcon = (log) => {
        if (log.action === 'email_check') {
            return log.authorized ?
                <CheckCircle size={14} color="#22c55e" /> :
                <XCircle size={14} color="#ef4444" />;
        }
        if (log.action === 'code_verify') {
            return log.codeMatch ?
                <CheckCircle size={14} color="#22c55e" /> :
                <AlertCircle size={14} color="#f97316" />;
        }
        return <Activity size={14} color="#3b82f6" />;
    };

    const getLogColor = (log) => {
        if (log.action === 'email_check' && !log.authorized) return '#ef4444';
        if (log.action === 'code_verify' && !log.codeMatch) return '#f97316';
        return '#22c55e';
    };

    const getLogMessage = (log) => {
        if (log.action === 'email_check') {
            return log.authorized ?
                `✓ Email verified: ${log.email}` :
                `✗ BLOCKED: ${log.email}`;
        }
        if (log.action === 'code_verify') {
            return log.codeMatch ?
                `✓ Code verified: ${log.email}` :
                `⚠ Invalid code attempt: ${log.email}`;
        }
        return log.action;
    };

    return (
        <div style={{ padding: '0' }}>
            {/* Security Overview Cards */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '20px',
                marginBottom: '32px',
            }}>
                {/* Session Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                        padding: '24px',
                        background: 'linear-gradient(135deg, rgba(34,197,94,0.1), rgba(34,197,94,0.05))',
                        borderRadius: '16px',
                        border: '1px solid rgba(34,197,94,0.3)',
                    }}
                >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            borderRadius: '12px',
                            background: 'rgba(34,197,94,0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <ShieldCheck size={24} color="#22c55e" />
                        </div>
                        <div>
                            <h3 style={{ margin: 0, fontSize: '16px' }}>Session Active</h3>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>Authenticated</p>
                        </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>User</span>
                            <span style={{ color: '#22c55e', fontWeight: '500' }}>{userEmail}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Started</span>
                            <span>{formatDate(sessionStart)}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Expires</span>
                            <span>{formatDate(sessionExpiry)}</span>
                        </div>
                    </div>
                </motion.div>

                {/* Code Rotation Status */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    style={{
                        padding: '24px',
                        background: 'var(--bg-secondary)',
                        borderRadius: '16px',
                        border: '1px solid var(--border-color)',
                    }}
                >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            borderRadius: '12px',
                            background: 'rgba(246,130,31,0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <Timer size={24} color="#f6821f" />
                        </div>
                        <div>
                            <h3 style={{ margin: 0, fontSize: '16px' }}>Code Rotation</h3>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>Hourly auto-refresh</p>
                        </div>
                    </div>
                    <div style={{
                        textAlign: 'center',
                        padding: '16px',
                        background: 'var(--bg-tertiary)',
                        borderRadius: '10px'
                    }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: '#f6821f', fontFamily: 'monospace' }}>
                            {timeRemaining || '-- : --'}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                            Until next code rotation
                        </div>
                    </div>
                </motion.div>

                {/* Logout Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    style={{
                        padding: '24px',
                        background: 'var(--bg-secondary)',
                        borderRadius: '16px',
                        border: '1px solid var(--border-color)',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                    }}
                >
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                            <div style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '12px',
                                background: 'rgba(239,68,68,0.2)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}>
                                <LogOut size={24} color="#ef4444" />
                            </div>
                            <div>
                                <h3 style={{ margin: 0, fontSize: '16px' }}>End Session</h3>
                                <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>Sign out securely</p>
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={onLogout}
                        style={{
                            padding: '12px',
                            background: 'rgba(239,68,68,0.1)',
                            border: '1px solid rgba(239,68,68,0.3)',
                            borderRadius: '8px',
                            color: '#ef4444',
                            fontSize: '14px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                            e.target.style.background = '#ef4444';
                            e.target.style.color = 'white';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.background = 'rgba(239,68,68,0.1)';
                            e.target.style.color = '#ef4444';
                        }}
                    >
                        <LogOut size={16} />
                        Sign Out
                    </button>
                </motion.div>
            </div>

            {/* Real-Time Access Logs */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <h3 style={{ fontSize: '14px', color: 'var(--text-muted)', margin: 0 }}>
                            REAL-TIME ACCESS LOGS
                        </h3>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '4px 10px',
                            borderRadius: '12px',
                            background: serverStatus === 'connected' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
                            border: `1px solid ${serverStatus === 'connected' ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
                        }}>
                            {serverStatus === 'connected' ? (
                                <>
                                    <motion.div
                                        animate={{ opacity: [1, 0.3, 1] }}
                                        transition={{ duration: 1.5, repeat: Infinity }}
                                        style={{
                                            width: '6px',
                                            height: '6px',
                                            borderRadius: '50%',
                                            background: '#22c55e',
                                        }}
                                    />
                                    <span style={{ fontSize: '11px', color: '#22c55e' }}>Live</span>
                                </>
                            ) : (
                                <>
                                    <WifiOff size={12} color="#ef4444" />
                                    <span style={{ fontSize: '11px', color: '#ef4444' }}>Offline</span>
                                </>
                            )}
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <button
                            onClick={() => setIsAutoRefresh(!isAutoRefresh)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                padding: '6px 12px',
                                background: isAutoRefresh ? 'rgba(59,130,246,0.1)' : 'transparent',
                                border: `1px solid ${isAutoRefresh ? 'rgba(59,130,246,0.3)' : 'var(--border-color)'}`,
                                borderRadius: '6px',
                                color: isAutoRefresh ? '#3b82f6' : 'var(--text-muted)',
                                fontSize: '12px',
                                cursor: 'pointer',
                            }}
                        >
                            <RefreshCw size={12} style={{
                                animation: isAutoRefresh ? 'spin 2s linear infinite' : 'none'
                            }} />
                            Auto
                        </button>
                        <button
                            onClick={fetchLogs}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                padding: '6px 12px',
                                background: 'transparent',
                                border: '1px solid var(--border-color)',
                                borderRadius: '6px',
                                color: 'var(--text-muted)',
                                fontSize: '12px',
                                cursor: 'pointer',
                            }}
                        >
                            <RefreshCw size={12} />
                            Refresh
                        </button>
                    </div>
                </div>

                {/* Log Terminal */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                        background: '#0d1117',
                        borderRadius: '12px',
                        border: '1px solid var(--border-color)',
                        overflow: 'hidden',
                    }}
                >
                    {/* Terminal Header */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '12px 16px',
                        background: '#161b22',
                        borderBottom: '1px solid var(--border-color)',
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <Terminal size={14} color="#8b949e" />
                            <span style={{ fontSize: '12px', color: '#8b949e' }}>
                                auth-server.cjs — Access Monitor
                            </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '11px', color: '#8b949e' }}>
                                {liveLogs.length} events
                            </span>
                        </div>
                    </div>

                    {/* Log Content */}
                    <div
                        ref={logsContainerRef}
                        style={{
                            height: '300px',
                            overflowY: 'auto',
                            padding: '12px 16px',
                            fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace',
                            fontSize: '12px',
                            lineHeight: '1.8',
                        }}
                    >
                        {liveLogs.length === 0 ? (
                            <div style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                height: '100%',
                                color: '#8b949e',
                                gap: '8px',
                            }}>
                                <Terminal size={32} />
                                <span>Waiting for access attempts...</span>
                                <span style={{ fontSize: '11px' }}>
                                    {serverStatus === 'connected' ? 'Connected to auth server' : 'Auth server offline'}
                                </span>
                            </div>
                        ) : (
                            liveLogs.map((log, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'flex-start',
                                        gap: '12px',
                                        padding: '6px 0',
                                        borderBottom: '1px solid rgba(48,54,61,0.5)',
                                    }}
                                >
                                    {/* Timestamp */}
                                    <span style={{
                                        color: '#8b949e',
                                        minWidth: '80px',
                                        flexShrink: 0,
                                    }}>
                                        {formatTime(log.timestamp)}
                                    </span>

                                    {/* Icon */}
                                    <span style={{ flexShrink: 0 }}>
                                        {getLogIcon(log)}
                                    </span>

                                    {/* Message */}
                                    <span style={{
                                        color: getLogColor(log),
                                        flex: 1,
                                    }}>
                                        {getLogMessage(log)}
                                    </span>

                                    {/* IP */}
                                    {log.ip && (
                                        <span style={{
                                            color: '#8b949e',
                                            fontSize: '11px',
                                        }}>
                                            {log.ip.replace('::ffff:', '')}
                                        </span>
                                    )}
                                </motion.div>
                            ))
                        )}
                    </div>
                </motion.div>
            </div>

            {/* Security Features */}
            <div style={{ marginBottom: '32px' }}>
                <h3 style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px' }}>SECURITY FEATURES</h3>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                    gap: '12px',
                }}>
                    {securityFeatures.map((feature, idx) => (
                        <motion.div
                            key={feature.name}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            style={{
                                padding: '16px',
                                background: 'var(--bg-secondary)',
                                borderRadius: '12px',
                                border: '1px solid var(--border-color)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '14px',
                            }}
                        >
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '10px',
                                background: `${feature.color}20`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexShrink: 0,
                            }}>
                                <feature.icon size={20} color={feature.color} />
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                    <span style={{ fontWeight: '500', fontSize: '14px' }}>{feature.name}</span>
                                    <span style={{
                                        padding: '2px 8px',
                                        borderRadius: '4px',
                                        fontSize: '10px',
                                        fontWeight: '600',
                                        background: feature.status === 'active' ? 'rgba(34,197,94,0.2)' :
                                            feature.status === 'recommended' ? 'rgba(249,115,22,0.2)' :
                                                'rgba(59,130,246,0.2)',
                                        color: feature.status === 'active' ? '#22c55e' :
                                            feature.status === 'recommended' ? '#f97316' :
                                                '#3b82f6',
                                    }}>
                                        {feature.status.toUpperCase()}
                                    </span>
                                </div>
                                <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>
                                    {feature.description}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>

            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
}

export default SecurityDashboard;
