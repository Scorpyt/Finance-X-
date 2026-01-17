import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield,
    Mail,
    Lock,
    ArrowRight,
    CheckCircle,
    AlertCircle,
    Loader2,
    Eye,
    EyeOff,
    KeyRound,
    Fingerprint,
    ShieldCheck,
    ShieldAlert,
    Clock,
    Users
} from 'lucide-react';

// Enterprise API endpoint
const AUTH_API = 'http://localhost:3001/api/auth';

// Cloudflare-style colors
const cfColors = {
    orange: '#f6821f',
    orangeLight: '#fbad41',
    dark: '#0d1117',
    darker: '#010409',
    border: '#30363d',
    text: '#c9d1d9',
    textMuted: '#8b949e',
    red: '#ef4444',
    green: '#22c55e',
};

function CloudflareAuth({ onAuthenticated }) {
    const [step, setStep] = useState('email'); // email, code, authenticating, success, denied
    const [email, setEmail] = useState('');
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [codeExpiry, setCodeExpiry] = useState(null);
    const [deniedMessage, setDeniedMessage] = useState('');

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!email || !email.includes('@')) {
            setError('Please enter a valid email address');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch(`${AUTH_API}/check-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email.toLowerCase().trim() })
            });

            const data = await response.json();

            if (!response.ok) {
                // Access denied - not in allowlist
                setIsLoading(false);
                setDeniedMessage(data.message);
                setStep('denied');
                return;
            }

            setCodeExpiry(data.expiresIn);
            setIsLoading(false);
            setStep('code');
        } catch (err) {
            setIsLoading(false);
            setError('Unable to connect to security server. Please try again.');
        }
    };

    const handleCodeSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (code.length !== 6) {
            setError('Please enter a 6-digit code');
            return;
        }

        setIsLoading(true);
        setStep('authenticating');

        try {
            const response = await fetch(`${AUTH_API}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email.toLowerCase().trim(),
                    code
                })
            });

            const data = await response.json();

            if (!response.ok) {
                setIsLoading(false);
                setStep('code');

                if (data.error === 'CODE_EXPIRED') {
                    setError('Code expired. A new code has been sent to your email.');
                } else {
                    setError(data.message || 'Invalid security code');
                }
                return;
            }

            // Success!
            setStep('success');

            // Store enterprise session
            localStorage.setItem('jarvis_auth', JSON.stringify({
                email: data.user.email,
                token: data.token,
                role: data.user.role,
                permissions: data.user.permissions,
                timestamp: Date.now(),
                expires: Date.now() + (60 * 60 * 1000), // 1 hour (matches code rotation)
            }));

            await new Promise(resolve => setTimeout(resolve, 1500));
            onAuthenticated();
        } catch (err) {
            setIsLoading(false);
            setStep('code');
            setError('Connection error. Please try again.');
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: `linear-gradient(135deg, ${cfColors.darker} 0%, ${cfColors.dark} 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}>
            {/* Background pattern */}
            <div style={{
                position: 'fixed',
                inset: 0,
                backgroundImage: `radial-gradient(circle at 25px 25px, ${cfColors.border} 2%, transparent 0%)`,
                backgroundSize: '50px 50px',
                opacity: 0.3,
                pointerEvents: 'none',
            }} />

            {/* Enterprise badge */}
            <div style={{
                position: 'fixed',
                top: '20px',
                right: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                background: 'rgba(246,130,31,0.1)',
                border: '1px solid rgba(246,130,31,0.3)',
                borderRadius: '20px',
                color: cfColors.orange,
                fontSize: '12px',
                fontWeight: '500',
            }}>
                <ShieldCheck size={14} />
                Enterprise Security
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                    width: '100%',
                    maxWidth: '420px',
                    position: 'relative',
                    zIndex: 1,
                }}
            >
                {/* Header */}
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', delay: 0.2 }}
                        style={{
                            width: '80px',
                            height: '80px',
                            margin: '0 auto 20px',
                            background: `linear-gradient(135deg, ${cfColors.orange}, ${cfColors.orangeLight})`,
                            borderRadius: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: `0 20px 60px ${cfColors.orange}40`,
                        }}
                    >
                        <Shield size={40} color="white" />
                    </motion.div>
                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: '700',
                        color: 'white',
                        margin: '0 0 8px 0',
                    }}>
                        JARVIS Access
                    </h1>
                    <p style={{
                        color: cfColors.textMuted,
                        fontSize: '14px',
                        margin: 0,
                    }}>
                        Enterprise Zero Trust Security
                    </p>
                </div>

                {/* Auth Card */}
                <motion.div
                    layout
                    style={{
                        background: cfColors.dark,
                        borderRadius: '16px',
                        border: `1px solid ${cfColors.border}`,
                        padding: '32px',
                        boxShadow: '0 25px 80px rgba(0,0,0,0.5)',
                    }}
                >
                    <AnimatePresence mode="wait">
                        {/* Email Step */}
                        {step === 'email' && (
                            <motion.form
                                key="email"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                onSubmit={handleEmailSubmit}
                            >
                                <div style={{ marginBottom: '24px' }}>
                                    <h2 style={{
                                        fontSize: '18px',
                                        fontWeight: '600',
                                        color: 'white',
                                        margin: '0 0 8px 0',
                                    }}>
                                        Enterprise Sign In
                                    </h2>
                                    <p style={{ color: cfColors.textMuted, fontSize: '14px', margin: 0 }}>
                                        Access restricted to authorized personnel only
                                    </p>
                                </div>

                                {/* Authorized users badge */}
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    padding: '10px 14px',
                                    background: 'rgba(59,130,246,0.1)',
                                    border: '1px solid rgba(59,130,246,0.3)',
                                    borderRadius: '8px',
                                    marginBottom: '20px',
                                    color: '#3b82f6',
                                    fontSize: '12px',
                                }}>
                                    <Users size={14} />
                                    <span>Only 3 authorized users can access this system</span>
                                </div>

                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{
                                        display: 'block',
                                        fontSize: '13px',
                                        color: cfColors.text,
                                        marginBottom: '8px',
                                        fontWeight: '500',
                                    }}>
                                        Enterprise Email
                                    </label>
                                    <div style={{ position: 'relative' }}>
                                        <Mail size={18} style={{
                                            position: 'absolute',
                                            left: '14px',
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            color: cfColors.textMuted,
                                        }} />
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="authorized-user@domain.com"
                                            style={{
                                                width: '100%',
                                                padding: '14px 14px 14px 44px',
                                                background: cfColors.darker,
                                                border: `1px solid ${cfColors.border}`,
                                                borderRadius: '10px',
                                                color: 'white',
                                                fontSize: '15px',
                                                outline: 'none',
                                                transition: 'border-color 0.2s',
                                                boxSizing: 'border-box',
                                            }}
                                            onFocus={(e) => e.target.style.borderColor = cfColors.orange}
                                            onBlur={(e) => e.target.style.borderColor = cfColors.border}
                                        />
                                    </div>
                                </div>

                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px',
                                            padding: '12px',
                                            background: 'rgba(239, 68, 68, 0.1)',
                                            border: '1px solid rgba(239, 68, 68, 0.3)',
                                            borderRadius: '8px',
                                            marginBottom: '20px',
                                        }}
                                    >
                                        <AlertCircle size={16} color="#ef4444" />
                                        <span style={{ color: '#ef4444', fontSize: '13px' }}>{error}</span>
                                    </motion.div>
                                )}

                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    style={{
                                        width: '100%',
                                        padding: '14px',
                                        background: `linear-gradient(135deg, ${cfColors.orange}, ${cfColors.orangeLight})`,
                                        border: 'none',
                                        borderRadius: '10px',
                                        color: 'white',
                                        fontSize: '15px',
                                        fontWeight: '600',
                                        cursor: isLoading ? 'not-allowed' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '8px',
                                        transition: 'all 0.2s',
                                        opacity: isLoading ? 0.7 : 1,
                                    }}
                                >
                                    {isLoading ? (
                                        <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                                    ) : (
                                        <>
                                            Request Access
                                            <ArrowRight size={18} />
                                        </>
                                    )}
                                </button>
                            </motion.form>
                        )}

                        {/* Access Denied Step */}
                        {step === 'denied' && (
                            <motion.div
                                key="denied"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0 }}
                                style={{ textAlign: 'center', padding: '20px 0' }}
                            >
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: 'spring' }}
                                    style={{
                                        width: '70px',
                                        height: '70px',
                                        margin: '0 auto 20px',
                                        background: 'rgba(239, 68, 68, 0.2)',
                                        borderRadius: '50%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <ShieldAlert size={36} color="#ef4444" />
                                </motion.div>
                                <h3 style={{ color: '#ef4444', margin: '0 0 12px 0', fontSize: '20px' }}>
                                    ACCESS DENIED
                                </h3>
                                <p style={{ color: cfColors.textMuted, fontSize: '14px', margin: '0 0 20px 0', lineHeight: 1.5 }}>
                                    {deniedMessage}
                                </p>
                                <div style={{
                                    padding: '16px',
                                    background: 'rgba(239, 68, 68, 0.1)',
                                    border: '1px solid rgba(239, 68, 68, 0.3)',
                                    borderRadius: '10px',
                                    marginBottom: '20px',
                                }}>
                                    <p style={{ color: '#ef4444', fontSize: '12px', margin: 0, fontWeight: '500' }}>
                                        ⚠️ This access attempt has been logged
                                    </p>
                                </div>
                                <button
                                    onClick={() => { setStep('email'); setEmail(''); setError(''); }}
                                    style={{
                                        padding: '12px 24px',
                                        background: 'transparent',
                                        border: `1px solid ${cfColors.border}`,
                                        borderRadius: '8px',
                                        color: cfColors.text,
                                        fontSize: '14px',
                                        cursor: 'pointer',
                                    }}
                                >
                                    Try Different Email
                                </button>
                            </motion.div>
                        )}

                        {/* Code Step */}
                        {step === 'code' && (
                            <motion.form
                                key="code"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                onSubmit={handleCodeSubmit}
                            >
                                <div style={{ marginBottom: '24px' }}>
                                    <h2 style={{
                                        fontSize: '18px',
                                        fontWeight: '600',
                                        color: 'white',
                                        margin: '0 0 8px 0',
                                    }}>
                                        Enter Security Code
                                    </h2>
                                    <p style={{ color: cfColors.textMuted, fontSize: '14px', margin: 0 }}>
                                        Code sent to <strong style={{ color: cfColors.orange }}>{email}</strong>
                                    </p>
                                </div>

                                {/* Code expiry timer */}
                                {codeExpiry && (
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '8px',
                                        padding: '10px',
                                        background: 'rgba(34,197,94,0.1)',
                                        border: '1px solid rgba(34,197,94,0.3)',
                                        borderRadius: '8px',
                                        marginBottom: '20px',
                                        color: '#22c55e',
                                        fontSize: '12px',
                                    }}>
                                        <Clock size={14} />
                                        <span>Code valid for {codeExpiry.minutes} minutes</span>
                                    </div>
                                )}

                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{
                                        display: 'block',
                                        fontSize: '13px',
                                        color: cfColors.text,
                                        marginBottom: '8px',
                                        fontWeight: '500',
                                    }}>
                                        Security Code
                                    </label>
                                    <div style={{ position: 'relative' }}>
                                        <KeyRound size={18} style={{
                                            position: 'absolute',
                                            left: '14px',
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            color: cfColors.textMuted,
                                        }} />
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            value={code}
                                            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                            placeholder="000000"
                                            maxLength={6}
                                            style={{
                                                width: '100%',
                                                padding: '14px 44px',
                                                background: cfColors.darker,
                                                border: `1px solid ${cfColors.border}`,
                                                borderRadius: '10px',
                                                color: 'white',
                                                fontSize: '20px',
                                                fontFamily: 'monospace',
                                                letterSpacing: '8px',
                                                textAlign: 'center',
                                                outline: 'none',
                                                boxSizing: 'border-box',
                                            }}
                                            onFocus={(e) => e.target.style.borderColor = cfColors.orange}
                                            onBlur={(e) => e.target.style.borderColor = cfColors.border}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            style={{
                                                position: 'absolute',
                                                right: '14px',
                                                top: '50%',
                                                transform: 'translateY(-50%)',
                                                background: 'none',
                                                border: 'none',
                                                cursor: 'pointer',
                                                color: cfColors.textMuted,
                                                padding: '4px',
                                            }}
                                        >
                                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </button>
                                    </div>
                                </div>

                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px',
                                            padding: '12px',
                                            background: 'rgba(239, 68, 68, 0.1)',
                                            border: '1px solid rgba(239, 68, 68, 0.3)',
                                            borderRadius: '8px',
                                            marginBottom: '20px',
                                        }}
                                    >
                                        <AlertCircle size={16} color="#ef4444" />
                                        <span style={{ color: '#ef4444', fontSize: '13px' }}>{error}</span>
                                    </motion.div>
                                )}

                                <button
                                    type="submit"
                                    disabled={isLoading || code.length !== 6}
                                    style={{
                                        width: '100%',
                                        padding: '14px',
                                        background: code.length === 6
                                            ? `linear-gradient(135deg, ${cfColors.orange}, ${cfColors.orangeLight})`
                                            : cfColors.border,
                                        border: 'none',
                                        borderRadius: '10px',
                                        color: 'white',
                                        fontSize: '15px',
                                        fontWeight: '600',
                                        cursor: code.length === 6 ? 'pointer' : 'not-allowed',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '8px',
                                        transition: 'all 0.2s',
                                    }}
                                >
                                    <Lock size={18} />
                                    Verify & Access JARVIS
                                </button>

                                <button
                                    type="button"
                                    onClick={() => { setStep('email'); setCode(''); setError(''); }}
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        background: 'transparent',
                                        border: 'none',
                                        color: cfColors.textMuted,
                                        fontSize: '13px',
                                        cursor: 'pointer',
                                        marginTop: '12px',
                                    }}
                                >
                                    ← Use a different email
                                </button>
                            </motion.form>
                        )}

                        {/* Authenticating Step */}
                        {step === 'authenticating' && (
                            <motion.div
                                key="authenticating"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                style={{ textAlign: 'center', padding: '20px 0' }}
                            >
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                    style={{
                                        width: '60px',
                                        height: '60px',
                                        margin: '0 auto 20px',
                                        border: `3px solid ${cfColors.border}`,
                                        borderTopColor: cfColors.orange,
                                        borderRadius: '50%',
                                    }}
                                />
                                <h3 style={{ color: 'white', margin: '0 0 8px 0' }}>Authenticating...</h3>
                                <p style={{ color: cfColors.textMuted, fontSize: '14px', margin: 0 }}>
                                    Verifying enterprise credentials
                                </p>
                            </motion.div>
                        )}

                        {/* Success Step */}
                        {step === 'success' && (
                            <motion.div
                                key="success"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0 }}
                                style={{ textAlign: 'center', padding: '20px 0' }}
                            >
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: 'spring', delay: 0.2 }}
                                    style={{
                                        width: '70px',
                                        height: '70px',
                                        margin: '0 auto 20px',
                                        background: 'rgba(34, 197, 94, 0.2)',
                                        borderRadius: '50%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <CheckCircle size={40} color="#22c55e" />
                                </motion.div>
                                <h3 style={{ color: 'white', margin: '0 0 8px 0' }}>Access Granted</h3>
                                <p style={{ color: cfColors.textMuted, fontSize: '14px', margin: 0 }}>
                                    Welcome to JARVIS Enterprise
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                {/* Footer */}
                <div style={{
                    textAlign: 'center',
                    marginTop: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    color: cfColors.textMuted,
                    fontSize: '12px',
                }}>
                    <ShieldCheck size={14} />
                    <span>Secured by Cloudflare Zero Trust</span>
                </div>
            </motion.div>

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
}

export default CloudflareAuth;
