"""
Audit & Compliance Layer
MiFID II / SOX compliant logging for regulatory requirements
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Import persistence
from extensions.persistence import get_db


class AuditLogger:
    """
    Immutable append-only audit trail.
    Regulatory compliance: MiFID II (EU), SOX (US), Dodd-Frank
    """
    
    def __init__(self):
        self.db = get_db()
        print("[Audit] Compliance logging enabled")
    
    def log_command(
        self, 
        command: str, 
        user: str = "terminal",
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None
    ):
        """
        Log every terminal command for audit trail.
        MiFID II Article 17: All algo trading decisions must be logged.
        """
        self.db.log_command(
            command=command,
            inputs=inputs or {},
            outputs=outputs or {},
            user=user
        )
    
    def log_decision(
        self,
        model_name: str,
        inputs: Dict,
        outputs: Dict,
        rationale: str = ""
    ):
        """
        Log model decisions (e.g., ADVISE command output).
        Required for Model Risk Management (SR 11-7).
        """
        decision_log = {
            "model": model_name,
            "inputs": inputs,
            "outputs": outputs,
            "rationale": rationale,
            "timestamp": datetime.now().isoformat()
        }
        
        self.db.log_command(
            command=f"MODEL_DECISION:{model_name}",
            inputs=inputs,
            outputs=outputs,
            user="system"
        )
    
    def export_audit_trail(
        self, 
        start: datetime, 
        end: datetime,
        format: str = "json"
    ) -> List[Dict]:
        """
        Export audit trail for regulatory reporting.
        Supports JSON, CSV formats.
        """
        records = self.db.export_audit_trail(start, end)
        
        if format == "csv":
            # Convert to CSV-friendly format
            import csv
            import io
            
            output = io.StringIO()
            if records:
                writer = csv.DictWriter(output, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)
            
            return output.getvalue()
        
        return records
    
    def get_user_activity(self, user: str, hours: int = 24) -> List[Dict]:
        """Track specific user activity"""
        end = datetime.now()
        start = end - timedelta(hours=hours)
        
        all_records = self.db.export_audit_trail(start, end)
        return [r for r in all_records if r['user'] == user]
    
    def detect_anomalies(self) -> List[Dict]:
        """
        Basic anomaly detection for compliance.
        Flags: High-frequency commands, unusual patterns
        """
        from datetime import timedelta
        
        # Check last hour
        end = datetime.now()
        start = end - timedelta(hours=1)
        records = self.db.export_audit_trail(start, end)
        
        anomalies = []
        
        # Flag 1: >100 commands in 1 hour
        if len(records) > 100:
            anomalies.append({
                "type": "HIGH_FREQUENCY",
                "severity": "WARNING",
                "details": f"{len(records)} commands in 1 hour",
                "timestamp": datetime.now().isoformat()
            })
        
        # Flag 2: Repeated failed commands
        errors = [r for r in records if r.get('outputs', {}).get('type') == 'ERROR']
        if len(errors) > 10:
            anomalies.append({
                "type": "REPEATED_ERRORS",
                "severity": "WARNING",
                "details": f"{len(errors)} errors in 1 hour",
                "timestamp": datetime.now().isoformat()
            })
        
        return anomalies
    
    def generate_compliance_report(self, start: datetime, end: datetime) -> Dict:
        """
        Full compliance report for auditors.
        Includes: command count, user activity, model decisions, anomalies
        """
        records = self.db.export_audit_trail(start, end)
        
        # Aggregate statistics
        total_commands = len(records)
        unique_users = len(set(r['user'] for r in records))
        
        command_types = {}
        for r in records:
            cmd = r['command'].split()[0] if r['command'] else 'UNKNOWN'
            command_types[cmd] = command_types.get(cmd, 0) + 1
        
        model_decisions = [r for r in records if 'MODEL_DECISION' in r['command']]
        
        return {
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "summary": {
                "total_commands": total_commands,
                "unique_users": unique_users,
                "model_decisions": len(model_decisions)
            },
            "command_breakdown": command_types,
            "anomalies": self.detect_anomalies(),
            "generated_at": datetime.now().isoformat()
        }


# Singleton instance
_audit_instance = None

def get_audit() -> AuditLogger:
    """Get or create audit logger instance"""
    global _audit_instance
    if _audit_instance is None:
        _audit_instance = AuditLogger()
    return _audit_instance
