import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowDown,
    ExternalLink,
    Play,
    FileCode,
    Zap,
    Database,
    Globe,
    Server,
    Monitor,
    Upload,
    Download,
    Beaker,
    AlertTriangle,
    CheckCircle,
    Activity,
    Cpu
} from 'lucide-react';
import { workflows, getWorkflowById } from '../data/workflows';

const StepIcon = ({ index }) => {
    const icons = [Monitor, Server, Zap, Database, FileCode, Globe];
    const Icon = icons[index % icons.length];
    return <Icon size={18} />;
};

function WorkflowVisualizer() {
    const [mode, setMode] = useState('library'); // 'library' or 'lab'
    const [activeWorkflow, setActiveWorkflow] = useState('command-flow');
    const [animatingStep, setAnimatingStep] = useState(null);

    // Lab States
    const [labInput, setLabInput] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const fileInputRef = useRef(null);

    const workflow = getWorkflowById(activeWorkflow);

    const playAnimation = () => {
        if (!workflow) return;
        workflow.steps.forEach((step, idx) => {
            setTimeout(() => {
                setAnimatingStep(idx + 1);
            }, idx * 800);
        });
        setTimeout(() => {
            setAnimatingStep(null);
        }, workflow.steps.length * 800 + 500);
    };

    const openInEditor = (path) => {
        window.open(`vscode://file${path}`, '_blank');
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => setLabInput(e.target.result);
            reader.readAsText(file);
        }
    };

    const handleExport = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(workflows, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "finance_x_workflows.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const runAnalysis = () => {
        setIsAnalyzing(true);
        setAnalysisResult(null);

        // Simulate analysis delay
        setTimeout(() => {
            // Mock logic: Keyword detection for "impact"
            const text = labInput.toLowerCase();
            const hasErrorHandling = text.includes('catch') || text.includes('error') || text.includes('retry');
            const hasDatabase = text.includes('db') || text.includes('database') || text.includes('save');
            const hasCache = text.includes('cache') || text.includes('redis');
            const isComplex = text.length > 500;

            const goodScore = 60 + (hasErrorHandling ? 15 : 0) + (hasCache ? 15 : 0) + (Math.random() * 10);
            const badScore = 100 - goodScore;

            setAnalysisResult({
                goodPercent: Math.round(goodScore),
                badPercent: Math.round(badScore),
                goodPoints: [
                    hasErrorHandling ? "Robust error handling detected" : "Standard flow execution",
                    hasCache ? "Optimized with caching layer" : "Direct execution path",
                    "Modular step separation"
                ],
                badPoints: [
                    !hasErrorHandling ? "Missing explicit error recovery" : "Complex error branching",
                    isComplex ? "High cyclomatic complexity risk" : "Linear dependency chain",
                    hasDatabase ? "Potential database write latency" : "In-memory processing only"
                ]
            });
            setIsAnalyzing(false);
        }, 1500);
    };

    return (
        <div>
            {/* Header / Mode Switcher */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '12px', background: 'var(--bg-secondary)', padding: '4px', borderRadius: '10px' }}>
                    <button
                        onClick={() => setMode('library')}
                        style={{
                            padding: '8px 16px',
                            background: mode === 'library' ? 'var(--bg-tertiary)' : 'transparent',
                            color: mode === 'library' ? 'white' : 'var(--text-muted)',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            fontSize: '13px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            transition: 'all 0.2s'
                        }}
                    >
                        <Database size={14} />
                        Library
                    </button>
                    <button
                        onClick={() => setMode('lab')}
                        style={{
                            padding: '8px 16px',
                            background: mode === 'lab' ? 'var(--accent-purple)' : 'transparent',
                            color: mode === 'lab' ? 'white' : 'var(--text-muted)',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            fontSize: '13px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            transition: 'all 0.2s'
                        }}
                    >
                        <Beaker size={14} />
                        Workflow Lab
                    </button>
                </div>

                {mode === 'library' && (
                    <button
                        onClick={handleExport}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '8px 16px',
                            background: 'rgba(59, 130, 246, 0.1)',
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            borderRadius: '8px',
                            color: 'var(--accent-blue)',
                            fontSize: '13px',
                            cursor: 'pointer',
                        }}
                    >
                        <Download size={14} />
                        Export All JSON
                    </button>
                )}
            </div>

            {/* VIEW: LIBRARY */}
            {mode === 'library' && (
                <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                        <div className="workflow-tabs">
                            {workflows.map((wf) => (
                                <button
                                    key={wf.id}
                                    className={`workflow-tab ${activeWorkflow === wf.id ? 'active' : ''}`}
                                    onClick={() => {
                                        setActiveWorkflow(wf.id);
                                        setAnimatingStep(null);
                                    }}
                                >
                                    {wf.name}
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={playAnimation}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '10px 20px',
                                background: 'linear-gradient(135deg, var(--accent-green), #16a34a)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'white',
                                fontSize: '14px',
                                fontWeight: '500',
                                cursor: 'pointer',
                            }}
                        >
                            <Play size={16} />
                            Play Animation
                        </button>
                    </div>

                    <div style={{
                        padding: '16px 20px',
                        background: 'var(--bg-secondary)',
                        borderRadius: '8px',
                        marginBottom: '24px',
                        border: '1px solid var(--border-color)',
                    }}>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                            {workflow?.description}
                        </p>
                    </div>

                    <div className="workflow-diagram">
                        {workflow?.steps.map((step, idx) => (
                            <div key={step.id}>
                                <motion.div
                                    className="workflow-step"
                                    initial={{ opacity: 0.6 }}
                                    animate={{
                                        opacity: animatingStep === step.id || animatingStep === null ? 1 : 0.4,
                                        scale: animatingStep === step.id ? 1.02 : 1,
                                    }}
                                    transition={{ duration: 0.3 }}
                                    style={{
                                        background: animatingStep === step.id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                        padding: '16px',
                                        borderRadius: '12px',
                                        border: animatingStep === step.id ? '1px solid var(--accent-blue)' : '1px solid transparent',
                                    }}
                                >
                                    <div
                                        className="step-number"
                                        style={{
                                            background: animatingStep === step.id
                                                ? 'linear-gradient(135deg, var(--accent-green), #16a34a)'
                                                : 'var(--accent-blue)',
                                        }}
                                    >
                                        {animatingStep === step.id ? <Zap size={16} /> : step.id}
                                    </div>
                                    <div className="step-content" style={{ flex: 1 }}>
                                        <div className="step-title">{step.title}</div>
                                        <div className="step-description">{step.description}</div>
                                        {step.function && (
                                            <code style={{
                                                display: 'inline-block',
                                                marginTop: '8px',
                                                padding: '4px 10px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '4px',
                                                fontSize: '12px',
                                                color: 'var(--accent-cyan)',
                                            }}>
                                                {step.function}
                                            </code>
                                        )}
                                        {step.details && (
                                            <div style={{
                                                marginTop: '8px',
                                                padding: '8px 12px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '6px',
                                                fontSize: '12px',
                                                color: 'var(--text-muted)',
                                                fontStyle: 'italic',
                                            }}>
                                                {step.details}
                                            </div>
                                        )}
                                    </div>
                                    {step.file && (
                                        <button
                                            onClick={() => openInEditor(step.file)}
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                padding: '8px 12px',
                                                background: 'var(--bg-tertiary)',
                                                border: '1px solid var(--border-color)',
                                                borderRadius: '6px',
                                                color: 'var(--text-secondary)',
                                                fontSize: '12px',
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
                                            <ExternalLink size={14} />
                                            View Code
                                        </button>
                                    )}
                                </motion.div>

                                {idx < workflow.steps.length - 1 && (
                                    <motion.div
                                        className="step-arrow"
                                        animate={{
                                            color: animatingStep === step.id + 1 ? 'var(--accent-green)' : 'var(--text-muted)',
                                        }}
                                    >
                                        <ArrowDown size={20} />
                                    </motion.div>
                                )}
                            </div>
                        ))}
                    </div>
                </>
            )}

            {/* VIEW: LAB */}
            {mode === 'lab' && (
                <div style={{ display: 'flex', gap: '24px', height: '100%' }}>
                    {/* Input Area */}
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div style={{
                            padding: '16px',
                            background: 'var(--bg-secondary)',
                            borderRadius: '12px',
                            border: '1px solid var(--border-color)',
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                                <h3 style={{ fontSize: '14px', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <FileCode size={16} color="var(--accent-purple)" />
                                    Workflow Definition
                                </h3>
                                <div>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        style={{ display: 'none' }}
                                        onChange={handleFileUpload}
                                        accept=".json,.yaml,.txt"
                                    />
                                    <button
                                        onClick={() => fileInputRef.current.click()}
                                        style={{
                                            background: 'transparent',
                                            border: 'none',
                                            color: 'var(--accent-blue)',
                                            fontSize: '12px',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px'
                                        }}
                                    >
                                        <Upload size={12} /> Import File
                                    </button>
                                </div>
                            </div>
                            <textarea
                                value={labInput}
                                onChange={(e) => setLabInput(e.target.value)}
                                placeholder={`Paste your workflow JSON or logic here...\n\nExample:\n{\n  "steps": [\n    "Fetch data from API",\n    "Cache result",\n    "Handle errors"\n  ]\n}`}
                                style={{
                                    width: '100%',
                                    height: '300px',
                                    background: 'var(--bg-tertiary)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: '8px',
                                    padding: '12px',
                                    color: 'var(--text-primary)',
                                    fontFamily: 'monospace',
                                    fontSize: '13px',
                                    resize: 'vertical'
                                }}
                            />
                        </div>
                        <button
                            onClick={runAnalysis}
                            disabled={!labInput || isAnalyzing}
                            style={{
                                padding: '12px',
                                background: isAnalyzing ? 'var(--bg-tertiary)' : 'linear-gradient(135deg, var(--accent-purple), #9333ea)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'white',
                                fontWeight: '600',
                                cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                gap: '8px'
                            }}
                        >
                            {isAnalyzing ? (
                                <>
                                    <Activity size={16} className="spin" /> Analyzing Impact...
                                </>
                            ) : (
                                <>
                                    <Zap size={16} /> Run Impact Analysis
                                </>
                            )}
                        </button>
                    </div>

                    {/* Results Area */}
                    <div style={{ flex: 1 }}>
                        <AnimatePresence mode="wait">
                            {!analysisResult ? (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 0.5 }}
                                    style={{
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        border: '2px dashed var(--border-color)',
                                        borderRadius: '12px',
                                        color: 'var(--text-muted)'
                                    }}
                                >
                                    <Cpu size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                                    <p>Ready to analyze system impact</p>
                                </motion.div>
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
                                >
                                    {/* Score Cards */}
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                        <div style={{
                                            background: 'rgba(34, 197, 94, 0.1)',
                                            border: '1px solid rgba(34, 197, 94, 0.3)',
                                            borderRadius: '12px',
                                            padding: '20px',
                                            textAlign: 'center'
                                        }}>
                                            <div style={{ fontSize: '13px', color: '#22c55e', fontWeight: '600', marginBottom: '8px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px' }}>
                                                <CheckCircle size={16} /> POSITIVE IMPACT
                                            </div>
                                            <div style={{ fontSize: '36px', fontWeight: '800', color: '#22c55e' }}>
                                                {analysisResult.goodPercent}%
                                            </div>
                                            <div style={{ fontSize: '11px', color: '#86efac', marginTop: '4px' }}>Efficiency & Stability</div>
                                        </div>

                                        <div style={{
                                            background: 'rgba(239, 68, 68, 0.1)',
                                            border: '1px solid rgba(239, 68, 68, 0.3)',
                                            borderRadius: '12px',
                                            padding: '20px',
                                            textAlign: 'center'
                                        }}>
                                            <div style={{ fontSize: '13px', color: '#ef4444', fontWeight: '600', marginBottom: '8px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px' }}>
                                                <AlertTriangle size={16} /> NEGATIVE RISK
                                            </div>
                                            <div style={{ fontSize: '36px', fontWeight: '800', color: '#ef4444' }}>
                                                {analysisResult.badPercent}%
                                            </div>
                                            <div style={{ fontSize: '11px', color: '#fca5a5', marginTop: '4px' }}>Latencies & Errors</div>
                                        </div>
                                    </div>

                                    {/* Detailed Breakdown */}
                                    <div style={{
                                        background: 'var(--bg-secondary)',
                                        borderRadius: '12px',
                                        border: '1px solid var(--border-color)',
                                        padding: '20px'
                                    }}>
                                        <h4 style={{ margin: '0 0 16px', fontSize: '14px', color: 'var(--text-primary)' }}>Impact Breakdown</h4>

                                        <div style={{ marginBottom: '20px' }}>
                                            <div style={{ fontSize: '12px', fontWeight: '600', color: '#22c55e', marginBottom: '8px' }}>PROS</div>
                                            {analysisResult.goodPoints.map((point, i) => (
                                                <div key={i} style={{ display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                                                    <span style={{ color: '#22c55e' }}>+</span> {point}
                                                </div>
                                            ))}
                                        </div>

                                        <div>
                                            <div style={{ fontSize: '12px', fontWeight: '600', color: '#ef4444', marginBottom: '8px' }}>CONS</div>
                                            {analysisResult.badPoints.map((point, i) => (
                                                <div key={i} style={{ display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                                                    <span style={{ color: '#ef4444' }}>-</span> {point}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            )}
        </div>
    );
}

export default WorkflowVisualizer;
