"""
Compliance Monitoring System
Automated compliance checking and reporting
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
from pathlib import Path

from core.config import settings
from core.ai_engine import AIEngine

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    NIST = "nist"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class ComplianceRequirement:
    """Compliance requirement data structure"""
    id: str
    framework: ComplianceFramework
    control_id: str
    title: str
    description: str
    category: str
    priority: str
    status: ComplianceStatus
    evidence: List[str]
    last_checked: datetime
    next_check: datetime
    score: float
    notes: str

@dataclass
class ComplianceAssessment:
    """Compliance assessment data structure"""
    id: str
    framework: ComplianceFramework
    assessment_date: datetime
    overall_score: float
    status: ComplianceStatus
    requirements: List[ComplianceRequirement]
    findings: List[Dict[str, Any]]
    recommendations: List[str]

class ComplianceMonitor:
    """
    Advanced Compliance Monitoring System
    Automated compliance checking and reporting
    """
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.requirements = {}
        self.assessments = {}
        self.monitoring = False
        
        # Initialize database
        self._init_database()
        
        # Load compliance frameworks
        self._load_compliance_frameworks()
        
        # Initialize monitoring rules
        self._init_monitoring_rules()
    
    def _init_database(self):
        """Initialize compliance monitoring database"""
        try:
            self.db_path = Path("data/compliance_monitor.db")
            self.db_path.parent.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create requirements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_requirements (
                    id TEXT PRIMARY KEY,
                    framework TEXT,
                    control_id TEXT,
                    title TEXT,
                    description TEXT,
                    category TEXT,
                    priority TEXT,
                    status TEXT,
                    evidence TEXT,
                    last_checked TIMESTAMP,
                    next_check TIMESTAMP,
                    score REAL,
                    notes TEXT
                )
            """)
            
            # Create assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    id TEXT PRIMARY KEY,
                    framework TEXT,
                    assessment_date TIMESTAMP,
                    overall_score REAL,
                    status TEXT,
                    requirements TEXT,
                    findings TEXT,
                    recommendations TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Compliance monitoring database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance database: {e}")
    
    def _load_compliance_frameworks(self):
        """Load compliance frameworks and requirements"""
        try:
            frameworks_file = Path("data/compliance_frameworks.yaml")
            if frameworks_file.exists():
                import yaml
                with open(frameworks_file, 'r') as f:
                    self.frameworks = yaml.safe_load(f)
            else:
                # Default compliance frameworks
                self.frameworks = {
                    "iso27001": {
                        "name": "ISO 27001",
                        "description": "Information Security Management System",
                        "requirements": [
                            {
                                "id": "A.5.1.1",
                                "title": "Information Security Policies",
                                "description": "Management direction and support for information security",
                                "category": "Information Security Policies",
                                "priority": "high"
                            },
                            {
                                "id": "A.6.1.1",
                                "title": "Information Security Roles and Responsibilities",
                                "description": "All information security responsibilities shall be defined and allocated",
                                "category": "Organization of Information Security",
                                "priority": "high"
                            },
                            {
                                "id": "A.8.1.1",
                                "title": "Inventory of Assets",
                                "description": "Assets associated with information and information processing facilities shall be identified",
                                "category": "Asset Management",
                                "priority": "medium"
                            }
                        ]
                    },
                    "soc2": {
                        "name": "SOC 2",
                        "description": "Service Organization Control 2",
                        "requirements": [
                            {
                                "id": "CC6.1",
                                "title": "Logical and Physical Access Security",
                                "description": "The entity implements logical access security software, infrastructure, and architectures",
                                "category": "Security",
                                "priority": "high"
                            },
                            {
                                "id": "CC6.2",
                                "title": "System Access",
                                "description": "Prior to issuing system credentials and granting system access",
                                "category": "Security",
                                "priority": "high"
                            }
                        ]
                    },
                    "pci_dss": {
                        "name": "PCI DSS",
                        "description": "Payment Card Industry Data Security Standard",
                        "requirements": [
                            {
                                "id": "1.1",
                                "title": "Install and maintain a firewall configuration",
                                "description": "Install and maintain a firewall configuration to protect cardholder data",
                                "category": "Build and Maintain a Secure Network",
                                "priority": "high"
                            },
                            {
                                "id": "2.1",
                                "title": "Do not use vendor-supplied defaults",
                                "description": "Always change vendor-supplied defaults and remove or disable unnecessary default accounts",
                                "category": "Build and Maintain a Secure Network",
                                "priority": "high"
                            }
                        ]
                    }
                }
            
            logger.info("✅ Compliance frameworks loaded")
            
        except Exception as e:
            logger.error(f"Failed to load compliance frameworks: {e}")
    
    def _init_monitoring_rules(self):
        """Initialize compliance monitoring rules"""
        try:
            self.monitoring_rules = {
                "password_policy": {
                    "check": "password_complexity_enforced",
                    "frequency": "daily",
                    "framework": "iso27001",
                    "requirement": "A.9.4.2"
                },
                "access_control": {
                    "check": "user_access_reviewed",
                    "frequency": "weekly",
                    "framework": "soc2",
                    "requirement": "CC6.2"
                },
                "vulnerability_management": {
                    "check": "vulnerabilities_patched",
                    "frequency": "daily",
                    "framework": "pci_dss",
                    "requirement": "6.2"
                }
            }
            
            logger.info("✅ Compliance monitoring rules initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring rules: {e}")
    
    async def start_monitoring(self):
        """Start compliance monitoring"""
        self.monitoring = True
        logger.info("🔄 Starting compliance monitoring...")
        
        while self.monitoring:
            try:
                # Check compliance requirements
                await self._check_compliance_requirements()
                
                # Generate compliance reports
                await self._generate_compliance_reports()
                
                # Update compliance scores
                await self._update_compliance_scores()
                
                # Wait for next cycle
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in compliance monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _check_compliance_requirements(self):
        """Check compliance requirements"""
        try:
            for framework_name, framework in self.frameworks.items():
                for req_data in framework.get("requirements", []):
                    await self._check_requirement(framework_name, req_data)
            
        except Exception as e:
            logger.error(f"Error checking compliance requirements: {e}")
    
    async def _check_requirement(self, framework_name: str, req_data: Dict[str, Any]):
        """Check a specific compliance requirement"""
        try:
            req_id = f"{framework_name}_{req_data['id']}"
            
            # Check if requirement exists
            if req_id not in self.requirements:
                # Create new requirement
                requirement = ComplianceRequirement(
                    id=req_id,
                    framework=ComplianceFramework(framework_name),
                    control_id=req_data["id"],
                    title=req_data["title"],
                    description=req_data["description"],
                    category=req_data["category"],
                    priority=req_data["priority"],
                    status=ComplianceStatus.NOT_APPLICABLE,
                    evidence=[],
                    last_checked=datetime.now(),
                    next_check=datetime.now() + timedelta(days=1),
                    score=0.0,
                    notes=""
                )
                self.requirements[req_id] = requirement
            
            requirement = self.requirements[req_id]
            
            # Check if it's time to check this requirement
            if datetime.now() < requirement.next_check:
                return
            
            # Perform compliance check
            compliance_result = await self._perform_compliance_check(requirement)
            
            # Update requirement
            requirement.status = compliance_result["status"]
            requirement.score = compliance_result["score"]
            requirement.evidence = compliance_result["evidence"]
            requirement.last_checked = datetime.now()
            requirement.next_check = datetime.now() + timedelta(days=1)
            requirement.notes = compliance_result["notes"]
            
            # Save requirement
            await self._save_requirement(requirement)
            
        except Exception as e:
            logger.error(f"Error checking requirement {req_data['id']}: {e}")
    
    async def _perform_compliance_check(self, requirement: ComplianceRequirement) -> Dict[str, Any]:
        """Perform compliance check for a requirement"""
        try:
            # Use AI to analyze compliance
            analysis_text = f"""
            Compliance Requirement: {requirement.title}
            Description: {requirement.description}
            Category: {requirement.category}
            Priority: {requirement.priority}
            """
            
            # Get AI analysis
            ai_analysis = await self.ai_engine.detect_threat(analysis_text, "compliance_check")
            
            # Determine compliance status based on AI analysis and checks
            status = self._determine_compliance_status(requirement, ai_analysis)
            score = self._calculate_compliance_score(requirement, ai_analysis)
            evidence = self._gather_compliance_evidence(requirement)
            notes = self._generate_compliance_notes(requirement, ai_analysis)
            
            return {
                "status": status,
                "score": score,
                "evidence": evidence,
                "notes": notes
            }
            
        except Exception as e:
            logger.error(f"Error performing compliance check: {e}")
            return {
                "status": ComplianceStatus.NON_COMPLIANT,
                "score": 0.0,
                "evidence": [],
                "notes": f"Error during compliance check: {str(e)}"
            }
    
    def _determine_compliance_status(self, requirement: ComplianceRequirement, ai_analysis: Dict[str, Any]) -> ComplianceStatus:
        """Determine compliance status based on analysis"""
        try:
            # Simple heuristic - in reality, this would be more sophisticated
            confidence = ai_analysis.get("confidence", 0.5)
            threat_level = ai_analysis.get("threat_level", "unknown")
            
            if confidence > 0.8 and threat_level == "benign":
                return ComplianceStatus.COMPLIANT
            elif confidence > 0.6:
                return ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                return ComplianceStatus.NON_COMPLIANT
                
        except Exception:
            return ComplianceStatus.NON_COMPLIANT
    
    def _calculate_compliance_score(self, requirement: ComplianceRequirement, ai_analysis: Dict[str, Any]) -> float:
        """Calculate compliance score"""
        try:
            base_score = 0.5
            confidence = ai_analysis.get("confidence", 0.5)
            threat_level = ai_analysis.get("threat_level", "unknown")
            
            # Adjust score based on AI analysis
            if threat_level == "benign":
                base_score += 0.3
            elif threat_level == "suspicious":
                base_score += 0.1
            else:
                base_score -= 0.2
            
            # Adjust based on confidence
            base_score += (confidence - 0.5) * 0.4
            
            return max(0.0, min(1.0, base_score))
            
        except Exception:
            return 0.0
    
    def _gather_compliance_evidence(self, requirement: ComplianceRequirement) -> List[str]:
        """Gather evidence for compliance requirement"""
        evidence = []
        
        try:
            # This would gather actual evidence from various sources
            # For now, we'll simulate evidence gathering
            
            if "password" in requirement.title.lower():
                evidence.extend([
                    "Password policy document exists",
                    "Password complexity requirements enforced",
                    "Regular password audits conducted"
                ])
            elif "access" in requirement.title.lower():
                evidence.extend([
                    "Access control matrix documented",
                    "Regular access reviews conducted",
                    "Privileged access monitored"
                ])
            elif "inventory" in requirement.title.lower():
                evidence.extend([
                    "Asset inventory maintained",
                    "Asset classification documented",
                    "Asset ownership assigned"
                ])
            else:
                evidence.append("General compliance evidence")
            
            return evidence
            
        except Exception as e:
            logger.error(f"Error gathering compliance evidence: {e}")
            return ["Error gathering evidence"]
    
    def _generate_compliance_notes(self, requirement: ComplianceRequirement, ai_analysis: Dict[str, Any]) -> str:
        """Generate compliance notes"""
        try:
            notes = []
            
            # Add AI analysis insights
            if ai_analysis.get("threat_indicators"):
                notes.append(f"AI detected indicators: {', '.join(ai_analysis['threat_indicators'])}")
            
            # Add requirement-specific notes
            if requirement.priority == "high":
                notes.append("High priority requirement - requires immediate attention")
            
            if requirement.framework == ComplianceFramework.ISO27001:
                notes.append("ISO 27001 requirement - international standard")
            elif requirement.framework == ComplianceFramework.SOC2:
                notes.append("SOC 2 requirement - service organization control")
            elif requirement.framework == ComplianceFramework.PCI_DSS:
                notes.append("PCI DSS requirement - payment card industry standard")
            
            return "; ".join(notes) if notes else "No additional notes"
            
        except Exception as e:
            logger.error(f"Error generating compliance notes: {e}")
            return "Error generating notes"
    
    async def _generate_compliance_reports(self):
        """Generate compliance reports"""
        try:
            # Generate framework-specific reports
            for framework_name in self.frameworks.keys():
                await self._generate_framework_report(framework_name)
            
            # Generate overall compliance report
            await self._generate_overall_report()
            
        except Exception as e:
            logger.error(f"Error generating compliance reports: {e}")
    
    async def _generate_framework_report(self, framework_name: str):
        """Generate compliance report for a specific framework"""
        try:
            framework_requirements = [
                req for req in self.requirements.values()
                if req.framework.value == framework_name
            ]
            
            if not framework_requirements:
                return
            
            # Calculate overall score
            total_score = sum(req.score for req in framework_requirements)
            overall_score = total_score / len(framework_requirements) if framework_requirements else 0.0
            
            # Determine overall status
            if overall_score >= 0.8:
                status = ComplianceStatus.COMPLIANT
            elif overall_score >= 0.6:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            # Create assessment
            assessment = ComplianceAssessment(
                id=f"assess_{framework_name}_{int(datetime.now().timestamp())}",
                framework=ComplianceFramework(framework_name),
                assessment_date=datetime.now(),
                overall_score=overall_score,
                status=status,
                requirements=framework_requirements,
                findings=self._generate_findings(framework_requirements),
                recommendations=self._generate_recommendations(framework_requirements)
            )
            
            # Store assessment
            self.assessments[assessment.id] = assessment
            
            # Save assessment
            await self._save_assessment(assessment)
            
            logger.info(f"✅ Generated compliance report for {framework_name}")
            
        except Exception as e:
            logger.error(f"Error generating framework report for {framework_name}: {e}")
    
    async def _generate_overall_report(self):
        """Generate overall compliance report"""
        try:
            # Calculate overall compliance score
            all_requirements = list(self.requirements.values())
            if not all_requirements:
                return
            
            total_score = sum(req.score for req in all_requirements)
            overall_score = total_score / len(all_requirements)
            
            # Determine overall status
            if overall_score >= 0.8:
                status = ComplianceStatus.COMPLIANT
            elif overall_score >= 0.6:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            # Generate findings and recommendations
            findings = self._generate_findings(all_requirements)
            recommendations = self._generate_recommendations(all_requirements)
            
            # Create overall assessment
            assessment = ComplianceAssessment(
                id=f"assess_overall_{int(datetime.now().timestamp())}",
                framework=None,  # Overall assessment
                assessment_date=datetime.now(),
                overall_score=overall_score,
                status=status,
                requirements=all_requirements,
                findings=findings,
                recommendations=recommendations
            )
            
            # Store assessment
            self.assessments[assessment.id] = assessment
            
            # Save assessment
            await self._save_assessment(assessment)
            
            logger.info("✅ Generated overall compliance report")
            
        except Exception as e:
            logger.error(f"Error generating overall report: {e}")
    
    def _generate_findings(self, requirements: List[ComplianceRequirement]) -> List[Dict[str, Any]]:
        """Generate compliance findings"""
        findings = []
        
        try:
            # Group requirements by status
            by_status = {}
            for req in requirements:
                status = req.status.value
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(req)
            
            # Generate findings for each status
            for status, reqs in by_status.items():
                if status == "non_compliant":
                    findings.append({
                        "type": "non_compliance",
                        "count": len(reqs),
                        "description": f"{len(reqs)} requirements are non-compliant",
                        "requirements": [req.control_id for req in reqs]
                    })
                elif status == "partially_compliant":
                    findings.append({
                        "type": "partial_compliance",
                        "count": len(reqs),
                        "description": f"{len(reqs)} requirements are partially compliant",
                        "requirements": [req.control_id for req in reqs]
                    })
            
            return findings
            
        except Exception as e:
            logger.error(f"Error generating findings: {e}")
            return []
    
    def _generate_recommendations(self, requirements: List[ComplianceRequirement]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        try:
            # Analyze non-compliant requirements
            non_compliant = [req for req in requirements if req.status == ComplianceStatus.NON_COMPLIANT]
            
            if non_compliant:
                recommendations.append(f"Address {len(non_compliant)} non-compliant requirements immediately")
                
                # Framework-specific recommendations
                frameworks = set(req.framework for req in non_compliant)
                for framework in frameworks:
                    framework_reqs = [req for req in non_compliant if req.framework == framework]
                    recommendations.append(f"Focus on {framework.value.upper()} requirements: {len(framework_reqs)} items")
            
            # Priority-based recommendations
            high_priority = [req for req in requirements if req.priority == "high" and req.status != ComplianceStatus.COMPLIANT]
            if high_priority:
                recommendations.append(f"Prioritize {len(high_priority)} high-priority requirements")
            
            # General recommendations
            recommendations.extend([
                "Implement regular compliance monitoring",
                "Establish compliance training program",
                "Create compliance dashboard for management",
                "Automate compliance evidence collection"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    async def _update_compliance_scores(self):
        """Update compliance scores"""
        try:
            # This would update scores based on recent activities
            # For now, we'll just log the update
            logger.info("📊 Updated compliance scores")
            
        except Exception as e:
            logger.error(f"Error updating compliance scores: {e}")
    
    async def _save_requirement(self, requirement: ComplianceRequirement):
        """Save compliance requirement to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO compliance_requirements 
                (id, framework, control_id, title, description, category, priority, 
                 status, evidence, last_checked, next_check, score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                requirement.id, requirement.framework.value, requirement.control_id,
                requirement.title, requirement.description, requirement.category,
                requirement.priority, requirement.status.value, json.dumps(requirement.evidence),
                requirement.last_checked.isoformat(), requirement.next_check.isoformat(),
                requirement.score, requirement.notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save requirement: {e}")
    
    async def _save_assessment(self, assessment: ComplianceAssessment):
        """Save compliance assessment to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO compliance_assessments 
                (id, framework, assessment_date, overall_score, status, requirements, 
                 findings, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment.id, assessment.framework.value if assessment.framework else None,
                assessment.assessment_date.isoformat(), assessment.overall_score,
                assessment.status.value, json.dumps([req.id for req in assessment.requirements]),
                json.dumps(assessment.findings), json.dumps(assessment.recommendations)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save assessment: {e}")
    
    async def get_compliance_status(self, framework: str = None) -> Dict[str, Any]:
        """Get compliance status"""
        try:
            if framework:
                # Get status for specific framework
                framework_requirements = [
                    req for req in self.requirements.values()
                    if req.framework.value == framework
                ]
                
                if not framework_requirements:
                    return {"error": f"No requirements found for framework: {framework}"}
                
                total_score = sum(req.score for req in framework_requirements)
                overall_score = total_score / len(framework_requirements)
                
                return {
                    "framework": framework,
                    "overall_score": overall_score,
                    "total_requirements": len(framework_requirements),
                    "compliant": len([req for req in framework_requirements if req.status == ComplianceStatus.COMPLIANT]),
                    "non_compliant": len([req for req in framework_requirements if req.status == ComplianceStatus.NON_COMPLIANT]),
                    "partially_compliant": len([req for req in framework_requirements if req.status == ComplianceStatus.PARTIALLY_COMPLIANT])
                }
            else:
                # Get overall status
                all_requirements = list(self.requirements.values())
                if not all_requirements:
                    return {"error": "No requirements found"}
                
                total_score = sum(req.score for req in all_requirements)
                overall_score = total_score / len(all_requirements)
                
                return {
                    "overall_score": overall_score,
                    "total_requirements": len(all_requirements),
                    "compliant": len([req for req in all_requirements if req.status == ComplianceStatus.COMPLIANT]),
                    "non_compliant": len([req for req in all_requirements if req.status == ComplianceStatus.NON_COMPLIANT]),
                    "partially_compliant": len([req for req in all_requirements if req.status == ComplianceStatus.PARTIALLY_COMPLIANT]),
                    "frameworks": list(set(req.framework.value for req in all_requirements))
                }
                
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            return {"error": str(e)}
    
    def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.monitoring = False
        logger.info("🛑 Stopped compliance monitoring")