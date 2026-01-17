import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X,
    GitBranch,
    Database,
    Server,
    ArrowRight,
    ArrowLeft,
    CheckCircle,
    AlertTriangle,
    Code,
    Box,
    Layers,
    FileText,
    Activity,
    Zap,
    Cpu
} from 'lucide-react';

const NodeDetailsPanel = ({ node, onClose }) => {
    if (!node) return null;

    // Helper to get type color
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

    const color = getTypeColor(node.type);

    return (
        <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            style={{
                width: '450px',
                maxHeight: 'calc(100vh - 140px)',
                background: 'rgba(13, 17, 23, 0.95)',
                backdropFilter: 'blur(10px)',
                borderRadius: '16px',
                border: '1px solid rgba(48, 54, 61, 0.8)',
                boxShadow: '-10px 0 30px rgba(0,0,0,0.5)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                zIndex: 1000,
            }}
        >
            {/* Header */}
            <div style={{
                padding: '20px',
                background: `linear-gradient(135deg, ${color}20, transparent)`,
                borderBottom: '1px solid rgba(48, 54, 61, 0.5)',
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '4px 8px',
                            borderRadius: '6px',
                            background: `${color}30`,
                            color: color,
                            fontSize: '11px',
                            fontWeight: '600',
                            marginBottom: '8px',
                            textTransform: 'uppercase'
                        }}>
                            <Box size={12} />
                            {node.type} MODULE
                        </div>
                        <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '700', color: 'white' }}>
                            {node.name}
                        </h2>
                        <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#8b949e' }}>
                            {node.path}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'rgba(255,255,255,0.05)',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '8px',
                            color: '#8b949e',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        <X size={18} />
                    </button>
                </div>
            </div>

            {/* Scrollable Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>

                {/* Description */}
                <div style={{ marginBottom: '24px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', color: '#c9d1d9' }}>
                        {node.description}
                    </p>
                </div>

                {/* Process Flow Visualization */}
                {node.processFlow && (
                    <div style={{ marginBottom: '24px' }}>
                        <h3 style={{ fontSize: '12px', fontWeight: '600', color: '#8b949e', textTransform: 'uppercase', marginBottom: '16px' }}>
                            Variable & Data Pipeline
                        </h3>

                        <div style={{ position: 'relative', paddingLeft: '16px' }}>
                            {/* Vertical Line */}
                            <div style={{
                                position: 'absolute',
                                left: '7px',
                                top: '10px',
                                bottom: '10px',
                                width: '2px',
                                background: `linear-gradient(to bottom, ${color}40, ${color}10)`
                            }} />

                            {/* Steps */}
                            {node.processFlow.steps.map((step, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '12px',
                                        marginBottom: '12px',
                                    }}
                                >
                                    <div style={{
                                        width: '16px',
                                        height: '16px',
                                        borderRadius: '50%',
                                        background: '#0d1117',
                                        border: `2px solid ${color}`,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '9px',
                                        fontWeight: '700',
                                        color: color,
                                        zIndex: 1
                                    }}>
                                        {index + 1}
                                    </div>
                                    <div style={{
                                        flex: 1,
                                        padding: '10px 14px',
                                        background: 'rgba(255,255,255,0.03)',
                                        border: '1px solid rgba(48, 54, 61, 0.5)',
                                        borderRadius: '8px',
                                        fontSize: '13px',
                                        color: '#e6edf3'
                                    }}>
                                        {step}
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}

                {/* I/O Section */}
                {node.dataFlow && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                        {/* Inputs */}
                        <div style={{
                            background: 'rgba(255,255,255,0.02)',
                            borderRadius: '12px',
                            padding: '16px',
                            border: '1px solid rgba(48, 54, 61, 0.5)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#e6edf3', fontSize: '13px', fontWeight: '600' }}>
                                <ArrowRight size={14} color="#22c55e" />
                                Inputs
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {node.dataFlow.inputs.map((input, i) => (
                                    <div key={i} style={{ fontSize: '12px', color: '#8b949e', padding: '4px 8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                                        {input}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Outputs */}
                        <div style={{
                            background: 'rgba(255,255,255,0.02)',
                            borderRadius: '12px',
                            padding: '16px',
                            border: '1px solid rgba(48, 54, 61, 0.5)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#e6edf3', fontSize: '13px', fontWeight: '600' }}>
                                <ArrowLeft size={14} color="#f97316" style={{ transform: 'rotate(180deg)' }} />
                                Outputs
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {node.dataFlow.outputs.map((output, i) => (
                                    <div key={i} style={{ fontSize: '12px', color: '#8b949e', padding: '4px 8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                                        {output}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Impact Section */}
                {node.processFlow?.impact && (
                    <div style={{
                        padding: '16px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.2)',
                        borderRadius: '12px',
                        display: 'flex',
                        gap: '12px'
                    }}>
                        <AlertTriangle size={20} color="#ef4444" style={{ flexShrink: 0 }} />
                        <div>
                            <div style={{ fontSize: '12px', fontWeight: '600', color: '#ef4444', marginBottom: '4px' }}>CRITICAL IMPACT</div>
                            <div style={{ fontSize: '13px', color: '#ffaeb0', lineHeight: '1.5' }}>
                                {node.processFlow.impact}
                            </div>
                        </div>
                    </div>
                )}

                {/* Dependency Links */}
                {node.dependencies && (
                    <div style={{ marginTop: '24px' }}>
                        <h3 style={{ fontSize: '12px', fontWeight: '600', color: '#8b949e', textTransform: 'uppercase', marginBottom: '12px' }}>
                            Dependencies
                        </h3>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {node.dependencies.map(dep => (
                                <div key={dep} style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '6px 10px',
                                    borderRadius: '20px',
                                    background: 'rgba(56, 139, 253, 0.15)',
                                    border: '1px solid rgba(56, 139, 253, 0.3)',
                                    color: '#58a6ff',
                                    fontSize: '11px',
                                    fontWeight: '500'
                                }}>
                                    <GitBranch size={12} />
                                    {dep}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Key Functions */}
                {node.functions && (
                    <div style={{ marginTop: '24px' }}>
                        <h3 style={{ fontSize: '12px', fontWeight: '600', color: '#8b949e', textTransform: 'uppercase', marginBottom: '12px' }}>
                            Core Functions
                        </h3>
                        <div style={{
                            background: '#0d1117',
                            border: '1px solid rgba(48, 54, 61, 0.5)',
                            borderRadius: '8px',
                            padding: '12px',
                            fontFamily: 'monospace',
                            fontSize: '12px'
                        }}>
                            {node.functions.map((func, i) => (
                                <div key={i} style={{
                                    color: '#e6edf3',
                                    marginBottom: '4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px'
                                }}>
                                    <span style={{ color: '#d2a8ff' }}>def</span>
                                    {func}():
                                </div>
                            ))}
                        </div>
                    </div>
                )}

            </div>
        </motion.div>
    );
};

export default NodeDetailsPanel;
