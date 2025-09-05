"""
Advanced Incident Response System
Automated incident detection, analysis, and response
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
from pathlib import Path

from core.config import settings
from core.ai_engine import AIEngine

logger = logging.getLogger(__name__)

class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    affected_assets: List[str]
    threat_indicators: List[str]
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str]
    tags: List[str]
    evidence: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    resolution_notes: Optional[str]
    ai_analysis: Dict[str, Any]

@dataclass
class IncidentResponse:
    """Incident response action"""
    id: str
    incident_id: str
    action_type: str
    description: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]

class IncidentResponseSystem:
    """
    Advanced Incident Response System
    Automated detection, analysis, and response to security incidents
    """
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.incidents = {}
        self.responses = {}
        self.monitoring = False
        self.alert_rules = {}
        
        # Initialize database
        self._init_database()
        
        # Load response playbooks
        self._load_response_playbooks()
        
        # Initialize alert rules
        self._init_alert_rules()
    
    def _init_database(self):
        """Initialize incident response database"""
        try:
            self.db_path = Path("data/incident_response.db")
            self.db_path.parent.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create incidents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    severity TEXT,
                    status TEXT,
                    affected_assets TEXT,
                    threat_indicators TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    assigned_to TEXT,
                    tags TEXT,
                    evidence TEXT,
                    timeline TEXT,
                    resolution_notes TEXT,
                    ai_analysis TEXT
                )
            """)
            
            # Create responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id TEXT PRIMARY KEY,
                    incident_id TEXT,
                    action_type TEXT,
                    description TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    FOREIGN KEY (incident_id) REFERENCES incidents (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Incident response database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize incident response database: {e}")
    
    def _load_response_playbooks(self):
        """Load incident response playbooks"""
        try:
            playbooks_file = Path("data/response_playbooks.yaml")
            if playbooks_file.exists():
                import yaml
                with open(playbooks_file, 'r') as f:
                    self.playbooks = yaml.safe_load(f)
            else:
                # Default playbooks
                self.playbooks = {
                    "malware_detection": {
                        "name": "Malware Detection Response",
                        "steps": [
                            "Isolate affected systems",
                            "Collect malware samples",
                            "Analyze malware behavior",
                            "Update security controls",
                            "Monitor for lateral movement"
                        ],
                        "automated": True
                    },
                    "data_breach": {
                        "name": "Data Breach Response",
                        "steps": [
                            "Contain the breach",
                            "Assess data exposure",
                            "Notify stakeholders",
                            "Implement additional controls",
                            "Conduct forensic analysis"
                        ],
                        "automated": False
                    },
                    "ddos_attack": {
                        "name": "DDoS Attack Response",
                        "steps": [
                            "Activate DDoS protection",
                            "Monitor network traffic",
                            "Implement rate limiting",
                            "Coordinate with ISP",
                            "Document attack details"
                        ],
                        "automated": True
                    }
                }
            
            logger.info("✅ Response playbooks loaded")
            
        except Exception as e:
            logger.error(f"Failed to load response playbooks: {e}")
    
    def _init_alert_rules(self):
        """Initialize incident detection alert rules"""
        try:
            self.alert_rules = {
                "high_risk_vulnerability": {
                    "condition": "vulnerability.severity == 'critical'",
                    "action": "create_incident",
                    "severity": "high",
                    "playbook": "vulnerability_response"
                },
                "multiple_failed_logins": {
                    "condition": "failed_logins > 10 in 5 minutes",
                    "action": "create_incident",
                    "severity": "medium",
                    "playbook": "brute_force_response"
                },
                "suspicious_network_activity": {
                    "condition": "unusual_traffic_patterns detected",
                    "action": "create_incident",
                    "severity": "medium",
                    "playbook": "network_anomaly_response"
                },
                "malware_detection": {
                    "condition": "malware_signature_matched",
                    "action": "create_incident",
                    "severity": "critical",
                    "playbook": "malware_detection"
                }
            }
            
            logger.info("✅ Alert rules initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize alert rules: {e}")
    
    async def start_monitoring(self):
        """Start incident monitoring and detection"""
        self.monitoring = True
        logger.info("🔄 Starting incident response monitoring...")
        
        while self.monitoring:
            try:
                # Monitor for new incidents
                await self._monitor_for_incidents()
                
                # Process open incidents
                await self._process_open_incidents()
                
                # Update incident statuses
                await self._update_incident_statuses()
                
                # Wait for next cycle
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in incident monitoring: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds before retrying
    
    async def _monitor_for_incidents(self):
        """Monitor for new security incidents"""
        try:
            # This would integrate with various security tools
            # For now, we'll simulate incident detection
            
            # Check for high-risk vulnerabilities
            await self._check_vulnerability_alerts()
            
            # Check for suspicious activities
            await self._check_suspicious_activities()
            
            # Check for malware detections
            await self._check_malware_detections()
            
        except Exception as e:
            logger.error(f"Error monitoring for incidents: {e}")
    
    async def _check_vulnerability_alerts(self):
        """Check for vulnerability-based incidents"""
        try:
            # This would check vulnerability scanner results
            # For demo, we'll simulate some checks
            pass
            
        except Exception as e:
            logger.error(f"Error checking vulnerability alerts: {e}")
    
    async def _check_suspicious_activities(self):
        """Check for suspicious activity incidents"""
        try:
            # This would check various security logs and events
            # For demo, we'll simulate some checks
            pass
            
        except Exception as e:
            logger.error(f"Error checking suspicious activities: {e}")
    
    async def _check_malware_detections(self):
        """Check for malware detection incidents"""
        try:
            # This would check malware detection systems
            # For demo, we'll simulate some checks
            pass
            
        except Exception as e:
            logger.error(f"Error checking malware detections: {e}")
    
    async def _process_open_incidents(self):
        """Process open incidents"""
        try:
            for incident_id, incident in self.incidents.items():
                if incident.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]:
                    await self._process_incident(incident)
            
        except Exception as e:
            logger.error(f"Error processing open incidents: {e}")
    
    async def _process_incident(self, incident: SecurityIncident):
        """Process a specific incident"""
        try:
            # Update incident status
            incident.status = IncidentStatus.INVESTIGATING
            incident.updated_at = datetime.now()
            
            # Perform AI analysis
            ai_analysis = await self._analyze_incident_with_ai(incident)
            incident.ai_analysis = ai_analysis
            
            # Execute response playbook
            await self._execute_response_playbook(incident)
            
            # Update timeline
            self._add_timeline_event(incident, "incident_processed", "Incident processed by AI system")
            
            # Save incident
            await self._save_incident(incident)
            
        except Exception as e:
            logger.error(f"Error processing incident {incident.id}: {e}")
    
    async def _analyze_incident_with_ai(self, incident: SecurityIncident) -> Dict[str, Any]:
        """Analyze incident using AI"""
        try:
            # Prepare incident data for AI analysis
            incident_text = f"""
            Incident: {incident.title}
            Description: {incident.description}
            Severity: {incident.severity.value}
            Affected Assets: {', '.join(incident.affected_assets)}
            Threat Indicators: {', '.join(incident.threat_indicators)}
            """
            
            # Use AI engine to analyze incident
            ai_result = await self.ai_engine.detect_threat(incident_text, "incident_analysis")
            
            # Generate additional analysis
            analysis = {
                "threat_level": ai_result.get("threat_level", "unknown"),
                "confidence": ai_result.get("confidence", 0.5),
                "threat_indicators": ai_result.get("threat_indicators", []),
                "recommended_actions": self._generate_recommended_actions(incident),
                "risk_score": self._calculate_incident_risk_score(incident),
                "attack_vector": self._identify_attack_vector(incident),
                "impact_assessment": self._assess_incident_impact(incident)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing incident with AI: {e}")
            return {"error": str(e)}
    
    def _generate_recommended_actions(self, incident: SecurityIncident) -> List[str]:
        """Generate recommended actions for incident"""
        actions = []
        
        if incident.severity == IncidentSeverity.CRITICAL:
            actions.extend([
                "Immediately isolate affected systems",
                "Activate incident response team",
                "Notify senior management",
                "Implement emergency controls"
            ])
        elif incident.severity == IncidentSeverity.HIGH:
            actions.extend([
                "Contain the threat",
                "Collect evidence",
                "Update security controls",
                "Monitor for lateral movement"
            ])
        else:
            actions.extend([
                "Document the incident",
                "Implement preventive measures",
                "Review security policies"
            ])
        
        return actions
    
    def _calculate_incident_risk_score(self, incident: SecurityIncident) -> float:
        """Calculate risk score for incident"""
        base_score = 0.0
        
        # Base score from severity
        severity_scores = {
            IncidentSeverity.LOW: 0.2,
            IncidentSeverity.MEDIUM: 0.4,
            IncidentSeverity.HIGH: 0.7,
            IncidentSeverity.CRITICAL: 0.9
        }
        base_score += severity_scores.get(incident.severity, 0.5)
        
        # Additional factors
        if len(incident.affected_assets) > 5:
            base_score += 0.1
        if len(incident.threat_indicators) > 3:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _identify_attack_vector(self, incident: SecurityIncident) -> str:
        """Identify likely attack vector"""
        description_lower = incident.description.lower()
        
        if "phishing" in description_lower or "email" in description_lower:
            return "Email/Phishing"
        elif "web" in description_lower or "http" in description_lower:
            return "Web Application"
        elif "network" in description_lower or "traffic" in description_lower:
            return "Network"
        elif "malware" in description_lower or "virus" in description_lower:
            return "Malware"
        else:
            return "Unknown"
    
    def _assess_incident_impact(self, incident: SecurityIncident) -> Dict[str, Any]:
        """Assess impact of incident"""
        impact = {
            "data_breach": False,
            "system_compromise": False,
            "service_disruption": False,
            "financial_impact": "low",
            "reputation_impact": "low"
        }
        
        description_lower = incident.description.lower()
        
        if "breach" in description_lower or "data" in description_lower:
            impact["data_breach"] = True
            impact["financial_impact"] = "high"
            impact["reputation_impact"] = "high"
        
        if "compromise" in description_lower or "hack" in description_lower:
            impact["system_compromise"] = True
            impact["financial_impact"] = "medium"
        
        if "ddos" in description_lower or "outage" in description_lower:
            impact["service_disruption"] = True
            impact["financial_impact"] = "medium"
        
        return impact
    
    async def _execute_response_playbook(self, incident: SecurityIncident):
        """Execute response playbook for incident"""
        try:
            # Determine appropriate playbook
            playbook_name = self._determine_playbook(incident)
            
            if playbook_name in self.playbooks:
                playbook = self.playbooks[playbook_name]
                
                # Execute playbook steps
                for step in playbook.get("steps", []):
                    response = IncidentResponse(
                        id=f"resp_{int(datetime.now().timestamp())}",
                        incident_id=incident.id,
                        action_type="playbook_step",
                        description=step,
                        status="pending",
                        created_at=datetime.now(),
                        completed_at=None,
                        result=None
                    )
                    
                    # Execute step
                    await self._execute_response_action(response)
                    
                    # Add to incident timeline
                    self._add_timeline_event(incident, "playbook_step", step)
            
        except Exception as e:
            logger.error(f"Error executing response playbook: {e}")
    
    def _determine_playbook(self, incident: SecurityIncident) -> str:
        """Determine appropriate playbook for incident"""
        description_lower = incident.description.lower()
        
        if "malware" in description_lower:
            return "malware_detection"
        elif "breach" in description_lower or "data" in description_lower:
            return "data_breach"
        elif "ddos" in description_lower:
            return "ddos_attack"
        else:
            return "general_response"
    
    async def _execute_response_action(self, response: IncidentResponse):
        """Execute a response action"""
        try:
            # Mark as in progress
            response.status = "in_progress"
            
            # Simulate action execution
            await asyncio.sleep(1)  # Simulate processing time
            
            # Mark as completed
            response.status = "completed"
            response.completed_at = datetime.now()
            response.result = {"status": "success", "message": "Action completed successfully"}
            
            # Save response
            await self._save_response(response)
            
        except Exception as e:
            logger.error(f"Error executing response action: {e}")
            response.status = "failed"
            response.result = {"status": "error", "message": str(e)}
    
    def _add_timeline_event(self, incident: SecurityIncident, event_type: str, description: str):
        """Add event to incident timeline"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "user": "system"
        }
        incident.timeline.append(event)
    
    async def _update_incident_statuses(self):
        """Update incident statuses based on progress"""
        try:
            for incident in self.incidents.values():
                if incident.status == IncidentStatus.INVESTIGATING:
                    # Check if investigation is complete
                    if self._is_investigation_complete(incident):
                        incident.status = IncidentStatus.CONTAINED
                        incident.updated_at = datetime.now()
                        self._add_timeline_event(incident, "status_change", "Incident contained")
                
                elif incident.status == IncidentStatus.CONTAINED:
                    # Check if incident is resolved
                    if self._is_incident_resolved(incident):
                        incident.status = IncidentStatus.RESOLVED
                        incident.updated_at = datetime.now()
                        self._add_timeline_event(incident, "status_change", "Incident resolved")
            
        except Exception as e:
            logger.error(f"Error updating incident statuses: {e}")
    
    def _is_investigation_complete(self, incident: SecurityIncident) -> bool:
        """Check if investigation is complete"""
        # Simple heuristic - in reality, this would be more sophisticated
        return len(incident.timeline) > 5
    
    def _is_incident_resolved(self, incident: SecurityIncident) -> bool:
        """Check if incident is resolved"""
        # Simple heuristic - in reality, this would be more sophisticated
        return len(incident.timeline) > 10
    
    async def create_incident(self, title: str, description: str, severity: str, 
                            affected_assets: List[str], threat_indicators: List[str] = None) -> str:
        """Create a new security incident"""
        try:
            incident_id = f"inc_{int(datetime.now().timestamp())}"
            
            incident = SecurityIncident(
                id=incident_id,
                title=title,
                description=description,
                severity=IncidentSeverity(severity),
                status=IncidentStatus.OPEN,
                affected_assets=affected_assets,
                threat_indicators=threat_indicators or [],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                assigned_to=None,
                tags=[],
                evidence=[],
                timeline=[],
                resolution_notes=None,
                ai_analysis={}
            )
            
            # Add initial timeline event
            self._add_timeline_event(incident, "incident_created", "Incident created")
            
            # Store incident
            self.incidents[incident_id] = incident
            
            # Save to database
            await self._save_incident(incident)
            
            logger.info(f"✅ Created incident: {incident_id}")
            return incident_id
            
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            raise
    
    async def _save_incident(self, incident: SecurityIncident):
        """Save incident to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO incidents 
                (id, title, description, severity, status, affected_assets, threat_indicators,
                 created_at, updated_at, assigned_to, tags, evidence, timeline, 
                 resolution_notes, ai_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident.id, incident.title, incident.description, incident.severity.value,
                incident.status.value, json.dumps(incident.affected_assets),
                json.dumps(incident.threat_indicators), incident.created_at.isoformat(),
                incident.updated_at.isoformat(), incident.assigned_to, json.dumps(incident.tags),
                json.dumps(incident.evidence), json.dumps(incident.timeline),
                incident.resolution_notes, json.dumps(incident.ai_analysis)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save incident: {e}")
    
    async def _save_response(self, response: IncidentResponse):
        """Save response to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO responses 
                (id, incident_id, action_type, description, status, created_at, 
                 completed_at, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                response.id, response.incident_id, response.action_type, response.description,
                response.status, response.created_at.isoformat(),
                response.completed_at.isoformat() if response.completed_at else None,
                json.dumps(response.result) if response.result else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save response: {e}")
    
    async def get_incidents(self, status: str = None, severity: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of incidents"""
        try:
            incidents = []
            for incident in self.incidents.values():
                if status and incident.status.value != status:
                    continue
                if severity and incident.severity.value != severity:
                    continue
                
                incidents.append({
                    "id": incident.id,
                    "title": incident.title,
                    "description": incident.description,
                    "severity": incident.severity.value,
                    "status": incident.status.value,
                    "affected_assets": incident.affected_assets,
                    "threat_indicators": incident.threat_indicators,
                    "created_at": incident.created_at.isoformat(),
                    "updated_at": incident.updated_at.isoformat(),
                    "assigned_to": incident.assigned_to,
                    "tags": incident.tags,
                    "ai_analysis": incident.ai_analysis
                })
            
            return incidents[:limit]
            
        except Exception as e:
            logger.error(f"Error getting incidents: {e}")
            return []
    
    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get specific incident details"""
        try:
            if incident_id not in self.incidents:
                return None
            
            incident = self.incidents[incident_id]
            return {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "affected_assets": incident.affected_assets,
                "threat_indicators": incident.threat_indicators,
                "created_at": incident.created_at.isoformat(),
                "updated_at": incident.updated_at.isoformat(),
                "assigned_to": incident.assigned_to,
                "tags": incident.tags,
                "evidence": incident.evidence,
                "timeline": incident.timeline,
                "resolution_notes": incident.resolution_notes,
                "ai_analysis": incident.ai_analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting incident {incident_id}: {e}")
            return None
    
    def stop_monitoring(self):
        """Stop incident monitoring"""
        self.monitoring = False
        logger.info("🛑 Stopped incident response monitoring")