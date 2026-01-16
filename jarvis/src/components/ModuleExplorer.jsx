import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Folder,
    FileCode,
    ChevronRight,
    ChevronDown,
    ExternalLink,
    Database,
    FileJson,
    FileType,
    Copy,
    Check
} from 'lucide-react';
import { modules, getAllModules } from '../data/architecture';

// File tree structure
const fileTree = [
    {
        name: 'Finance-X',
        type: 'folder',
        path: '/Users/aayush/Finance-X-',
        children: [
            {
                name: 'Core Application',
                type: 'folder',
                children: [
                    { name: 'server.py', type: 'python', id: 'server' },
                    { name: 'bloomberg_service.py', type: 'python', id: 'bloomberg_service' },
                    { name: 'main.py', type: 'python', id: 'main' },
                    { name: 'terminal_ui.py', type: 'python', id: 'terminal_ui' },
                ]
            },
            {
                name: 'Intelligence Engines',
                type: 'folder',
                children: [
                    { name: 'engine.py', type: 'python', id: 'engine' },
                    { name: 'india_engine.py', type: 'python', id: 'india_engine' },
                    { name: 'bloomberg_engine.py', type: 'python', id: 'bloomberg_engine' },
                    { name: 'study_engine.py', type: 'python', id: 'study_engine' },
                    { name: 'performance_engine.py', type: 'python', id: 'performance_engine' },
                ]
            },
            {
                name: 'Support Modules',
                type: 'folder',
                children: [
                    { name: 'analyst.py', type: 'python', id: 'analyst' },
                    { name: 'models.py', type: 'python', id: 'models' },
                    { name: 'database.py', type: 'python', id: 'database' },
                    { name: 'user_data.py', type: 'python', id: 'user_data' },
                ]
            },
            {
                name: 'extensions/',
                type: 'folder',
                children: [
                    { name: 'yfinance_data.py', type: 'python', id: 'ext_yfinance' },
                    { name: 'wri_aqueduct.py', type: 'python', id: 'ext_wri' },
                    { name: 'audit.py', type: 'python', id: 'ext_audit' },
                    { name: 'command_handlers.py', type: 'python', id: 'ext_commands' },
                    { name: 'persistence.py', type: 'python', id: 'ext_persistence' },
                ]
            },
            {
                name: 'static/',
                type: 'folder',
                children: [
                    { name: 'index.html', type: 'html', id: 'index_html' },
                    { name: 'terminal.js', type: 'js', id: 'terminal_js' },
                    { name: 'terminal.css', type: 'css', id: 'terminal_css' },
                ]
            },
            {
                name: 'Databases',
                type: 'folder',
                children: [
                    { name: 'finance.db', type: 'db', id: 'finance_db' },
                    { name: 'users.db', type: 'db', id: 'users_db' },
                ]
            },
        ]
    }
];

const FileIcon = ({ type }) => {
    switch (type) {
        case 'python': return <FileCode size={16} style={{ color: '#22c55e' }} />;
        case 'js': return <FileCode size={16} style={{ color: '#f7df1e' }} />;
        case 'html': return <FileType size={16} style={{ color: '#e34c26' }} />;
        case 'css': return <FileType size={16} style={{ color: '#264de4' }} />;
        case 'db': return <Database size={16} style={{ color: '#06b6d4' }} />;
        case 'json': return <FileJson size={16} style={{ color: '#f97316' }} />;
        default: return <FileCode size={16} />;
    }
};

const TreeItem = ({ item, depth = 0, selectedId, onSelect }) => {
    const [isOpen, setIsOpen] = useState(depth < 2);

    if (item.type === 'folder') {
        return (
            <div>
                <div
                    className="file-item folder"
                    style={{ paddingLeft: `${16 + depth * 16}px` }}
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    <Folder size={16} />
                    <span>{item.name}</span>
                </div>
                <AnimatePresence>
                    {isOpen && item.children && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            {item.children.map((child, idx) => (
                                <TreeItem
                                    key={idx}
                                    item={child}
                                    depth={depth + 1}
                                    selectedId={selectedId}
                                    onSelect={onSelect}
                                />
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        );
    }

    return (
        <div
            className={`file-item ${item.type} ${selectedId === item.id ? 'active' : ''}`}
            style={{ paddingLeft: `${16 + depth * 16}px` }}
            onClick={() => onSelect(item.id)}
        >
            <FileIcon type={item.type} />
            <span>{item.name}</span>
        </div>
    );
};

function ModuleExplorer() {
    const [selectedId, setSelectedId] = useState(null);
    const [copied, setCopied] = useState(false);

    const allModules = getAllModules();
    const selectedModule = allModules.find(m => m.id === selectedId);

    const copyPath = () => {
        if (selectedModule?.path) {
            navigator.clipboard.writeText(selectedModule.path);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const openInEditor = () => {
        if (selectedModule?.path) {
            window.open(`vscode://file${selectedModule.path}`, '_blank');
        }
    };

    return (
        <div className="explorer-layout">
            {/* File Tree */}
            <div className="file-tree">
                <div className="file-tree-header">
                    <Folder size={16} style={{ marginRight: '8px' }} />
                    Project Files
                </div>
                {fileTree.map((item, idx) => (
                    <TreeItem
                        key={idx}
                        item={item}
                        selectedId={selectedId}
                        onSelect={setSelectedId}
                    />
                ))}
            </div>

            {/* Code Preview */}
            <div className="code-preview">
                {selectedModule ? (
                    <>
                        <div className="code-preview-header">
                            <div className="code-preview-title">
                                <FileIcon type={selectedModule.type === 'data' ? 'db' : 'python'} />
                                {selectedModule.name}
                            </div>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                    onClick={copyPath}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '6px',
                                        padding: '6px 12px',
                                        background: 'var(--bg-tertiary)',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: '6px',
                                        color: 'var(--text-secondary)',
                                        fontSize: '12px',
                                        cursor: 'pointer',
                                    }}
                                >
                                    {copied ? <Check size={14} /> : <Copy size={14} />}
                                    {copied ? 'Copied!' : 'Copy Path'}
                                </button>
                                <button onClick={openInEditor} className="open-in-editor">
                                    <ExternalLink size={14} />
                                    Open in VS Code
                                </button>
                            </div>
                        </div>
                        <div className="code-preview-content">
                            <div style={{ marginBottom: '24px' }}>
                                <h4 style={{ marginBottom: '8px', color: 'var(--text-muted)', fontSize: '12px' }}>DESCRIPTION</h4>
                                <p style={{ lineHeight: '1.6' }}>{selectedModule.description}</p>
                            </div>

                            <div style={{ marginBottom: '24px' }}>
                                <h4 style={{ marginBottom: '8px', color: 'var(--text-muted)', fontSize: '12px' }}>FILE PATH</h4>
                                <code style={{
                                    display: 'block',
                                    padding: '12px',
                                    background: 'var(--bg-tertiary)',
                                    borderRadius: '6px',
                                    fontSize: '13px',
                                    color: 'var(--accent-cyan)',
                                    wordBreak: 'break-all',
                                }}>
                                    {selectedModule.path}
                                </code>
                            </div>

                            {selectedModule.lines && (
                                <div style={{ marginBottom: '24px' }}>
                                    <h4 style={{ marginBottom: '8px', color: 'var(--text-muted)', fontSize: '12px' }}>STATISTICS</h4>
                                    <div style={{ display: 'flex', gap: '16px' }}>
                                        <div style={{
                                            padding: '12px 20px',
                                            background: 'var(--bg-tertiary)',
                                            borderRadius: '8px',
                                            textAlign: 'center',
                                        }}>
                                            <div style={{ fontSize: '24px', fontWeight: '700' }}>{selectedModule.lines}</div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Lines</div>
                                        </div>
                                        {selectedModule.classes && (
                                            <div style={{
                                                padding: '12px 20px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '8px',
                                                textAlign: 'center',
                                            }}>
                                                <div style={{ fontSize: '24px', fontWeight: '700' }}>{selectedModule.classes.length}</div>
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Classes</div>
                                            </div>
                                        )}
                                        {selectedModule.functions && (
                                            <div style={{
                                                padding: '12px 20px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '8px',
                                                textAlign: 'center',
                                            }}>
                                                <div style={{ fontSize: '24px', fontWeight: '700' }}>{selectedModule.functions.length}</div>
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Functions</div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {selectedModule.classes && (
                                <div style={{ marginBottom: '24px' }}>
                                    <h4 style={{ marginBottom: '12px', color: 'var(--text-muted)', fontSize: '12px' }}>CLASSES</h4>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                        {selectedModule.classes.map((cls) => (
                                            <code key={cls} style={{
                                                padding: '8px 14px',
                                                background: 'linear-gradient(135deg, rgba(34,197,94,0.2), rgba(34,197,94,0.1))',
                                                border: '1px solid rgba(34,197,94,0.3)',
                                                borderRadius: '6px',
                                                fontSize: '13px',
                                                color: '#22c55e',
                                            }}>
                                                class {cls}
                                            </code>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedModule.functions && (
                                <div style={{ marginBottom: '24px' }}>
                                    <h4 style={{ marginBottom: '12px', color: 'var(--text-muted)', fontSize: '12px' }}>FUNCTIONS</h4>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                        {selectedModule.functions.map((fn) => (
                                            <code key={fn} style={{
                                                padding: '8px 14px',
                                                background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(59,130,246,0.1))',
                                                border: '1px solid rgba(59,130,246,0.3)',
                                                borderRadius: '6px',
                                                fontSize: '13px',
                                                color: '#3b82f6',
                                            }}>
                                                def {fn}()
                                            </code>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedModule.dependencies && (
                                <div style={{ marginBottom: '24px' }}>
                                    <h4 style={{ marginBottom: '12px', color: 'var(--text-muted)', fontSize: '12px' }}>DEPENDENCIES</h4>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                        {selectedModule.dependencies.map((dep) => (
                                            <span
                                                key={dep}
                                                style={{
                                                    padding: '6px 12px',
                                                    background: 'var(--bg-tertiary)',
                                                    borderRadius: '6px',
                                                    fontSize: '12px',
                                                    cursor: 'pointer',
                                                }}
                                                onClick={() => setSelectedId(dep)}
                                            >
                                                {dep}.py →
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedModule.endpoints && (
                                <div>
                                    <h4 style={{ marginBottom: '12px', color: 'var(--text-muted)', fontSize: '12px' }}>API ENDPOINTS</h4>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        {selectedModule.endpoints.map((endpoint) => (
                                            <code key={endpoint} style={{
                                                padding: '10px 14px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '6px',
                                                fontSize: '13px',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '10px',
                                            }}>
                                                <span style={{
                                                    padding: '2px 8px',
                                                    background: 'rgba(34,197,94,0.2)',
                                                    color: '#22c55e',
                                                    borderRadius: '4px',
                                                    fontSize: '11px',
                                                    fontWeight: '600',
                                                }}>
                                                    {endpoint.includes('status') || endpoint.includes('market') ? 'GET' : 'POST'}
                                                </span>
                                                <span style={{ color: 'var(--accent-cyan)' }}>{endpoint}</span>
                                            </code>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="empty-state">
                        <FileCode size={48} />
                        <h3 style={{ marginBottom: '8px' }}>Select a file</h3>
                        <p>Click on a file in the tree to view its details</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ModuleExplorer;
