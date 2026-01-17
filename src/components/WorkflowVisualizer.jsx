import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    ArrowDown,
    ExternalLink,
    Play,
    FileCode,
    Zap,
    Database,
    Globe,
    Server,
    Monitor
} from 'lucide-react';
import { workflows, getWorkflowById } from '../data/workflows';

const StepIcon = ({ index }) => {
    const icons = [Monitor, Server, Zap, Database, FileCode, Globe];
    const Icon = icons[index % icons.length];
    return <Icon size={18} />;
};

function WorkflowVisualizer() {
    const [activeWorkflow, setActiveWorkflow] = useState('command-flow');
    const [animatingStep, setAnimatingStep] = useState(null);

    const workflow = getWorkflowById(activeWorkflow);

    const playAnimation = () => {
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

    return (
        <div>
            {/* Workflow Tabs */}
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

            {/* Workflow Description */}
            <div style={{
                padding: '16px 20px',
                background: 'var(--bg-secondary)',
                borderRadius: '8px',
                marginBottom: '24px',
                border: '1px solid var(--border-color)',
            }}>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                    {workflow.description}
                </p>
            </div>

            {/* Workflow Steps */}
            <div className="workflow-diagram">
                {workflow.steps.map((step, idx) => (
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

                        {/* Arrow between steps */}
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

            {/* Legend */}
            <div style={{
                marginTop: '32px',
                padding: '16px 20px',
                background: 'var(--bg-secondary)',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                display: 'flex',
                gap: '24px',
                flexWrap: 'wrap',
            }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>Legend:</strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--accent-blue)' }} />
                    <span>Step Number</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                    <code style={{ padding: '2px 6px', background: 'var(--bg-tertiary)', borderRadius: '4px', color: 'var(--accent-cyan)' }}>
                        function()
                    </code>
                    <span>Function Call</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                    <ExternalLink size={12} />
                    <span>Click to open in VS Code</span>
                </div>
            </div>
        </div>
    );
}

export default WorkflowVisualizer;
