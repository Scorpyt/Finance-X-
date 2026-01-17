import { useCallback, useMemo, useState, useRef } from 'react';
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    Handle,
    Position,
    MarkerType,
    getBezierPath,
    EdgeLabelRenderer,
    useReactFlow,
    ReactFlowProvider,
} from 'reactflow';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ExternalLink,
    X,
    FileCode,
    Layers,
    GitBranch,
    Database,
    Server,
    Cpu,
    ArrowRight,
    ArrowLeft,
    Globe,
    Zap,
    Copy,
    Check,
    ChevronDown,
    ChevronUp,
    Box,
    Activity,
    Link2,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Play,
    Code,
    Terminal,
    Shuffle,
    RefreshCw,
    Info
} from 'lucide-react';
import { modules, getModuleById, getAllModules } from '../data/architecture';
import NodeDetailsPanel from './NodeDetailsPanel';
import 'reactflow/dist/style.css';

// ==================== VIRTUAL IDE SIMULATION ENGINE ====================

const simulationKnowledge = {
    // Module compatibility matrix - defines what happens when connections change
    dependencies: {
        'server': {
            requires: ['engine', 'india_engine', 'bloomberg_engine', 'study_engine', 'analyst', 'user_data'],
            provides: ['HTTP API', 'WebSocket', 'Command routing'],
            critical: true,
        },
        'engine': {
            requires: ['models', 'database', 'performance_engine'],
            provides: ['Market analysis', 'AI predictions', 'Portfolio evaluation'],
            critical: true,
        },
        'india_engine': {
            requires: ['yfinance'],
            provides: ['NSE data', 'NIFTY 50', 'Indian market analysis'],
            critical: false,
        },
        'bloomberg_engine': {
            requires: ['yfinance'],
            provides: ['FX rates', 'Sector analysis', 'Stock screener', 'Top movers'],
            critical: false,
        },
        'study_engine': {
            requires: ['rss'],
            provides: ['News analysis', 'Educational content'],
            critical: false,
        },
        'database': {
            requires: ['findb', 'userdb'],
            provides: ['Data persistence', 'Query interface'],
            critical: true,
        },
        'user_data': {
            requires: ['userdb'],
            provides: ['Portfolio storage', 'User preferences'],
            critical: false,
        },
        'bloomberg_api': {
            requires: ['bloomberg_engine'],
            provides: ['Bloomberg microservice API'],
            critical: false,
        },
        'client': {
            requires: ['server', 'bloomberg_api'],
            provides: ['User interface'],
            critical: true,
        },
    },

    // Simulate what happens when a connection is changed
    simulateConnectionChange: (sourceId, oldTargetId, newTargetId) => {
        const results = {
            status: 'success',
            severity: 'info',
            title: '',
            description: '',
            impacts: [],
            codeChanges: [],
            warnings: [],
            suggestions: [],
        };

        // Get source module info
        const sourceInfo = simulationKnowledge.dependencies[sourceId];
        const oldTargetInfo = simulationKnowledge.dependencies[oldTargetId];
        const newTargetInfo = simulationKnowledge.dependencies[newTargetId];

        // Determine compatibility
        if (!newTargetInfo) {
            results.status = 'error';
            results.severity = 'critical';
            results.title = 'Invalid Connection Target';
            results.description = `Cannot connect ${sourceId} to ${newTargetId} - target module not found in dependency graph.`;
            results.impacts.push({
                type: 'error',
                message: 'Application will fail to start',
            });
            return results;
        }

        // Check if this breaks critical dependencies
        if (sourceInfo?.critical && oldTargetInfo?.critical) {
            results.status = 'warning';
            results.severity = 'high';
            results.title = 'Critical Dependency Change';
            results.description = `Changing connection from ${oldTargetId} to ${newTargetId} affects a critical system path.`;
            results.warnings.push('This change may cause system instability');
            results.warnings.push('Existing data flows will be disrupted');
        }

        // Simulate specific connection scenarios
        const connectionKey = `${sourceId}->${newTargetId}`;
        const scenarios = {
            'server->database': {
                status: 'success',
                severity: 'medium',
                title: 'Direct Database Access',
                description: 'Server will bypass engine layer and access database directly.',
                impacts: [
                    { type: 'perf', message: '↑ 15% faster queries (no middleware)' },
                    { type: 'warning', message: '↓ No AI analysis on queries' },
                    { type: 'security', message: '⚠ Raw SQL exposure risk' },
                ],
                codeChanges: [
                    { file: 'server.py', line: 45, change: 'from database import DatabaseManager' },
                    { file: 'server.py', line: 120, change: 'db = DatabaseManager()' },
                    { file: 'engine.py', change: '# Remove server routing (unused)' },
                ],
                suggestions: ['Consider adding input validation', 'Add SQL injection protection'],
            },
            'server->yfinance': {
                status: 'warning',
                severity: 'high',
                title: 'Direct API Access Bypass',
                description: 'Server will call yfinance directly, bypassing all engine processing.',
                impacts: [
                    { type: 'warning', message: 'india_engine will not process data' },
                    { type: 'warning', message: 'bloomberg_engine bypassed' },
                    { type: 'perf', message: '↑ Raw data, no caching' },
                    { type: 'error', message: 'Disruption Mode will not work' },
                ],
                codeChanges: [
                    { file: 'server.py', line: 10, change: 'import yfinance as yf' },
                    { file: 'server.py', line: 85, change: 'data = yf.Ticker(symbol).history()' },
                ],
                warnings: ['Rate limiting not handled', 'No data normalization'],
            },
            'india_engine->database': {
                status: 'success',
                severity: 'low',
                title: 'Local Data Caching',
                description: 'India engine will cache market data locally in database.',
                impacts: [
                    { type: 'perf', message: '↑ 50% faster on repeat queries' },
                    { type: 'storage', message: '↑ Database size will grow' },
                    { type: 'success', message: 'Offline mode possible' },
                ],
                codeChanges: [
                    { file: 'india_engine.py', line: 25, change: 'from database import cache_market_data' },
                    { file: 'india_engine.py', line: 89, change: 'cache_market_data(symbol, data)' },
                ],
                suggestions: ['Add cache expiration (suggest 5min)', 'Add cache invalidation on market close'],
            },
            'bloomberg_engine->rss': {
                status: 'error',
                severity: 'critical',
                title: 'Incompatible Data Sources',
                description: 'Bloomberg engine expects structured market data, not RSS feeds.',
                impacts: [
                    { type: 'error', message: 'TypeError: Cannot parse RSS as market data' },
                    { type: 'error', message: 'FX rates will fail' },
                    { type: 'error', message: 'Sector analysis will crash' },
                ],
                codeChanges: [
                    { file: 'bloomberg_engine.py', line: 45, change: '# ERROR: RSS feed incompatible' },
                ],
                warnings: ['This connection is not viable', 'System will not start'],
            },
            'engine->user_data': {
                status: 'success',
                severity: 'low',
                title: 'Portfolio-Aware Analysis',
                description: 'Engine will have direct access to user portfolios for personalized analysis.',
                impacts: [
                    { type: 'success', message: 'AI can analyze user holdings' },
                    { type: 'success', message: 'Personalized recommendations' },
                    { type: 'perf', message: '↑ Smarter Disruption Mode alerts' },
                ],
                codeChanges: [
                    { file: 'engine.py', line: 15, change: 'from user_data import get_portfolio' },
                    { file: 'engine.py', line: 178, change: 'portfolio = get_portfolio(user_id)' },
                ],
                suggestions: ['Great enhancement!', 'Consider privacy implications'],
            },
            'study_engine->yfinance': {
                status: 'success',
                severity: 'medium',
                title: 'Market-Aware News',
                description: 'Study engine can correlate news with real-time market data.',
                impacts: [
                    { type: 'success', message: 'News sentiment + price correlation' },
                    { type: 'success', message: 'Event-driven insights' },
                    { type: 'perf', message: '↑ 30% more relevant news' },
                ],
                codeChanges: [
                    { file: 'study_engine.py', line: 8, change: 'import yfinance as yf' },
                    { file: 'study_engine.py', line: 145, change: 'price_impact = yf.Ticker(symbol).info' },
                ],
            },
            'analyst->engine': {
                status: 'warning',
                severity: 'medium',
                title: 'Circular Dependency Warning',
                description: 'Analyst connecting to engine may create circular dependency.',
                impacts: [
                    { type: 'warning', message: 'Potential infinite loop' },
                    { type: 'warning', message: 'Stack overflow risk' },
                    { type: 'perf', message: '↓ Memory usage will spike' },
                ],
                codeChanges: [
                    { file: 'analyst.py', line: 5, change: 'from engine import analyze  # Circular!' },
                ],
                warnings: ['Break the cycle with lazy imports', 'Consider event-based communication'],
            },
            'client->engine': {
                status: 'error',
                severity: 'critical',
                title: 'Architecture Violation',
                description: 'Client should never directly access engine - must go through server API.',
                impacts: [
                    { type: 'error', message: 'CORS will block this in browser' },
                    { type: 'security', message: 'Exposes internal logic' },
                    { type: 'error', message: 'No authentication layer' },
                ],
                warnings: ['This breaks the API gateway pattern', 'Security vulnerability'],
            },
        };

        // Check if we have a specific scenario
        if (scenarios[connectionKey]) {
            return { ...results, ...scenarios[connectionKey] };
        }

        // Default generic simulation
        results.title = 'Connection Analysis';
        results.description = `Analyzing impact of connecting ${sourceId} to ${newTargetId}`;
        results.impacts.push({
            type: 'info',
            message: `${sourceId} will now depend on ${newTargetId}`,
        });
        results.codeChanges.push({
            file: `${sourceId}.py`,
            change: `from ${newTargetId} import *`,
        });

        return results;
    },
};

// ==================== CUSTOM INTERACTIVE EDGE ====================

const CustomEdge = ({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    source,
    target,
    style = {},
    markerEnd,
    data,
}) => {
    const [isHovered, setIsHovered] = useState(false);

    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });

    const edgeColor = isHovered ? '#f6821f' : (style.stroke || '#64748b');

    return (
        <>
            {/* Invisible wider path for easier interaction */}
            <path
                d={edgePath}
                fill="none"
                stroke="transparent"
                strokeWidth={20}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                onClick={() => data?.onEdgeClick?.(id, source, target)}
                style={{ cursor: 'pointer' }}
            />
            {/* Visible edge */}
            <path
                id={id}
                d={edgePath}
                fill="none"
                stroke={edgeColor}
                strokeWidth={isHovered ? 3 : 2}
                markerEnd={markerEnd}
                style={{
                    transition: 'all 0.2s',
                    filter: isHovered ? 'drop-shadow(0 0 8px ' + edgeColor + ')' : 'none',
                }}
            />
            {/* Edge Label on Hover */}
            {isHovered && (
                <EdgeLabelRenderer>
                    <div
                        style={{
                            position: 'absolute',
                            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                            pointerEvents: 'all',
                        }}
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(17,17,24,0.95)',
                                borderRadius: '6px',
                                border: '1px solid #f6821f',
                                fontSize: '11px',
                                color: 'white',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                whiteSpace: 'nowrap',
                            }}
                        >
                            <Shuffle size={12} color="#f6821f" />
                            Click to simulate change
                        </motion.div>
                    </div>
                </EdgeLabelRenderer>
            )}
        </>
    );
};

// ==================== CUSTOM NODE COMPONENT ====================

const CustomNode = ({ data, selected }) => {
    return (
        <motion.div
            className={`custom-node ${data.type}`}
            onClick={() => data.onSelect(data)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            style={{
                boxShadow: selected ? '0 0 20px rgba(59, 130, 246, 0.5)' : 'none',
                border: selected ? '2px solid #3b82f6' : '1px solid var(--border-color)',
            }}
        >
            <Handle type="target" position={Position.Top} style={{ background: '#3b82f6' }} />
            <div className="node-title">{data.label}</div>
            <div className="node-subtitle">{data.subtitle}</div>
            <Handle type="source" position={Position.Bottom} style={{ background: '#22c55e' }} />
        </motion.div>
    );
};

const nodeTypes = { custom: CustomNode };
const edgeTypes = { custom: CustomEdge };

// ==================== NODES AND EDGES SETUP ====================

const createNodes = (onSelect) => [
    { id: 'client', position: { x: 400, y: 0 }, data: { label: 'Terminal UI', subtitle: 'index.html + terminal.js', type: 'frontend', moduleId: 'index_html', onSelect }, type: 'custom' },
    { id: 'server', position: { x: 250, y: 120 }, data: { label: 'server.py', subtitle: 'FastAPI Application', type: 'core', moduleId: 'server', onSelect }, type: 'custom' },
    { id: 'bloomberg_api', position: { x: 550, y: 120 }, data: { label: 'bloomberg_service.py', subtitle: 'Microservice API', type: 'core', moduleId: 'bloomberg_service', onSelect }, type: 'custom' },
    { id: 'engine', position: { x: 50, y: 260 }, data: { label: 'engine.py', subtitle: 'Intelligence Engine', type: 'engine', moduleId: 'engine', onSelect }, type: 'custom' },
    { id: 'india', position: { x: 220, y: 260 }, data: { label: 'india_engine.py', subtitle: 'NSE Market Engine', type: 'engine', moduleId: 'india_engine', onSelect }, type: 'custom' },
    { id: 'bloomberg', position: { x: 390, y: 260 }, data: { label: 'bloomberg_engine.py', subtitle: 'Bloomberg Features', type: 'engine', moduleId: 'bloomberg_engine', onSelect }, type: 'custom' },
    { id: 'study', position: { x: 560, y: 260 }, data: { label: 'study_engine.py', subtitle: 'News & Learning', type: 'engine', moduleId: 'study_engine', onSelect }, type: 'custom' },
    { id: 'perf', position: { x: 730, y: 260 }, data: { label: 'performance_engine.py', subtitle: 'Hardware Optimizer', type: 'engine', moduleId: 'performance_engine', onSelect }, type: 'custom' },
    { id: 'analyst', position: { x: 50, y: 400 }, data: { label: 'analyst.py', subtitle: 'Event Analysis', type: 'support', moduleId: 'analyst', onSelect }, type: 'custom' },
    { id: 'models', position: { x: 220, y: 400 }, data: { label: 'models.py', subtitle: 'Data Models', type: 'support', moduleId: 'models', onSelect }, type: 'custom' },
    { id: 'database', position: { x: 390, y: 400 }, data: { label: 'database.py', subtitle: 'SQLite Manager', type: 'support', moduleId: 'database', onSelect }, type: 'custom' },
    { id: 'user_data', position: { x: 560, y: 400 }, data: { label: 'user_data.py', subtitle: 'Portfolio Manager', type: 'support', moduleId: 'user_data', onSelect }, type: 'custom' },
    { id: 'findb', position: { x: 320, y: 520 }, data: { label: 'finance.db', subtitle: 'Market Data Storage', type: 'data', moduleId: 'finance_db', onSelect }, type: 'custom' },
    { id: 'userdb', position: { x: 500, y: 520 }, data: { label: 'users.db', subtitle: 'User Data Storage', type: 'data', moduleId: 'users_db', onSelect }, type: 'custom' },
    { id: 'yfinance', position: { x: 220, y: 640 }, data: { label: 'yfinance API', subtitle: 'Market Data', type: 'extension', onSelect }, type: 'custom' },
    { id: 'rss', position: { x: 560, y: 640 }, data: { label: 'RSS Feeds', subtitle: 'News Data', type: 'extension', onSelect }, type: 'custom' },
];

const createEdges = (onEdgeClick) => [
    { id: 'e1', source: 'client', target: 'server', type: 'custom', animated: true, style: { stroke: '#3b82f6' }, data: { onEdgeClick } },
    { id: 'e2', source: 'client', target: 'bloomberg_api', type: 'custom', animated: true, style: { stroke: '#3b82f6' }, data: { onEdgeClick } },
    { id: 'e3', source: 'server', target: 'engine', type: 'custom', style: { stroke: '#22c55e' }, data: { onEdgeClick } },
    { id: 'e4', source: 'server', target: 'india', type: 'custom', style: { stroke: '#22c55e' }, data: { onEdgeClick } },
    { id: 'e5', source: 'server', target: 'bloomberg', type: 'custom', style: { stroke: '#22c55e' }, data: { onEdgeClick } },
    { id: 'e6', source: 'server', target: 'study', type: 'custom', style: { stroke: '#22c55e' }, data: { onEdgeClick } },
    { id: 'e7', source: 'server', target: 'analyst', type: 'custom', style: { stroke: '#f97316' }, data: { onEdgeClick } },
    { id: 'e8', source: 'server', target: 'user_data', type: 'custom', style: { stroke: '#f97316' }, data: { onEdgeClick } },
    { id: 'e9', source: 'bloomberg_api', target: 'bloomberg', type: 'custom', style: { stroke: '#22c55e' }, data: { onEdgeClick } },
    { id: 'e10', source: 'engine', target: 'models', type: 'custom', style: { stroke: '#f97316' }, data: { onEdgeClick } },
    { id: 'e11', source: 'engine', target: 'database', type: 'custom', style: { stroke: '#f97316' }, data: { onEdgeClick } },
    { id: 'e12', source: 'engine', target: 'perf', type: 'custom', style: { stroke: '#22c55e' }, data: { onEdgeClick } },
    { id: 'e13', source: 'india', target: 'yfinance', type: 'custom', style: { stroke: '#a855f7' }, data: { onEdgeClick } },
    { id: 'e14', source: 'bloomberg', target: 'yfinance', type: 'custom', style: { stroke: '#a855f7' }, data: { onEdgeClick } },
    { id: 'e15', source: 'study', target: 'rss', type: 'custom', style: { stroke: '#a855f7' }, data: { onEdgeClick } },
    { id: 'e16', source: 'database', target: 'findb', type: 'custom', style: { stroke: '#06b6d4' }, data: { onEdgeClick } },
    { id: 'e17', source: 'database', target: 'userdb', type: 'custom', style: { stroke: '#06b6d4' }, data: { onEdgeClick } },
    { id: 'e18', source: 'user_data', target: 'userdb', type: 'custom', style: { stroke: '#06b6d4' }, data: { onEdgeClick } },
];

// ==================== HELPER FUNCTIONS ====================

const getTypeColor = (type) => {
    switch (type) {
        case 'core': return '#3b82f6';
        case 'engine': return '#22c55e';
        case 'support': return '#f97316';
        case 'extension': return '#a855f7';
        case 'data': return '#06b6d4';
        case 'frontend': return '#ec4899';
        default: return '#64748b';
    }
};

const InfoSection = ({ title, icon: Icon, children, defaultOpen = true }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    return (
        <div style={{ marginBottom: '16px' }}>
            <div onClick={() => setIsOpen(!isOpen)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', padding: '8px 0', borderBottom: '1px solid var(--border-color)', marginBottom: isOpen ? '12px' : 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '12px', fontWeight: '600' }}>
                    <Icon size={14} />
                    <span>{title}</span>
                </div>
                {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </div>
            <AnimatePresence>
                {isOpen && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}>
                        {children}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const Tag = ({ children, color = 'var(--accent-blue)' }) => (
    <span style={{ display: 'inline-block', padding: '4px 10px', background: `${color}20`, color: color, borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace', marginRight: '6px', marginBottom: '6px' }}>
        {children}
    </span>
);

// ==================== SIMULATION PANEL COMPONENT ====================

const SimulationPanel = ({ simulation, sourceNode, targetNode, onClose, onApply, allNodes }) => {
    const [selectedNewTarget, setSelectedNewTarget] = useState(null);
    const [simulationResult, setSimulationResult] = useState(null);

    const availableTargets = allNodes.filter(n => n.id !== sourceNode && n.id !== targetNode);

    const runSimulation = (newTargetId) => {
        setSelectedNewTarget(newTargetId);
        const result = simulationKnowledge.simulateConnectionChange(sourceNode, targetNode, newTargetId);
        setSimulationResult(result);
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical': return '#ef4444';
            case 'high': return '#f97316';
            case 'medium': return '#f59e0b';
            case 'low': return '#22c55e';
            default: return '#3b82f6';
        }
    };

    const getImpactIcon = (type) => {
        switch (type) {
            case 'error': return <XCircle size={14} color="#ef4444" />;
            case 'warning': return <AlertTriangle size={14} color="#f97316" />;
            case 'success': return <CheckCircle size={14} color="#22c55e" />;
            case 'perf': return <Zap size={14} color="#3b82f6" />;
            case 'security': return <AlertTriangle size={14} color="#f59e0b" />;
            default: return <Info size={14} color="#64748b" />;
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            style={{
                width: '420px',
                maxHeight: 'calc(100vh - 140px)',
                background: 'var(--bg-secondary)',
                borderRadius: '16px',
                border: '1px solid var(--border-color)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
            }}
        >
            {/* Header */}
            <div style={{
                padding: '20px',
                background: 'linear-gradient(135deg, rgba(246,130,31,0.15), rgba(246,130,31,0.05))',
                borderBottom: '1px solid rgba(246,130,31,0.3)',
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div>
                        <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <Terminal size={20} style={{ color: '#f6821f' }} />
                            Virtual IDE Simulation
                        </h3>
                        <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
                            Simulate what happens if you change this connection
                        </p>
                    </div>
                    <button onClick={onClose} style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', borderRadius: '8px', cursor: 'pointer', color: 'var(--text-muted)', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <X size={16} />
                    </button>
                </div>

                {/* Current Connection */}
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '12px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '8px',
                }}>
                    <span style={{ padding: '4px 10px', background: 'rgba(59,130,246,0.2)', color: '#3b82f6', borderRadius: '4px', fontSize: '12px', fontWeight: '600' }}>
                        {sourceNode}
                    </span>
                    <ArrowRight size={16} color="var(--text-muted)" />
                    <span style={{ padding: '4px 10px', background: 'rgba(34,197,94,0.2)', color: '#22c55e', borderRadius: '4px', fontSize: '12px', fontWeight: '600' }}>
                        {targetNode}
                    </span>
                </div>
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
                {/* Target Selection */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', display: 'block', marginBottom: '8px' }}>
                        SELECT NEW TARGET
                    </label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {availableTargets.map(node => (
                            <button
                                key={node.id}
                                onClick={() => runSimulation(node.id)}
                                style={{
                                    padding: '6px 12px',
                                    background: selectedNewTarget === node.id ? '#f6821f' : 'var(--bg-tertiary)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: '6px',
                                    color: selectedNewTarget === node.id ? 'white' : 'var(--text-secondary)',
                                    fontSize: '11px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                }}
                            >
                                {node.id}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Simulation Result */}
                <AnimatePresence>
                    {simulationResult && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                        >
                            {/* Status Badge */}
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                padding: '12px',
                                background: `${getSeverityColor(simulationResult.severity)}15`,
                                border: `1px solid ${getSeverityColor(simulationResult.severity)}40`,
                                borderRadius: '8px',
                                marginBottom: '16px',
                            }}>
                                {simulationResult.status === 'error' ? <XCircle size={20} color={getSeverityColor(simulationResult.severity)} /> :
                                    simulationResult.status === 'warning' ? <AlertTriangle size={20} color={getSeverityColor(simulationResult.severity)} /> :
                                        <CheckCircle size={20} color={getSeverityColor(simulationResult.severity)} />}
                                <div>
                                    <div style={{ fontWeight: '600', fontSize: '14px', color: getSeverityColor(simulationResult.severity) }}>
                                        {simulationResult.title}
                                    </div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                        {simulationResult.description}
                                    </div>
                                </div>
                            </div>

                            {/* Impacts */}
                            {simulationResult.impacts?.length > 0 && (
                                <InfoSection title="IMPACT ANALYSIS" icon={Activity} defaultOpen={true}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        {simulationResult.impacts.map((impact, i) => (
                                            <div key={i} style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '10px',
                                                padding: '8px 12px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '6px',
                                                fontSize: '12px',
                                            }}>
                                                {getImpactIcon(impact.type)}
                                                <span style={{ color: 'var(--text-secondary)' }}>{impact.message}</span>
                                            </div>
                                        ))}
                                    </div>
                                </InfoSection>
                            )}

                            {/* Code Changes */}
                            {simulationResult.codeChanges?.length > 0 && (
                                <InfoSection title="REQUIRED CODE CHANGES" icon={Code} defaultOpen={true}>
                                    <div style={{
                                        background: '#0d1117',
                                        borderRadius: '8px',
                                        padding: '12px',
                                        fontFamily: 'ui-monospace, monospace',
                                        fontSize: '11px',
                                    }}>
                                        {simulationResult.codeChanges.map((change, i) => (
                                            <div key={i} style={{ marginBottom: i < simulationResult.codeChanges.length - 1 ? '8px' : 0 }}>
                                                <div style={{ color: '#8b949e' }}>
                                                    {change.file}{change.line ? `:${change.line}` : ''}
                                                </div>
                                                <div style={{ color: '#22c55e', marginTop: '2px' }}>
                                                    + {change.change}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </InfoSection>
                            )}

                            {/* Warnings */}
                            {simulationResult.warnings?.length > 0 && (
                                <InfoSection title="WARNINGS" icon={AlertTriangle} defaultOpen={true}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                        {simulationResult.warnings.map((warning, i) => (
                                            <div key={i} style={{
                                                padding: '8px 12px',
                                                background: 'rgba(239,68,68,0.1)',
                                                border: '1px solid rgba(239,68,68,0.2)',
                                                borderRadius: '6px',
                                                fontSize: '12px',
                                                color: '#ef4444',
                                            }}>
                                                ⚠️ {warning}
                                            </div>
                                        ))}
                                    </div>
                                </InfoSection>
                            )}

                            {/* Suggestions */}
                            {simulationResult.suggestions?.length > 0 && (
                                <InfoSection title="SUGGESTIONS" icon={CheckCircle} defaultOpen={true}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                        {simulationResult.suggestions.map((suggestion, i) => (
                                            <div key={i} style={{
                                                padding: '8px 12px',
                                                background: 'rgba(34,197,94,0.1)',
                                                borderRadius: '6px',
                                                fontSize: '12px',
                                                color: '#22c55e',
                                            }}>
                                                💡 {suggestion}
                                            </div>
                                        ))}
                                    </div>
                                </InfoSection>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>

                {!simulationResult && (
                    <div style={{
                        textAlign: 'center',
                        padding: '40px 20px',
                        color: 'var(--text-muted)',
                    }}>
                        <Shuffle size={40} style={{ marginBottom: '12px', opacity: 0.5 }} />
                        <p style={{ margin: 0, fontSize: '13px' }}>
                            Select a new target above to simulate the impact of changing this connection
                        </p>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div style={{
                padding: '16px 20px',
                borderTop: '1px solid var(--border-color)',
                background: 'var(--bg-tertiary)',
                display: 'flex',
                gap: '12px',
            }}>
                <button
                    onClick={onClose}
                    style={{
                        flex: 1,
                        padding: '10px',
                        background: 'transparent',
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px',
                        color: 'var(--text-secondary)',
                        fontSize: '13px',
                        cursor: 'pointer',
                    }}
                >
                    Cancel
                </button>
                <button
                    onClick={() => simulationResult && simulationResult.status !== 'error' && onApply(selectedNewTarget)}
                    disabled={!simulationResult || simulationResult.status === 'error'}
                    style={{
                        flex: 1,
                        padding: '10px',
                        background: simulationResult && simulationResult.status !== 'error' ? '#f6821f' : 'var(--bg-tertiary)',
                        border: 'none',
                        borderRadius: '8px',
                        color: simulationResult && simulationResult.status !== 'error' ? 'white' : 'var(--text-muted)',
                        fontSize: '13px',
                        fontWeight: '600',
                        cursor: simulationResult && simulationResult.status !== 'error' ? 'pointer' : 'not-allowed',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                    }}
                >
                    <Play size={14} />
                    Apply Change
                </button>
            </div>
        </motion.div>
    );
};

// ==================== MAIN COMPONENT ====================

function ArchitectureDiagramInner() {
    const [selectedModule, setSelectedModule] = useState(null);
    const [copied, setCopied] = useState(false);
    const [simulationEdge, setSimulationEdge] = useState(null);

    const handleNodeSelect = useCallback((nodeData) => {
        if (nodeData.moduleId) {
            const module = getModuleById(nodeData.moduleId);
            setSelectedModule(module);
        }
        setSimulationEdge(null);
    }, []);

    const handleEdgeClick = useCallback((edgeId, source, target) => {
        setSelectedModule(null);
        setSimulationEdge({ edgeId, source, target });
    }, []);

    const initialNodes = useMemo(() => createNodes(handleNodeSelect), [handleNodeSelect]);
    const initialEdges = useMemo(() => createEdges(handleEdgeClick), [handleEdgeClick]);

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const applyConnectionChange = useCallback((newTarget) => {
        if (!simulationEdge) return;

        setEdges(eds => eds.map(edge => {
            if (edge.id === simulationEdge.edgeId) {
                return {
                    ...edge,
                    target: newTarget,
                    style: { ...edge.style, stroke: '#f6821f' },
                    animated: true,
                };
            }
            return edge;
        }));
        setSimulationEdge(null);
    }, [simulationEdge, setEdges]);

    const openInEditor = (path) => {
        window.open(`vscode://file${path}`, '_blank');
    };

    const copyPath = () => {
        if (selectedModule?.path) {
            navigator.clipboard.writeText(selectedModule.path);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const typeColor = selectedModule ? getTypeColor(selectedModule.type) : '#3b82f6';

    return (
        <div style={{ display: 'flex', gap: '24px', height: 'calc(100vh - 140px)' }}>
            <div className="architecture-container" style={{ flex: 1 }}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    nodeTypes={nodeTypes}
                    edgeTypes={edgeTypes}
                    fitView
                    attributionPosition="bottom-left"
                >
                    <Controls />
                    <MiniMap
                        style={{ background: '#111118' }}
                        nodeColor={(node) => getTypeColor(node.data.type)}
                    />
                    <Background variant="dots" gap={20} size={1} color="#27272a" />
                </ReactFlow>

                {/* Instructions */}
                {!selectedModule && !simulationEdge && (
                    <div style={{
                        position: 'absolute',
                        top: '20px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        padding: '10px 20px',
                        background: 'rgba(17, 17, 24, 0.9)',
                        borderRadius: '8px',
                        border: '1px solid var(--border-color)',
                        fontSize: '13px',
                        color: 'var(--text-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                    }}>
                        <Activity size={16} style={{ color: 'var(--accent-blue)' }} />
                        Click nodes for info • Hover wires to simulate changes
                    </div>
                )}
            </div>

            {/* Simulation Panel */}
            <AnimatePresence>
                {simulationEdge && (
                    <SimulationPanel
                        sourceNode={simulationEdge.source}
                        targetNode={simulationEdge.target}
                        onClose={() => setSimulationEdge(null)}
                        onApply={applyConnectionChange}
                        allNodes={nodes}
                    />
                )}
            </AnimatePresence>

            {/* Module Info Panel - NEW Interactive Panel */}
            <AnimatePresence>
                {selectedModule && (
                    <NodeDetailsPanel
                        node={selectedModule}
                        onClose={() => setSelectedModule(null)}
                    />
                )}
            </AnimatePresence>
        </div>

    );
}

function ArchitectureDiagram() {
    return (
        <ReactFlowProvider>
            <ArchitectureDiagramInner />
        </ReactFlowProvider>
    );
}

export default ArchitectureDiagram;
