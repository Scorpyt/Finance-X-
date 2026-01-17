import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Network,
  FolderTree,
  Workflow,
  Activity,
  FileCode,
  Cpu,
  Database,
  Puzzle,
  X,
  ExternalLink,
  Server,
  Code,
  Box,
  Layers,
  HardDrive,
  ChevronRight,
  Shield,
  LogOut
} from 'lucide-react';
import ArchitectureDiagram from './components/ArchitectureDiagram';
import ModuleExplorer from './components/ModuleExplorer';
import WorkflowVisualizer from './components/WorkflowVisualizer';
import ExecutionMonitor from './components/ExecutionMonitor';
import CloudflareAuth from './components/CloudflareAuth';
import SecurityDashboard from './components/SecurityDashboard';
import { modules, getAllModules } from './data/architecture';
import './App.css';

// Stats Detail Modal Component
const StatsDetailModal = ({ stat, onClose }) => {
  if (!stat) return null;

  const openInEditor = (path) => {
    window.open(`vscode://file${path}`, '_blank');
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px',
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: 'spring', damping: 25 }}
        style={{
          background: 'var(--bg-secondary)',
          borderRadius: '16px',
          border: '1px solid var(--border-color)',
          width: '100%',
          maxWidth: '700px',
          maxHeight: '80vh',
          overflow: 'hidden',
          boxShadow: '0 25px 80px rgba(0,0,0,0.5)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          background: `linear-gradient(135deg, ${stat.color}15, ${stat.color}05)`,
          borderBottom: `1px solid ${stat.color}30`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: `${stat.color}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: stat.color,
            }}>
              <stat.icon size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '22px', fontWeight: '700', margin: 0 }}>{stat.title}</h2>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>{stat.subtitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              color: 'var(--text-muted)',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', maxHeight: '60vh', overflowY: 'auto' }}>
          {/* Summary Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '16px',
            marginBottom: '24px',
          }}>
            {stat.summaryStats?.map((s, i) => (
              <div key={i} style={{
                padding: '16px',
                background: 'var(--bg-tertiary)',
                borderRadius: '12px',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '28px', fontWeight: '700', color: stat.color }}>{s.value}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Description */}
          {stat.description && (
            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>OVERVIEW</h4>
              <p style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-secondary)', margin: 0 }}>
                {stat.description}
              </p>
            </div>
          )}

          {/* Items List */}
          <div>
            <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
              {stat.itemsLabel || 'ITEMS'}
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {stat.items?.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '10px',
                    borderLeft: `3px solid ${item.typeColor || stat.color}`,
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                      <span style={{ fontWeight: '600', fontSize: '14px' }}>{item.name}</span>
                      {item.badge && (
                        <span style={{
                          padding: '2px 8px',
                          background: `${item.typeColor || stat.color}20`,
                          color: item.typeColor || stat.color,
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: '600',
                        }}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
                      {item.description}
                    </p>
                    {item.details && (
                      <div style={{ display: 'flex', gap: '12px', marginTop: '8px', flexWrap: 'wrap' }}>
                        {item.details.map((d, j) => (
                          <span key={j} style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                            {d.icon && <span style={{ marginRight: '4px' }}>{d.icon}</span>}
                            {d.label}: <strong>{d.value}</strong>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  {item.path && (
                    <button
                      onClick={() => openInEditor(item.path)}
                      style={{
                        background: 'transparent',
                        border: '1px solid var(--border-color)',
                        borderRadius: '6px',
                        padding: '6px 10px',
                        cursor: 'pointer',
                        color: 'var(--text-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '11px',
                        transition: 'all 0.2s',
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = stat.color;
                        e.target.style.color = 'white';
                        e.target.style.borderColor = stat.color;
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'transparent';
                        e.target.style.color = 'var(--text-secondary)';
                        e.target.style.borderColor = 'var(--border-color)';
                      }}
                    >
                      <ExternalLink size={12} />
                      Open
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [userName, setUserName] = useState('');
  const [userRole, setUserRole] = useState('');
  const [activeView, setActiveView] = useState('architecture');
  const [selectedStat, setSelectedStat] = useState(null);

  // Check for existing authentication on mount
  useEffect(() => {
    const authData = localStorage.getItem('jarvis_auth');
    if (authData) {
      const parsed = JSON.parse(authData);
      if (parsed.expires && parsed.expires > Date.now()) {
        setIsAuthenticated(true);
        setUserEmail(parsed.email);
        setUserName(parsed.name || '');
        setUserRole(parsed.role || '');
      } else {
        localStorage.removeItem('jarvis_auth');
      }
    }
  }, []);

  const handleAuthenticated = () => {
    const authData = JSON.parse(localStorage.getItem('jarvis_auth') || '{}');
    setIsAuthenticated(true);
    setUserEmail(authData.email);
    setUserName(authData.name || '');
    setUserRole(authData.role || '');
  };

  const handleLogout = () => {
    localStorage.removeItem('jarvis_auth');
    setIsAuthenticated(false);
    setUserEmail('');
    setUserName('');
    setUserRole('');
    setActiveView('architecture');
  };

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <CloudflareAuth onAuthenticated={handleAuthenticated} />;
  }

  const navItems = [
    { id: 'architecture', name: 'Architecture', icon: Network, description: 'System Architecture Diagram' },
    { id: 'modules', name: 'Module Explorer', icon: FolderTree, description: 'Browse Code Files' },
    { id: 'workflows', name: 'Workflows', icon: Workflow, description: 'Data Flow Pipelines' },
    { id: 'monitor', name: 'System Monitor', icon: Activity, description: 'Real-time Status' },
    { id: 'security', name: 'Security', icon: Shield, description: 'Authentication & Access Control' },
  ];

  // Calculate total lines of code
  const allModules = getAllModules();
  const totalLines = allModules.reduce((acc, m) => acc + (m.lines || 0), 0);

  // Prepare stats data with comprehensive information
  const statsData = {
    pythonFiles: {
      icon: FileCode,
      title: '27 Python Files',
      subtitle: 'Core codebase files',
      color: '#22c55e',
      description: 'The Finance-X terminal is built with 27 Python files organized into core application, engines, support modules, and extensions. The codebase follows a modular architecture for maintainability and scalability.',
      summaryStats: [
        { value: totalLines.toLocaleString(), label: 'Total Lines' },
        { value: '4', label: 'Core Files' },
        { value: '5', label: 'Engines' },
        { value: '4', label: 'Support' },
        { value: '5', label: 'Extensions' },
      ],
      itemsLabel: 'ALL PYTHON FILES',
      items: [
        ...modules.core.map(m => ({
          name: m.name,
          description: m.description,
          badge: 'CORE',
          typeColor: '#3b82f6',
          path: m.path,
          details: m.lines ? [{ label: 'Lines', value: m.lines }] : [],
        })),
        ...modules.engines.map(m => ({
          name: m.name,
          description: m.description,
          badge: 'ENGINE',
          typeColor: '#22c55e',
          path: m.path,
          details: [
            { label: 'Lines', value: m.lines },
            ...(m.classes ? [{ label: 'Classes', value: m.classes.length }] : []),
          ],
        })),
        ...modules.support.map(m => ({
          name: m.name,
          description: m.description,
          badge: 'SUPPORT',
          typeColor: '#f97316',
          path: m.path,
          details: m.lines ? [{ label: 'Lines', value: m.lines }] : [],
        })),
        ...modules.extensions.map(m => ({
          name: m.name,
          description: m.description,
          badge: 'EXTENSION',
          typeColor: '#a855f7',
          path: m.path,
          details: m.lines ? [{ label: 'Lines', value: m.lines }] : [],
        })),
      ],
    },
    coreEngines: {
      icon: Cpu,
      title: '5 Core Engines',
      subtitle: 'Intelligence & processing modules',
      color: '#3b82f6',
      description: 'The five core engines power all market analysis, data processing, and intelligence features. Each engine is specialized for specific tasks like risk detection, market data fetching, Bloomberg features, news analysis, and performance optimization.',
      summaryStats: [
        { value: '5', label: 'Total Engines' },
        { value: modules.engines.reduce((a, m) => a + (m.lines || 0), 0).toLocaleString(), label: 'Lines of Code' },
        { value: modules.engines.reduce((a, m) => a + (m.classes?.length || 0), 0), label: 'Classes' },
        { value: modules.engines.reduce((a, m) => a + (m.functions?.length || 0), 0), label: 'Functions' },
      ],
      itemsLabel: 'ENGINE BREAKDOWN',
      items: modules.engines.map(m => ({
        name: m.name,
        description: m.purpose || m.description,
        badge: m.layer || 'ENGINE',
        typeColor: '#22c55e',
        path: m.path,
        details: [
          { label: 'Lines', value: m.lines },
          { label: 'Classes', value: m.classes?.length || 0 },
          { label: 'Functions', value: m.functions?.length || 0 },
        ],
      })),
    },
    databases: {
      icon: Database,
      title: '2 Databases',
      subtitle: 'SQLite data storage',
      color: '#06b6d4',
      description: 'Finance-X uses two SQLite databases for persistent storage. finance.db stores market data, events, and system states, while users.db manages user portfolios and positions for disruption monitoring.',
      summaryStats: [
        { value: '2', label: 'Databases' },
        { value: '~3 MB', label: 'Total Size' },
        { value: '4+', label: 'Tables' },
        { value: 'SQLite', label: 'Engine' },
      ],
      itemsLabel: 'DATABASE FILES',
      items: [
        {
          name: 'finance.db',
          description: 'Primary database for market data, event history, price history, and system state snapshots',
          badge: '2.9 MB',
          typeColor: '#06b6d4',
          path: '/Users/aayush/Finance-X-/finance.db',
          details: [
            { label: 'Tables', value: 'events, system_states, price_history' },
          ],
        },
        {
          name: 'users.db',
          description: 'User data storage for portfolio positions, watchlists, and preferences',
          badge: '16 KB',
          typeColor: '#06b6d4',
          path: '/Users/aayush/Finance-X-/users.db',
          details: [
            { label: 'Tables', value: 'positions' },
          ],
        },
      ],
    },
    extensions: {
      icon: Puzzle,
      title: '5 Extensions',
      subtitle: 'Modular plugin system',
      color: '#a855f7',
      description: 'The extension system provides modular integrations and add-on functionality. Extensions can hook into the core engine, provide custom commands, integrate external APIs, and add specialized features.',
      summaryStats: [
        { value: '5', label: 'Extensions' },
        { value: modules.extensions.reduce((a, m) => a + (m.lines || 0), 0), label: 'Lines of Code' },
        { value: '3', label: 'API Integrations' },
        { value: '2', label: 'System Utils' },
      ],
      itemsLabel: 'AVAILABLE EXTENSIONS',
      items: modules.extensions.map(m => ({
        name: m.name,
        description: m.purpose || m.description,
        badge: m.layer || 'EXTENSION',
        typeColor: '#a855f7',
        path: m.path,
        details: m.lines ? [{ label: 'Lines', value: m.lines }] : [],
      })),
    },
  };

  const renderView = () => {
    switch (activeView) {
      case 'architecture':
        return <ArchitectureDiagram />;
      case 'modules':
        return <ModuleExplorer />;
      case 'workflows':
        return <WorkflowVisualizer />;
      case 'monitor':
        return <ExecutionMonitor />;
      case 'security':
        return <SecurityDashboard userEmail={userEmail} onLogout={handleLogout} />;
      default:
        return <ArchitectureDiagram />;
    }
  };

  const activeItem = navItems.find(item => item.id === activeView);

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">J</div>
          <div className="sidebar-title">
            <h1>JARVIS</h1>
            <span>Architecture Visualizer</span>
          </div>
        </div>

        {/* User Info */}
        <div style={{
          margin: '0 12px 16px',
          padding: '12px',
          background: userRole === 'Founder' ? 'rgba(246,130,31,0.1)' : 'rgba(34,197,94,0.1)',
          borderRadius: '8px',
          border: `1px solid ${userRole === 'Founder' ? 'rgba(246,130,31,0.3)' : 'rgba(34,197,94,0.2)'}`,
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: userRole === 'Founder'
              ? 'linear-gradient(135deg, #f6821f, #fbad41)'
              : 'linear-gradient(135deg, #22c55e, #10b981)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: '700',
            fontSize: '14px',
            boxShadow: userRole === 'Founder' ? '0 0 12px rgba(246,130,31,0.4)' : 'none',
          }}>
            {userName ? userName.charAt(0).toUpperCase() : userEmail.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>
                {userName || 'Team Member'}
              </span>
              {userRole === 'Founder' && (
                <span style={{
                  padding: '2px 6px',
                  background: 'linear-gradient(135deg, #f6821f, #fbad41)',
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '9px',
                  fontWeight: '700',
                  letterSpacing: '0.5px',
                }}>FOUNDER</span>
              )}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {userEmail}
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-title">Navigation</div>
            {navItems.map(item => (
              <div
                key={item.id}
                className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                onClick={() => setActiveView(item.id)}
              >
                <item.icon />
                <span>{item.name}</span>
              </div>
            ))}
          </div>

          <div className="nav-section">
            <div className="nav-section-title">Quick Stats</div>

            {/* Python Files */}
            <motion.div
              className="nav-item stat-item"
              onClick={() => setSelectedStat(statsData.pythonFiles)}
              whileHover={{ x: 4 }}
              style={{ cursor: 'pointer' }}
            >
              <FileCode style={{ color: '#22c55e' }} />
              <span>27 Python Files</span>
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </motion.div>

            {/* Core Engines */}
            <motion.div
              className="nav-item stat-item"
              onClick={() => setSelectedStat(statsData.coreEngines)}
              whileHover={{ x: 4 }}
              style={{ cursor: 'pointer' }}
            >
              <Cpu style={{ color: '#3b82f6' }} />
              <span>5 Core Engines</span>
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </motion.div>

            {/* Databases */}
            <motion.div
              className="nav-item stat-item"
              onClick={() => setSelectedStat(statsData.databases)}
              whileHover={{ x: 4 }}
              style={{ cursor: 'pointer' }}
            >
              <Database style={{ color: '#06b6d4' }} />
              <span>2 Databases</span>
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </motion.div>

            {/* Extensions */}
            <motion.div
              className="nav-item stat-item"
              onClick={() => setSelectedStat(statsData.extensions)}
              whileHover={{ x: 4 }}
              style={{ cursor: 'pointer' }}
            >
              <Puzzle style={{ color: '#a855f7' }} />
              <span>5 Extensions</span>
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </motion.div>
          </div>

          {/* Total Lines of Code */}
          <div style={{
            margin: '16px 12px',
            padding: '16px',
            background: 'linear-gradient(135deg, rgba(34,197,94,0.1), rgba(59,130,246,0.1))',
            borderRadius: '12px',
            border: '1px solid var(--border-color)',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '28px', fontWeight: '700', background: 'linear-gradient(135deg, #22c55e, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {totalLines.toLocaleString()}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Total Lines of Code</div>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="content-header">
          <h2>{activeItem?.name}</h2>
          <p>{activeItem?.description}</p>
        </header>

        <div className="content-body">
          {renderView()}
        </div>
      </main>

      {/* Stats Detail Modal */}
      <AnimatePresence>
        {selectedStat && (
          <StatsDetailModal stat={selectedStat} onClose={() => setSelectedStat(null)} />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
