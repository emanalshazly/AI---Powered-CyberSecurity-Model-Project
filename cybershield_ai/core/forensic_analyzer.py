"""
Advanced Forensic Analysis System
Automated digital forensics and evidence collection
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
import hashlib
import mimetypes
import subprocess
import os

from core.config import settings
from core.ai_engine import AIEngine

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    MALWARE = "malware"
    NETWORK = "network"
    MEMORY = "memory"
    DISK = "disk"
    LOG = "log"
    EMAIL = "email"

class EvidenceType(Enum):
    FILE = "file"
    MEMORY_DUMP = "memory_dump"
    NETWORK_CAPTURE = "network_capture"
    LOG_ENTRY = "log_entry"
    REGISTRY_KEY = "registry_key"
    PROCESS = "process"

@dataclass
class ForensicEvidence:
    """Forensic evidence data structure"""
    id: str
    evidence_type: EvidenceType
    source: str
    description: str
    hash_md5: str
    hash_sha1: str
    hash_sha256: str
    file_size: int
    mime_type: str
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    metadata: Dict[str, Any]
    analysis_results: Dict[str, Any]

@dataclass
class ForensicAnalysis:
    """Forensic analysis data structure"""
    id: str
    analysis_type: AnalysisType
    evidence: List[ForensicEvidence]
    findings: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]
    status: str
    confidence: float
    ai_analysis: Dict[str, Any]

class ForensicAnalyzer:
    """
    Advanced Forensic Analysis System
    Automated digital forensics and evidence collection
    """
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.analyses = {}
        self.evidence = {}
        self.analysis_queue = []
        
        # Initialize database
        self._init_database()
        
        # Initialize analysis tools
        self._init_analysis_tools()
        
        # Initialize artifact patterns
        self._init_artifact_patterns()
    
    def _init_database(self):
        """Initialize forensic analysis database"""
        try:
            self.db_path = Path("data/forensic_analysis.db")
            self.db_path.parent.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create evidence table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forensic_evidence (
                    id TEXT PRIMARY KEY,
                    evidence_type TEXT,
                    source TEXT,
                    description TEXT,
                    hash_md5 TEXT,
                    hash_sha1 TEXT,
                    hash_sha256 TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    created_at TIMESTAMP,
                    modified_at TIMESTAMP,
                    accessed_at TIMESTAMP,
                    metadata TEXT,
                    analysis_results TEXT
                )
            """)
            
            # Create analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forensic_analyses (
                    id TEXT PRIMARY KEY,
                    analysis_type TEXT,
                    evidence TEXT,
                    findings TEXT,
                    timeline TEXT,
                    artifacts TEXT,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT,
                    confidence REAL,
                    ai_analysis TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Forensic analysis database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize forensic database: {e}")
    
    def _init_analysis_tools(self):
        """Initialize forensic analysis tools"""
        try:
            self.analysis_tools = {
                "file_analysis": {
                    "file": "file",
                    "description": "File type analysis"
                },
                "hash_analysis": {
                    "file": "md5sum",
                    "description": "Hash calculation"
                },
                "strings_analysis": {
                    "file": "strings",
                    "description": "String extraction"
                },
                "hex_analysis": {
                    "file": "hexdump",
                    "description": "Hexadecimal analysis"
                }
            }
            
            # Check tool availability
            for tool_name, tool_info in self.analysis_tools.items():
                try:
                    subprocess.run([tool_info["file"], "--version"], 
                                 capture_output=True, check=True)
                    tool_info["available"] = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    tool_info["available"] = False
                    logger.warning(f"Tool {tool_name} not available")
            
            logger.info("✅ Forensic analysis tools initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analysis tools: {e}")
    
    def _init_artifact_patterns(self):
        """Initialize forensic artifact patterns"""
        try:
            self.artifact_patterns = {
                "malware_indicators": [
                    "CreateRemoteThread",
                    "VirtualAllocEx",
                    "WriteProcessMemory",
                    "LoadLibrary",
                    "GetProcAddress",
                    "RegSetValueEx",
                    "CreateService",
                    "ShellExecute"
                ],
                "network_indicators": [
                    "socket",
                    "connect",
                    "send",
                    "recv",
                    "bind",
                    "listen",
                    "accept"
                ],
                "persistence_indicators": [
                    "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                    "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
                ],
                "suspicious_strings": [
                    "cmd.exe",
                    "powershell",
                    "wscript",
                    "cscript",
                    "rundll32",
                    "regsvr32",
                    "mshta",
                    "certutil"
                ]
            }
            
            logger.info("✅ Forensic artifact patterns initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize artifact patterns: {e}")
    
    async def analyze_file(self, file_path: str, analysis_type: AnalysisType = AnalysisType.MALWARE) -> str:
        """Analyze a file for forensic evidence"""
        try:
            analysis_id = f"forensic_{int(datetime.now().timestamp())}"
            
            # Create analysis record
            analysis = ForensicAnalysis(
                id=analysis_id,
                analysis_type=analysis_type,
                evidence=[],
                findings=[],
                timeline=[],
                artifacts=[],
                created_at=datetime.now(),
                completed_at=None,
                status="processing",
                confidence=0.0,
                ai_analysis={}
            )
            
            # Add to queue
            self.analysis_queue.append(analysis)
            
            # Start analysis in background
            asyncio.create_task(self._process_analysis(analysis, file_path))
            
            logger.info(f"✅ Started forensic analysis: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"Error starting forensic analysis: {e}")
            raise
    
    async def _process_analysis(self, analysis: ForensicAnalysis, file_path: str):
        """Process forensic analysis"""
        try:
            # Collect evidence
            evidence = await self._collect_evidence(file_path)
            analysis.evidence = evidence
            
            # Analyze evidence
            findings = await self._analyze_evidence(evidence, analysis.analysis_type)
            analysis.findings = findings
            
            # Generate timeline
            timeline = await self._generate_timeline(evidence, findings)
            analysis.timeline = timeline
            
            # Extract artifacts
            artifacts = await self._extract_artifacts(evidence, analysis.analysis_type)
            analysis.artifacts = artifacts
            
            # AI analysis
            ai_analysis = await self._perform_ai_analysis(analysis)
            analysis.ai_analysis = ai_analysis
            
            # Calculate confidence
            analysis.confidence = self._calculate_confidence(analysis)
            
            # Complete analysis
            analysis.status = "completed"
            analysis.completed_at = datetime.now()
            
            # Store analysis
            self.analyses[analysis.id] = analysis
            
            # Save to database
            await self._save_analysis(analysis)
            
            logger.info(f"✅ Completed forensic analysis: {analysis.id}")
            
        except Exception as e:
            logger.error(f"Error processing forensic analysis: {e}")
            analysis.status = "failed"
            analysis.completed_at = datetime.now()
    
    async def _collect_evidence(self, file_path: str) -> List[ForensicEvidence]:
        """Collect forensic evidence from file"""
        evidence_list = []
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file stats
            stat = os.stat(file_path)
            
            # Calculate hashes
            hashes = await self._calculate_hashes(file_path)
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Create evidence record
            evidence = ForensicEvidence(
                id=f"evidence_{int(datetime.now().timestamp())}",
                evidence_type=EvidenceType.FILE,
                source=file_path,
                description=f"File evidence: {os.path.basename(file_path)}",
                hash_md5=hashes["md5"],
                hash_sha1=hashes["sha1"],
                hash_sha256=hashes["sha256"],
                file_size=stat.st_size,
                mime_type=mime_type,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                accessed_at=datetime.fromtimestamp(stat.st_atime),
                metadata={
                    "permissions": oct(stat.st_mode),
                    "inode": stat.st_ino,
                    "device": stat.st_dev
                },
                analysis_results={}
            )
            
            evidence_list.append(evidence)
            
            # Store evidence
            self.evidence[evidence.id] = evidence
            
            # Save evidence
            await self._save_evidence(evidence)
            
            return evidence_list
            
        except Exception as e:
            logger.error(f"Error collecting evidence: {e}")
            return []
    
    async def _calculate_hashes(self, file_path: str) -> Dict[str, str]:
        """Calculate file hashes"""
        try:
            hashes = {"md5": "", "sha1": "", "sha256": ""}
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            hashes["md5"] = hashlib.md5(content).hexdigest()
            hashes["sha1"] = hashlib.sha1(content).hexdigest()
            hashes["sha256"] = hashlib.sha256(content).hexdigest()
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error calculating hashes: {e}")
            return {"md5": "", "sha1": "", "sha256": ""}
    
    async def _analyze_evidence(self, evidence: List[ForensicEvidence], analysis_type: AnalysisType) -> List[Dict[str, Any]]:
        """Analyze forensic evidence"""
        findings = []
        
        try:
            for ev in evidence:
                # File analysis
                file_findings = await self._analyze_file(ev)
                findings.extend(file_findings)
                
                # Type-specific analysis
                if analysis_type == AnalysisType.MALWARE:
                    malware_findings = await self._analyze_malware(ev)
                    findings.extend(malware_findings)
                elif analysis_type == AnalysisType.NETWORK:
                    network_findings = await self._analyze_network(ev)
                    findings.extend(network_findings)
                elif analysis_type == AnalysisType.MEMORY:
                    memory_findings = await self._analyze_memory(ev)
                    findings.extend(memory_findings)
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing evidence: {e}")
            return []
    
    async def _analyze_file(self, evidence: ForensicEvidence) -> List[Dict[str, Any]]:
        """Analyze file evidence"""
        findings = []
        
        try:
            # Basic file analysis
            findings.append({
                "type": "file_info",
                "description": f"File: {evidence.source}",
                "size": evidence.file_size,
                "mime_type": evidence.mime_type,
                "hashes": {
                    "md5": evidence.hash_md5,
                    "sha1": evidence.hash_sha1,
                    "sha256": evidence.hash_sha256
                }
            })
            
            # Check for suspicious patterns
            if evidence.mime_type in ["application/x-executable", "application/x-msdownload"]:
                findings.append({
                    "type": "suspicious_file",
                    "description": "Executable file detected",
                    "severity": "medium",
                    "confidence": 0.7
                })
            
            # Check file size
            if evidence.file_size > 100 * 1024 * 1024:  # 100MB
                findings.append({
                    "type": "large_file",
                    "description": f"Large file detected: {evidence.file_size} bytes",
                    "severity": "low",
                    "confidence": 0.9
                })
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return []
    
    async def _analyze_malware(self, evidence: ForensicEvidence) -> List[Dict[str, Any]]:
        """Analyze evidence for malware indicators"""
        findings = []
        
        try:
            # This would perform actual malware analysis
            # For now, we'll simulate some checks
            
            # Check file extension
            file_ext = os.path.splitext(evidence.source)[1].lower()
            suspicious_extensions = ['.exe', '.dll', '.scr', '.bat', '.cmd', '.ps1', '.vbs']
            
            if file_ext in suspicious_extensions:
                findings.append({
                    "type": "suspicious_extension",
                    "description": f"Suspicious file extension: {file_ext}",
                    "severity": "medium",
                    "confidence": 0.6
                })
            
            # Check for known malware hashes (simplified)
            known_malware_hashes = [
                "d41d8cd98f00b204e9800998ecf8427e",  # Example MD5
                "da39a3ee5e6b4b0d3255bfef95601890afd80709"  # Example SHA1
            ]
            
            if evidence.hash_md5 in known_malware_hashes or evidence.hash_sha1 in known_malware_hashes:
                findings.append({
                    "type": "known_malware",
                    "description": "File matches known malware hash",
                    "severity": "critical",
                    "confidence": 0.95
                })
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing malware: {e}")
            return []
    
    async def _analyze_network(self, evidence: ForensicEvidence) -> List[Dict[str, Any]]:
        """Analyze evidence for network indicators"""
        findings = []
        
        try:
            # This would analyze network captures
            # For now, we'll simulate some checks
            
            findings.append({
                "type": "network_analysis",
                "description": "Network capture analysis completed",
                "severity": "info",
                "confidence": 0.8
            })
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing network: {e}")
            return []
    
    async def _analyze_memory(self, evidence: ForensicEvidence) -> List[Dict[str, Any]]:
        """Analyze evidence for memory artifacts"""
        findings = []
        
        try:
            # This would analyze memory dumps
            # For now, we'll simulate some checks
            
            findings.append({
                "type": "memory_analysis",
                "description": "Memory dump analysis completed",
                "severity": "info",
                "confidence": 0.8
            })
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing memory: {e}")
            return []
    
    async def _generate_timeline(self, evidence: List[ForensicEvidence], findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate forensic timeline"""
        timeline = []
        
        try:
            # Add evidence events
            for ev in evidence:
                timeline.append({
                    "timestamp": ev.created_at.isoformat(),
                    "event": "evidence_created",
                    "description": f"Evidence collected: {ev.description}",
                    "source": ev.source
                })
            
            # Add finding events
            for finding in findings:
                timeline.append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "finding_discovered",
                    "description": finding.get("description", "Finding discovered"),
                    "severity": finding.get("severity", "unknown")
                })
            
            # Sort timeline by timestamp
            timeline.sort(key=lambda x: x["timestamp"])
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error generating timeline: {e}")
            return []
    
    async def _extract_artifacts(self, evidence: List[ForensicEvidence], analysis_type: AnalysisType) -> List[Dict[str, Any]]:
        """Extract forensic artifacts"""
        artifacts = []
        
        try:
            for ev in evidence:
                # Extract strings
                strings = await self._extract_strings(ev.source)
                if strings:
                    artifacts.append({
                        "type": "strings",
                        "evidence_id": ev.id,
                        "data": strings[:100],  # Limit to first 100 strings
                        "count": len(strings)
                    })
                
                # Extract metadata
                metadata = await self._extract_metadata(ev.source)
                if metadata:
                    artifacts.append({
                        "type": "metadata",
                        "evidence_id": ev.id,
                        "data": metadata
                    })
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Error extracting artifacts: {e}")
            return []
    
    async def _extract_strings(self, file_path: str) -> List[str]:
        """Extract strings from file"""
        try:
            if not self.analysis_tools["strings_analysis"]["available"]:
                return []
            
            result = subprocess.run(
                ["strings", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error extracting strings: {e}")
            return []
    
    async def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        try:
            if not self.analysis_tools["file_analysis"]["available"]:
                return {}
            
            result = subprocess.run(
                ["file", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "file_type": result.stdout.strip(),
                    "extracted_at": datetime.now().isoformat()
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    async def _perform_ai_analysis(self, analysis: ForensicAnalysis) -> Dict[str, Any]:
        """Perform AI analysis on forensic data"""
        try:
            # Prepare data for AI analysis
            analysis_text = f"""
            Forensic Analysis: {analysis.id}
            Type: {analysis.analysis_type.value}
            Evidence Count: {len(analysis.evidence)}
            Findings Count: {len(analysis.findings)}
            Artifacts Count: {len(analysis.artifacts)}
            """
            
            # Use AI engine for analysis
            ai_result = await self.ai_engine.detect_threat(analysis_text, "forensic_analysis")
            
            # Generate additional analysis
            analysis_result = {
                "threat_level": ai_result.get("threat_level", "unknown"),
                "confidence": ai_result.get("confidence", 0.5),
                "threat_indicators": ai_result.get("threat_indicators", []),
                "recommendations": self._generate_forensic_recommendations(analysis),
                "risk_assessment": self._assess_forensic_risk(analysis)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error performing AI analysis: {e}")
            return {"error": str(e)}
    
    def _generate_forensic_recommendations(self, analysis: ForensicAnalysis) -> List[str]:
        """Generate forensic recommendations"""
        recommendations = []
        
        try:
            # Based on findings
            critical_findings = [f for f in analysis.findings if f.get("severity") == "critical"]
            if critical_findings:
                recommendations.append("Immediate containment required - critical findings detected")
            
            # Based on analysis type
            if analysis.analysis_type == AnalysisType.MALWARE:
                recommendations.extend([
                    "Isolate affected systems",
                    "Collect additional memory dumps",
                    "Analyze network traffic",
                    "Update antivirus signatures"
                ])
            elif analysis.analysis_type == AnalysisType.NETWORK:
                recommendations.extend([
                    "Monitor network traffic",
                    "Check firewall logs",
                    "Analyze DNS queries",
                    "Review network policies"
                ])
            
            # General recommendations
            recommendations.extend([
                "Preserve evidence chain of custody",
                "Document all findings",
                "Notify incident response team",
                "Conduct additional analysis if needed"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def _assess_forensic_risk(self, analysis: ForensicAnalysis) -> Dict[str, Any]:
        """Assess forensic risk"""
        try:
            risk_score = 0.0
            
            # Base risk from findings
            for finding in analysis.findings:
                severity = finding.get("severity", "low")
                if severity == "critical":
                    risk_score += 0.3
                elif severity == "high":
                    risk_score += 0.2
                elif severity == "medium":
                    risk_score += 0.1
            
            # Risk from evidence count
            if len(analysis.evidence) > 10:
                risk_score += 0.1
            
            # Risk from artifacts
            if len(analysis.artifacts) > 5:
                risk_score += 0.1
            
            risk_level = "low"
            if risk_score > 0.7:
                risk_level = "high"
            elif risk_score > 0.4:
                risk_level = "medium"
            
            return {
                "risk_score": min(risk_score, 1.0),
                "risk_level": risk_level,
                "factors": [
                    f"{len(analysis.findings)} findings",
                    f"{len(analysis.evidence)} evidence items",
                    f"{len(analysis.artifacts)} artifacts"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error assessing forensic risk: {e}")
            return {"risk_score": 0.0, "risk_level": "unknown", "factors": []}
    
    def _calculate_confidence(self, analysis: ForensicAnalysis) -> float:
        """Calculate analysis confidence"""
        try:
            base_confidence = 0.5
            
            # Confidence from evidence quality
            if analysis.evidence:
                base_confidence += 0.2
            
            # Confidence from findings
            if analysis.findings:
                base_confidence += 0.2
            
            # Confidence from artifacts
            if analysis.artifacts:
                base_confidence += 0.1
            
            return min(base_confidence, 1.0)
            
        except Exception:
            return 0.5
    
    async def _save_evidence(self, evidence: ForensicEvidence):
        """Save forensic evidence to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO forensic_evidence 
                (id, evidence_type, source, description, hash_md5, hash_sha1, hash_sha256,
                 file_size, mime_type, created_at, modified_at, accessed_at, metadata, analysis_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evidence.id, evidence.evidence_type.value, evidence.source, evidence.description,
                evidence.hash_md5, evidence.hash_sha1, evidence.hash_sha256, evidence.file_size,
                evidence.mime_type, evidence.created_at.isoformat(), evidence.modified_at.isoformat(),
                evidence.accessed_at.isoformat(), json.dumps(evidence.metadata),
                json.dumps(evidence.analysis_results)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save evidence: {e}")
    
    async def _save_analysis(self, analysis: ForensicAnalysis):
        """Save forensic analysis to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO forensic_analyses 
                (id, analysis_type, evidence, findings, timeline, artifacts, created_at,
                 completed_at, status, confidence, ai_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.id, analysis.analysis_type.value, json.dumps([ev.id for ev in analysis.evidence]),
                json.dumps(analysis.findings), json.dumps(analysis.timeline), json.dumps(analysis.artifacts),
                analysis.created_at.isoformat(), analysis.completed_at.isoformat() if analysis.completed_at else None,
                analysis.status, analysis.confidence, json.dumps(analysis.ai_analysis)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get forensic analysis results"""
        try:
            if analysis_id not in self.analyses:
                return None
            
            analysis = self.analyses[analysis_id]
            
            return {
                "id": analysis.id,
                "analysis_type": analysis.analysis_type.value,
                "evidence": [
                    {
                        "id": ev.id,
                        "type": ev.evidence_type.value,
                        "source": ev.source,
                        "description": ev.description,
                        "hashes": {
                            "md5": ev.hash_md5,
                            "sha1": ev.hash_sha1,
                            "sha256": ev.hash_sha256
                        },
                        "file_size": ev.file_size,
                        "mime_type": ev.mime_type
                    }
                    for ev in analysis.evidence
                ],
                "findings": analysis.findings,
                "timeline": analysis.timeline,
                "artifacts": analysis.artifacts,
                "created_at": analysis.created_at.isoformat(),
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                "status": analysis.status,
                "confidence": analysis.confidence,
                "ai_analysis": analysis.ai_analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis {analysis_id}: {e}")
            return None
    
    async def get_analyses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of forensic analyses"""
        try:
            analyses = []
            for analysis in list(self.analyses.values())[:limit]:
                analyses.append({
                    "id": analysis.id,
                    "analysis_type": analysis.analysis_type.value,
                    "evidence_count": len(analysis.evidence),
                    "findings_count": len(analysis.findings),
                    "created_at": analysis.created_at.isoformat(),
                    "status": analysis.status,
                    "confidence": analysis.confidence
                })
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error getting analyses: {e}")
            return []