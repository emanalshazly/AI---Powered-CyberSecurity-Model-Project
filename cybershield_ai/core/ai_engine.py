"""
AI Engine - Core AI capabilities for CyberShield AI
Combines multiple free AI models for comprehensive threat analysis
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import numpy as np
import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, AutoModelForCausalLM
)
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import cv2
from PIL import Image
import requests
from sentence_transformers import SentenceTransformer
import spacy
from textblob import TextBlob
import yara

from core.config import settings

logger = logging.getLogger(__name__)

class AIEngine:
    """
    Revolutionary AI Engine that combines multiple free AI models
    for comprehensive cybersecurity analysis
    """
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models_path = Path(settings.AI_MODELS_PATH)
        self.models_path.mkdir(exist_ok=True)
        
        # Initialize model configurations
        self.model_configs = {
            "vulnerability_classifier": {
                "model_name": "microsoft/DialoGPT-medium",
                "task": "text-classification",
                "description": "Classifies vulnerabilities and security issues"
            },
            "threat_detector": {
                "model_name": "distilbert-base-uncased",
                "task": "text-classification",
                "description": "Detects threats in text and logs"
            },
            "malware_analyzer": {
                "model_name": "bert-base-uncased",
                "task": "text-classification",
                "description": "Analyzes malware characteristics"
            },
            "anomaly_detector": {
                "model_name": "isolation_forest",
                "task": "anomaly_detection",
                "description": "Detects anomalies in system behavior"
            },
            "nlp_analyzer": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "task": "feature-extraction",
                "description": "Natural language processing for security reports"
            },
            "computer_vision": {
                "model_name": "yolov8n",
                "task": "object-detection",
                "description": "Visual analysis of network traffic and system states"
            },
            "code_analyzer": {
                "model_name": "microsoft/codebert-base",
                "task": "text-classification",
                "description": "Analyzes code for security vulnerabilities"
            },
            "threat_intelligence": {
                "model_name": "facebook/bart-large",
                "task": "text-generation",
                "description": "Generates threat intelligence reports"
            }
        }
        
        # YARA rules for malware detection
        self.yara_rules = None
        
    async def initialize(self):
        """Initialize all AI models"""
        logger.info("🧠 Initializing AI Engine...")
        
        try:
            # Load models in parallel for faster startup
            tasks = [
                self._load_vulnerability_classifier(),
                self._load_threat_detector(),
                self._load_malware_analyzer(),
                self._load_nlp_analyzer(),
                self._load_code_analyzer(),
                self._load_threat_intelligence(),
                self._load_yara_rules(),
                self._initialize_anomaly_detector()
            ]
            
            await asyncio.gather(*tasks)
            
            logger.info("✅ AI Engine initialized successfully")
            logger.info(f"📊 Loaded {len(self.models)} AI models")
            logger.info(f"🔧 Device: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Engine: {e}")
            raise
    
    async def _load_vulnerability_classifier(self):
        """Load vulnerability classification model"""
        try:
            model_name = self.model_configs["vulnerability_classifier"]["model_name"]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=5  # Critical, High, Medium, Low, Info
            )
            
            self.models["vulnerability_classifier"] = model
            self.tokenizers["vulnerability_classifier"] = tokenizer
            
            logger.info("✅ Vulnerability classifier loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load vulnerability classifier: {e}")
    
    async def _load_threat_detector(self):
        """Load threat detection model"""
        try:
            model_name = self.model_configs["threat_detector"]["model_name"]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=3  # Benign, Suspicious, Malicious
            )
            
            self.models["threat_detector"] = model
            self.tokenizers["threat_detector"] = tokenizer
            
            logger.info("✅ Threat detector loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load threat detector: {e}")
    
    async def _load_malware_analyzer(self):
        """Load malware analysis model"""
        try:
            model_name = self.model_configs["malware_analyzer"]["model_name"]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=10  # Different malware families
            )
            
            self.models["malware_analyzer"] = model
            self.tokenizers["malware_analyzer"] = tokenizer
            
            logger.info("✅ Malware analyzer loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load malware analyzer: {e}")
    
    async def _load_nlp_analyzer(self):
        """Load NLP analysis model"""
        try:
            model_name = self.model_configs["nlp_analyzer"]["model_name"]
            model = SentenceTransformer(model_name)
            
            self.models["nlp_analyzer"] = model
            
            # Load spaCy model for advanced NLP
            try:
                nlp = spacy.load("en_core_web_sm")
                self.models["spacy_nlp"] = nlp
            except OSError:
                logger.warning("⚠️ spaCy model not found, using basic NLP")
            
            logger.info("✅ NLP analyzer loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load NLP analyzer: {e}")
    
    async def _load_code_analyzer(self):
        """Load code analysis model"""
        try:
            model_name = self.model_configs["code_analyzer"]["model_name"]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=7  # Different vulnerability types
            )
            
            self.models["code_analyzer"] = model
            self.tokenizers["code_analyzer"] = tokenizer
            
            logger.info("✅ Code analyzer loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load code analyzer: {e}")
    
    async def _load_threat_intelligence(self):
        """Load threat intelligence model"""
        try:
            model_name = self.model_configs["threat_intelligence"]["model_name"]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            self.models["threat_intelligence"] = model
            self.tokenizers["threat_intelligence"] = tokenizer
            
            logger.info("✅ Threat intelligence model loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load threat intelligence model: {e}")
    
    async def _load_yara_rules(self):
        """Load YARA rules for malware detection"""
        try:
            # Create basic YARA rules
            yara_rules = """
            rule SuspiciousFile {
                strings:
                    $s1 = "cmd.exe" nocase
                    $s2 = "powershell" nocase
                    $s3 = "wscript" nocase
                    $s4 = "cscript" nocase
                condition:
                    2 of them
            }
            
            rule MalwareIndicators {
                strings:
                    $s1 = "CreateRemoteThread" nocase
                    $s2 = "VirtualAllocEx" nocase
                    $s3 = "WriteProcessMemory" nocase
                    $s4 = "LoadLibrary" nocase
                condition:
                    3 of them
            }
            """
            
            self.yara_rules = yara.compile(source=yara_rules)
            logger.info("✅ YARA rules loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load YARA rules: {e}")
    
    async def _initialize_anomaly_detector(self):
        """Initialize anomaly detection models"""
        try:
            # Isolation Forest for anomaly detection
            self.models["anomaly_detector"] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # DBSCAN for clustering
            self.models["clustering"] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            logger.info("✅ Anomaly detection models initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize anomaly detector: {e}")
    
    async def analyze_vulnerability(self, description: str, cve_id: str = None) -> Dict[str, Any]:
        """Analyze vulnerability using AI"""
        try:
            if "vulnerability_classifier" not in self.models:
                return {"error": "Vulnerability classifier not available"}
            
            model = self.models["vulnerability_classifier"]
            tokenizer = self.tokenizers["vulnerability_classifier"]
            
            # Prepare input
            inputs = tokenizer(
                description,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Get prediction
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = predictions[0][predicted_class].item()
            
            # Map to severity levels
            severity_map = {0: "Critical", 1: "High", 2: "Medium", 3: "Low", 4: "Info"}
            severity = severity_map.get(predicted_class, "Unknown")
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(description, severity, cve_id)
            
            return {
                "severity": severity,
                "confidence": confidence,
                "risk_score": risk_score,
                "cve_id": cve_id,
                "description": description,
                "ai_analysis": {
                    "model_used": "vulnerability_classifier",
                    "prediction_confidence": confidence,
                    "risk_factors": self._extract_risk_factors(description)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing vulnerability: {e}")
            return {"error": str(e)}
    
    async def detect_threat(self, text: str, context: str = None) -> Dict[str, Any]:
        """Detect threats in text using AI"""
        try:
            if "threat_detector" not in self.models:
                return {"error": "Threat detector not available"}
            
            model = self.models["threat_detector"]
            tokenizer = self.tokenizers["threat_detector"]
            
            # Prepare input
            input_text = f"{context}: {text}" if context else text
            inputs = tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Get prediction
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = predictions[0][predicted_class].item()
            
            # Map to threat levels
            threat_map = {0: "Benign", 1: "Suspicious", 2: "Malicious"}
            threat_level = threat_map.get(predicted_class, "Unknown")
            
            # Additional analysis
            sentiment = self._analyze_sentiment(text)
            entities = self._extract_entities(text)
            
            return {
                "threat_level": threat_level,
                "confidence": confidence,
                "sentiment": sentiment,
                "entities": entities,
                "text": text,
                "ai_analysis": {
                    "model_used": "threat_detector",
                    "prediction_confidence": confidence,
                    "threat_indicators": self._extract_threat_indicators(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting threat: {e}")
            return {"error": str(e)}
    
    async def analyze_malware(self, file_path: str, file_content: bytes = None) -> Dict[str, Any]:
        """Analyze malware using AI and YARA rules"""
        try:
            results = {
                "file_path": file_path,
                "yara_matches": [],
                "ai_analysis": {},
                "risk_score": 0.0
            }
            
            # YARA analysis
            if self.yara_rules and file_content:
                matches = self.yara_rules.match(data=file_content)
                results["yara_matches"] = [str(match) for match in matches]
            
            # AI analysis if we have text content
            if file_content and "malware_analyzer" in self.models:
                # Convert bytes to text (basic approach)
                try:
                    text_content = file_content.decode('utf-8', errors='ignore')
                    model = self.models["malware_analyzer"]
                    tokenizer = self.tokenizers["malware_analyzer"]
                    
                    inputs = tokenizer(
                        text_content[:1000],  # Limit to first 1000 chars
                        return_tensors="pt",
                        truncation=True,
                        padding=True,
                        max_length=512
                    )
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                        predicted_class = torch.argmax(predictions, dim=-1).item()
                        confidence = predictions[0][predicted_class].item()
                    
                    malware_families = [
                        "Trojan", "Virus", "Worm", "Rootkit", "Backdoor",
                        "Ransomware", "Spyware", "Adware", "Botnet", "Other"
                    ]
                    
                    results["ai_analysis"] = {
                        "predicted_family": malware_families[predicted_class],
                        "confidence": confidence,
                        "model_used": "malware_analyzer"
                    }
                    
                except Exception as e:
                    logger.warning(f"AI malware analysis failed: {e}")
            
            # Calculate overall risk score
            risk_score = 0.0
            if results["yara_matches"]:
                risk_score += 0.5
            if results["ai_analysis"].get("confidence", 0) > 0.7:
                risk_score += 0.5
            
            results["risk_score"] = min(risk_score, 1.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing malware: {e}")
            return {"error": str(e)}
    
    async def detect_anomalies(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect anomalies in system data"""
        try:
            if "anomaly_detector" not in self.models:
                return {"error": "Anomaly detector not available"}
            
            # Convert data to feature matrix
            features = self._extract_features(data)
            
            if len(features) < 2:
                return {"anomalies": [], "message": "Insufficient data for anomaly detection"}
            
            # Fit and predict anomalies
            anomaly_detector = self.models["anomaly_detector"]
            anomaly_detector.fit(features)
            predictions = anomaly_detector.predict(features)
            anomaly_scores = anomaly_detector.decision_function(features)
            
            # Identify anomalies
            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
                if pred == -1:  # Anomaly
                    anomalies.append({
                        "index": i,
                        "data_point": data[i],
                        "anomaly_score": float(score),
                        "severity": "High" if score < -0.5 else "Medium"
                    })
            
            return {
                "anomalies": anomalies,
                "total_anomalies": len(anomalies),
                "anomaly_rate": len(anomalies) / len(data),
                "model_used": "isolation_forest"
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"error": str(e)}
    
    async def generate_threat_intelligence(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate threat intelligence report using AI"""
        try:
            if "threat_intelligence" not in self.models:
                return {"error": "Threat intelligence model not available"}
            
            model = self.models["threat_intelligence"]
            tokenizer = self.tokenizers["threat_intelligence"]
            
            # Prepare prompt
            prompt = f"""
            Generate a comprehensive threat intelligence report based on the following data:
            
            Threat Type: {threat_data.get('type', 'Unknown')}
            Source IP: {threat_data.get('source_ip', 'Unknown')}
            Target: {threat_data.get('target', 'Unknown')}
            Description: {threat_data.get('description', 'No description')}
            
            Please provide:
            1. Threat assessment
            2. Risk level
            3. Recommended actions
            4. Indicators of compromise
            5. Mitigation strategies
            """
            
            # Generate response
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "threat_intelligence_report": generated_text,
                "generated_at": "2024-01-15T10:30:00Z",
                "model_used": "threat_intelligence",
                "input_data": threat_data
            }
            
        except Exception as e:
            logger.error(f"Error generating threat intelligence: {e}")
            return {"error": str(e)}
    
    def _calculate_risk_score(self, description: str, severity: str, cve_id: str = None) -> float:
        """Calculate risk score based on multiple factors"""
        risk_score = 0.0
        
        # Base score from severity
        severity_scores = {"Critical": 0.9, "High": 0.7, "Medium": 0.5, "Low": 0.3, "Info": 0.1}
        risk_score += severity_scores.get(severity, 0.5)
        
        # Keywords that increase risk
        high_risk_keywords = ["remote", "code execution", "privilege escalation", "buffer overflow", "sql injection"]
        for keyword in high_risk_keywords:
            if keyword.lower() in description.lower():
                risk_score += 0.1
        
        # CVE age factor (newer CVEs are riskier)
        if cve_id and "CVE-" in cve_id:
            year = cve_id.split("-")[1]
            if year.isdigit():
                current_year = 2024
                age = current_year - int(year)
                risk_score += max(0, (5 - age) * 0.05)  # Newer CVEs get higher score
        
        return min(risk_score, 1.0)
    
    def _extract_risk_factors(self, description: str) -> List[str]:
        """Extract risk factors from vulnerability description"""
        risk_factors = []
        
        risk_patterns = {
            "remote_code_execution": ["remote", "code execution", "rce"],
            "privilege_escalation": ["privilege escalation", "elevation"],
            "information_disclosure": ["information disclosure", "leak", "exposure"],
            "denial_of_service": ["denial of service", "dos", "crash"],
            "authentication_bypass": ["authentication bypass", "auth bypass"]
        }
        
        description_lower = description.lower()
        for factor, patterns in risk_patterns.items():
            if any(pattern in description_lower for pattern in patterns):
                risk_factors.append(factor)
        
        return risk_factors
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                "polarity": sentiment.polarity,  # -1 to 1
                "subjectivity": sentiment.subjectivity,  # 0 to 1
                "classification": "positive" if sentiment.polarity > 0.1 else "negative" if sentiment.polarity < -0.1 else "neutral"
            }
        except Exception:
            return {"polarity": 0, "subjectivity": 0, "classification": "neutral"}
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text"""
        try:
            if "spacy_nlp" in self.models:
                nlp = self.models["spacy_nlp"]
                doc = nlp(text)
                return [
                    {"text": ent.text, "label": ent.label_, "confidence": 1.0}
                    for ent in doc.ents
                ]
            else:
                # Basic entity extraction
                import re
                entities = []
                
                # IP addresses
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                for match in re.finditer(ip_pattern, text):
                    entities.append({"text": match.group(), "label": "IP_ADDRESS", "confidence": 0.9})
                
                # URLs
                url_pattern = r'https?://[^\s]+'
                for match in re.finditer(url_pattern, text):
                    entities.append({"text": match.group(), "label": "URL", "confidence": 0.9})
                
                return entities
                
        except Exception:
            return []
    
    def _extract_threat_indicators(self, text: str) -> List[str]:
        """Extract threat indicators from text"""
        indicators = []
        
        threat_patterns = {
            "malware": ["malware", "virus", "trojan", "worm", "rootkit"],
            "phishing": ["phishing", "spoof", "fake", "suspicious email"],
            "attack": ["attack", "exploit", "hack", "breach", "intrusion"],
            "suspicious_activity": ["suspicious", "anomalous", "unusual", "abnormal"]
        }
        
        text_lower = text.lower()
        for category, patterns in threat_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                indicators.append(category)
        
        return indicators
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from data for anomaly detection"""
        features = []
        
        for item in data:
            feature_vector = []
            
            # Extract numerical features
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    feature_vector.append(value)
                elif isinstance(value, str):
                    # Convert string to numerical representation
                    feature_vector.append(len(value))
                else:
                    feature_vector.append(0)
            
            features.append(feature_vector)
        
        return np.array(features)
    
    async def cleanup(self):
        """Cleanup AI models and resources"""
        try:
            # Clear GPU memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Clear models
            self.models.clear()
            self.tokenizers.clear()
            
            logger.info("✅ AI Engine cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")