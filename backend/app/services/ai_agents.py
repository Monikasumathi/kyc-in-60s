"""
AI Agent System for Enhanced KYC Review
Uses CrewAI with 2 specialized agents
Supports multiple LLM providers: OpenAI, Ollama, Custom APIs
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables for LLM configuration
# Find .env file in backend directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Try to import CrewAI
try:
    from crewai import Agent, Task, Crew, LLM
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("⚠️  CrewAI not available. Using mock responses.")


class LLMConfig:
    """Configuration for LLM providers"""
    
    def __init__(
        self,
        provider: str = "mock",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
    
    @classmethod
    def from_env(cls):
        """
        Load configuration from environment variables
        Simple pattern: LLM_API_KEY + BASE_URL + MODEL_NAME (matches working repo)
        """
        # Read generic environment variables (like working repo)
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("BASE_URL")
        model = os.getenv("MODEL_NAME")
        temperature = float(os.getenv("TEMPERATURE", "0.7"))
        provider = os.getenv("LLM_PROVIDER", "").lower()
        
        # If we have API key and base URL, use them
        if api_key and base_url and model:
            # Auto-detect provider if not explicitly set
            if not provider or provider == "mock":
                if "openrouter.ai" in base_url:
                    provider = "openrouter"
                elif "openai.com" in base_url:
                    provider = "openai"
                elif "anthropic.com" in base_url:
                    provider = "anthropic"
                else:
                    provider = "custom"  # Generic custom provider
            
            return cls(
                provider=provider,
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature
            )
        
        # Fallback: Check for provider-specific variables
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            model = model or "meta-llama/llama-3.3-70b-instruct:free"
            print(f"✅ Using OPENROUTER_API_KEY")
            print(f"   Model: {model}")
            return cls(
                provider="openrouter",
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                model=model,
                temperature=temperature
            )
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return cls(
                provider="openai",
                api_key=openai_key,
                base_url=os.getenv("OPENAI_API_BASE"),
                model=model or "gpt-4-turbo",
                temperature=temperature
            )
        
        # Mock mode (no LLM needed)
        print("⚠️  No LLM credentials found, using mock mode")
        return cls(provider="mock")


class KYCAgentSystem:
    """
    Two-Agent System for KYC Enhancement
    
    Agent 1: Risk Intelligence Analyst
    - Reviews all technical outputs
    - Provides smart risk interpretation
    - Identifies patterns and anomalies
    
    Agent 2: Customer Experience Agent
    - Generates personalized messages
    - Explains decisions clearly
    - Provides helpful guidance
    
    Supports multiple LLM providers:
    - OpenAI (GPT-4, GPT-3.5-turbo)
    - Ollama (Local LLMs - llama2, mistral, etc.)
    - Custom OpenAI-compatible APIs
    - Mock mode (for demos, no API needed)
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize KYC Agent System
        
        Args:
            config: LLMConfig object. If None, loads from environment variables
        """
        if config is None:
            config = LLMConfig.from_env()
        
        self.config = config
        self.use_mock = (config.provider == "mock" or not CREWAI_AVAILABLE)
        
        if not self.use_mock:
            try:
                self.llm = self._create_llm()
                self._setup_crew()
                print(f"✅ AI Agents initialized with {config.provider.upper()} ({config.model})")
            except Exception as e:
                print(f"⚠️  Failed to initialize LLM: {str(e)}")
                print("⚠️  Falling back to MOCK mode for demo")
                self.use_mock = True
        
        if self.use_mock:
            print("ℹ️  AI Agents running in MOCK mode (demo-ready)")
    
    def _create_llm(self):
        """
        Create LLM instance using CrewAI's LLM class
        Supports multiple providers through base_url and api_key configuration
        """
        return LLM(
            model=self.config.model,
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            temperature=self.config.temperature,
            timeout=300
        )
    
    def _setup_crew(self):
        """Setup the 2-agent crew with CrewAI"""
        
        # Agent 1: Risk Intelligence Analyst
        self.risk_analyst = Agent(
            role="Risk Intelligence Analyst",
            goal="""Analyze KYC verification results and provide intelligent 
            risk assessment with clear reasoning""",
            backstory="""You are an expert AI analyst specializing in identity 
            verification and fraud detection. You can interpret OCR confidence 
            scores, face matching results, and image quality metrics to provide 
            nuanced risk assessments. You understand that low confidence doesn't 
            always mean fraud - it could be poor image quality, unusual fonts, 
            or non-Latin characters. You look for patterns and provide context.""",
            verbose=False,
            allow_delegation=False,
            llm=self.llm  # Use the LLM instance we created
        )
        
        # Agent 2: Customer Experience Agent
        self.cx_agent = Agent(
            role="Customer Experience Specialist",
            goal="""Generate personalized, empathetic communications that 
            explain KYC decisions clearly and provide helpful next steps""",
            backstory="""You are a customer experience expert who excels at 
            communicating complex technical decisions in simple, friendly 
            language. You understand that KYC can be stressful for customers, 
            so you always maintain a helpful, positive tone. When explaining 
            rejections or delays, you provide specific, actionable guidance 
            on how to resolve issues.""",
            verbose=False,
            allow_delegation=False,
            llm=self.llm  # Use the LLM instance we created
        )
    
    def review_application(
        self,
        extracted_data: Dict,
        quality_check: Dict,
        face_match: Dict,
        risk_assessment: Dict
    ) -> Dict[str, Any]:
        """
        AI agents review the KYC application
        
        Returns:
        - Enhanced risk analysis
        - Personalized customer message
        - Actionable recommendations
        """
        
        if self.use_mock:
            return self._mock_review(extracted_data, risk_assessment, quality_check, face_match)
        else:
            return self._crew_review(
                extracted_data,
                quality_check,
                face_match,
                risk_assessment
            )
    
    def _mock_review(
        self,
        extracted_data: Dict,
        risk_assessment: Dict,
        quality_check: Dict,
        face_match: Dict
    ) -> Dict[str, Any]:
        """
        Mock agent responses for demo without API costs
        Provides realistic, intelligent-sounding analysis
        """
        
        risk_level = risk_assessment.get('risk_level', 'low')
        risk_score = risk_assessment.get('score', 0.0)
        confidence = risk_assessment.get('confidence', 0.0)
        reason_codes = risk_assessment.get('reason_codes', [])
        
        # Agent 1: Risk Intelligence Analysis
        if risk_level == 'low' and not reason_codes:
            risk_analysis = {
                'assessment': 'LOW_RISK_VERIFIED',
                'confidence': 0.95,
                'reasoning': """
**Risk Intelligence Analysis** 🎯

I've conducted a comprehensive review of all verification metrics:

✓ **Data Quality**: All identity fields extracted successfully with strong 
  confidence scores (>85%). The OCR performed well on this document.

✓ **Biometric Verification**: Face matching returned {:.0f}% confidence, 
  which exceeds our 60% threshold. The facial features align well between 
  the selfie and document photo.

✓ **Image Quality**: Document image passes all quality checks - minimal blur 
  (score: {:.1f}), no significant glare, and proper framing. Good lighting 
  and focus enabled accurate data extraction.

✓ **Data Consistency**: All extracted information is internally consistent. 
  Age calculation is reasonable, document not expired, and ID format follows 
  standard patterns.

**Risk Score**: {:.2f} (well below LOW threshold of 0.3)
**My Confidence**: 95%

**Pattern Analysis**: This application exhibits all characteristics of a 
legitimate verification. No fraud indicators detected. The data quality and 
biometric match suggest this is the genuine document holder.

**Recommendation**: APPROVE for instant account activation.
                """.format(
                    face_match.get('confidence', 0.75) * 100,
                    quality_check.get('blur_score', 100),
                    risk_score
                ),
                'fraud_indicators': [],
                'strengths': [
                    'Complete data extraction',
                    'Strong face match',
                    'High-quality images',
                    'Consistent information'
                ]
            }
            
            # Agent 2: Customer Message
            customer_message = """
🎉 **Welcome Aboard!**

Great news - your identity verification is complete and your account is now active!

**What We Verified:**
✓ Your identity document was authenticated  
✓ Your selfie matched your ID photo  
✓ All your information was securely recorded  

**Processing Time:** Just a few seconds! Our AI-powered system analyzed your 
documents instantly while maintaining bank-grade security.

**What's Next:**
• Check your email for your welcome package and account details
• Set up your security preferences in the app
• Start exploring all available services

**Quick Tip:** Your document expires on {expiry_date}. We'll send you a friendly 
reminder 6 months before to help you stay ahead!

Got questions? Our support team is here 24/7.

---
*Verified by AI • Secured by encryption • Compliant with regulations*
            """.format(
                expiry_date=extracted_data.get('expiry_date', {}).get('value', '2030')
            )
            
            recommendation = 'APPROVE'
            
        elif risk_level == 'low' and reason_codes:
            risk_analysis = {
                'assessment': 'LOW_RISK_WITH_NOTES',
                'confidence': 0.80,
                'reasoning': """
**Risk Intelligence Analysis** 🔍

I've reviewed the verification results. Overall profile is low risk, but with 
some observations:

**Positive Indicators:**
✓ Face matching successful ({face_confidence:.0f}% confidence)
✓ Document structure appears authentic
✓ No major fraud patterns detected

**Areas of Note:**
{notes}

**Risk Score**: {risk_score:.2f} (low risk range)
**My Confidence**: 80%

**Context**: These issues appear to be technical (image quality, OCR 
limitations) rather than indicators of fraud. The core identity verification 
is solid.

**Recommendation**: APPROVE, with suggestion for profile enhancement.
                """.format(
                    face_confidence=face_match.get('confidence', 0.75) * 100,
                    notes=self._format_reason_codes(reason_codes),
                    risk_score=risk_score
                ),
                'fraud_indicators': [],
                'strengths': ['Successful face match', 'Valid document structure']
            }
            
            customer_message = """
✅ **Application Approved!**

Your account is now active. We successfully verified your identity, though we 
noticed a few minor things:

{user_friendly_notes}

**Don't worry** - these small issues don't affect your approval! Your core 
identity verification passed all security checks.

**What's Next:**
• Your account is ready to use immediately
• Email sent with your account details
• Consider updating your profile with any missing information for the best experience

**Pro Tip:** For future document uploads, ensure good lighting and that all 
text is clearly visible. This helps our AI work even faster!

Welcome to our platform! 🎊
            """.format(
                user_friendly_notes=self._user_friendly_notes(reason_codes)
            )
            
            recommendation = 'APPROVE'
            
        else:  # medium or high risk
            risk_analysis = {
                'assessment': 'REQUIRES_HUMAN_REVIEW',
                'confidence': 0.70,
                'reasoning': """
**Risk Intelligence Analysis** ⚠️

This application requires human expert review:

**Concerns Identified:**
{concerns}

**Risk Score**: {risk_score:.2f} (manual review threshold)
**My Confidence**: 70%

**Analysis**: While I don't detect obvious fraud, the data quality or 
verification confidence isn't sufficient for automated approval. A human 
reviewer can assess context that AI might miss and make the final call.

**Recommendation**: MANUAL_REVIEW by specialist team (typical turnaround: 2-4 hours)
                """.format(
                    concerns=self._format_reason_codes(reason_codes),
                    risk_score=risk_score
                ),
                'fraud_indicators': reason_codes,
                'strengths': []
            }
            
            customer_message = """
📋 **Your Application is Under Review**

Thank you for submitting your KYC verification!

**Current Status:** Our specialist team is reviewing your application

**Why the extra step?**
{explanation}

This is a standard security procedure to ensure we properly verify everyone. 
It's not a rejection - we just need a human expert to take a closer look.

**What Happens Next:**
• Our team will review within 2-4 hours (usually faster!)
• You'll receive an email update as soon as we're done
• We may contact you if we need any clarification

**Can You Help Speed This Up?**
{helpful_tips}

We appreciate your patience. Your security is worth the extra moment! 🔒

---
*Questions? Contact support@kyc-platform.com*
            """.format(
                explanation=self._explain_review_reason(reason_codes),
                helpful_tips=self._helpful_tips(reason_codes)
            )
            
            recommendation = 'MANUAL_REVIEW'
        
        return {
            'recommendation': recommendation,
            'confidence': risk_analysis['confidence'],
            'risk_summary': str(risk_analysis),  # Convert to string for consistency
            'customer_message': customer_message,
            'next_steps': "Check your email for further instructions." if recommendation == 'MANUAL_REVIEW' else "Proceed with account activation.",
            'processing_timestamp': datetime.utcnow().isoformat(),
            'agent_version': 'mock-v1.0',
            'agents_used': ['Risk Intelligence Analyst (Mock)', 'Customer Experience Agent (Mock)']
        }
    
    def _format_reason_codes(self, codes):
        """Format reason codes for analyst view"""
        if not codes:
            return "No issues detected"
        
        formatted = []
        for code in codes:
            if 'MISSING_FIELD' in code:
                formatted.append(f"⚠ {code.replace('_', ' ').title()}")
            elif 'LOW_CONFIDENCE' in code:
                formatted.append(f"⚠ {code.replace('_', ' ').title()}")
            else:
                formatted.append(f"⚠ {code.replace('_', ' ').title()}")
        return '\n'.join(formatted)
    
    def _user_friendly_notes(self, codes):
        """Convert technical codes to user-friendly language"""
        if not codes:
            return ""
        
        messages = []
        for code in codes:
            if 'MISSING_FIELD_ADDRESS' in code:
                messages.append("• We couldn't fully read your address - no problem, you can update it in settings")
            elif 'LOW_CONFIDENCE_NAME' in code:
                messages.append("• Your name was extracted with slightly lower confidence - possibly due to the font style")
            elif 'IMAGE_BLURRY' in code:
                messages.append("• The image was a bit blurry - still readable, but clearer photos help next time")
            elif 'IMAGE_GLARE' in code:
                messages.append("• There was some glare on the document - tip: avoid direct overhead lighting")
        
        return '\n'.join(messages) if messages else "Everything looks great!"
    
    def _explain_review_reason(self, codes):
        """Explain why review is needed"""
        if 'FACE_MATCH_FAILED' in codes:
            return "Our AI had difficulty matching your selfie to your ID photo. This happens sometimes due to lighting, angles, or if your appearance has changed significantly since your ID was issued."
        elif any('MISSING_FIELD' in c for c in codes):
            return "Some required information couldn't be fully extracted from your document. This sometimes happens with certain document styles or image quality."
        elif any('IMAGE' in c for c in codes):
            return "The image quality made it difficult for our AI to read all details with high confidence."
        else:
            return "Our AI needs a human expert to verify some details for your security."
    
    def _helpful_tips(self, codes):
        """Provide helpful tips based on issues"""
        tips = []
        if 'IMAGE_BLURRY' in codes:
            tips.append("• If asked to resubmit, hold your phone steady or use a flat surface")
        if 'IMAGE_GLARE' in codes:
            tips.append("• Use natural light or position the document away from direct light sources")
        if 'FACE_MATCH_FAILED' in codes:
            tips.append("• Ensure your selfie is taken in good lighting with your full face visible")
        
        return '\n'.join(tips) if tips else "No action needed - just sit tight!"
    
    def _crew_review(
        self,
        extracted_data: Dict,
        quality_check: Dict,
        face_match: Dict,
        risk_assessment: Dict
    ) -> Dict[str, Any]:
        """
        Real CrewAI execution with OpenAI
        """
        
        # Task 1: Risk Analysis
        risk_task = Task(
            description=f"""
            Analyze this KYC verification data and provide intelligent risk assessment:
            
            **Extracted Data:**
            {extracted_data}
            
            **Quality Metrics:**
            {quality_check}
            
            **Face Match:**
            {face_match}
            
            **Risk Assessment:**
            {risk_assessment}
            
            Provide:
            1. Overall risk evaluation (LOW_RISK_VERIFIED, LOW_RISK_WITH_NOTES, or REQUIRES_HUMAN_REVIEW)
            2. Detailed reasoning considering all factors
            3. List of strengths and concerns
            4. Your confidence level (0-1)
            5. Fraud indicators if any
            6. Recommendation (APPROVE or MANUAL_REVIEW)
            """,
            agent=self.risk_analyst,
            expected_output="Detailed risk analysis with recommendation"
        )
        
        # Task 2: Customer Communication
        cx_task = Task(
            description=f"""
            Based on the risk analysis, generate a personalized customer message.
            
            **Risk Analysis Results:**
            {{context}}
            
            **Requirements:**
            1. Use friendly, conversational tone
            2. Explain the decision clearly
            3. If approved: celebrate and provide next steps
            4. If under review: explain why without technical jargon, provide timeline
            5. Include helpful tips relevant to any issues identified
            6. Keep it concise but warm
            
            Make the customer feel valued and informed!
            """,
            agent=self.cx_agent,
            expected_output="Customer-friendly message explaining the decision",
            context=[risk_task]  # Uses risk_task output as context
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.risk_analyst, self.cx_agent],
            tasks=[risk_task, cx_task],
            verbose=False  # Set to True for debugging
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # CrewAI returns a CrewOutput object - convert to string
        # The final output is the last task's result (customer message)
        customer_message = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        # Extract risk analysis from task outputs
        risk_summary = ""
        if hasattr(result, 'tasks_output') and len(result.tasks_output) > 0:
            risk_summary = str(result.tasks_output[0].raw) if hasattr(result.tasks_output[0], 'raw') else str(result.tasks_output[0])
        else:
            risk_summary = customer_message  # Fallback
        
        # Parse recommendation from risk analysis (look for keywords)
        recommendation = 'MANUAL_REVIEW'  # Default
        risk_lower = risk_summary.lower()
        if 'approve' in risk_lower and 'manual' not in risk_lower:
            recommendation = 'APPROVE'
        elif 'reject' in risk_lower or 'deny' in risk_lower:
            recommendation = 'REJECT'
        
        # Extract confidence (look for percentage or decimal in text)
        confidence = 0.85  # Default
        import re
        confidence_match = re.search(r'confidence[:\s]+(\d+)%', risk_lower)
        if confidence_match:
            confidence = float(confidence_match.group(1)) / 100
        else:
            confidence_match = re.search(r'confidence[:\s]+([0-9.]+)', risk_lower)
            if confidence_match:
                confidence = float(confidence_match.group(1))
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'risk_summary': risk_summary,
            'customer_message': customer_message,
            'next_steps': "Check your email for further instructions." if recommendation == 'MANUAL_REVIEW' else "Proceed with account activation.",
            'processing_timestamp': datetime.utcnow().isoformat(),
            'agent_version': 'crewai-v1.0',
            'agents_used': ['Risk Intelligence Analyst (LLM)', 'Customer Experience Agent (LLM)']
        }


# Convenience functions
def create_agent_system(config: Optional[LLMConfig] = None) -> KYCAgentSystem:
    """
    Create and return KYC Agent System
    
    Args:
        config: LLMConfig object. If None, loads from environment
    
    Returns:
        KYCAgentSystem instance
    """
    return KYCAgentSystem(config=config)


def create_openai_agent(api_key: str, model: str = "gpt-4-turbo") -> KYCAgentSystem:
    """Convenience: Create agent with OpenAI"""
    config = LLMConfig(provider="openai", api_key=api_key, model=model)
    return KYCAgentSystem(config=config)


def create_ollama_agent(base_url: str = "http://localhost:11434", model: str = "llama2") -> KYCAgentSystem:
    """Convenience: Create agent with Ollama (local)"""
    config = LLMConfig(provider="ollama", base_url=base_url, model=model)
    return KYCAgentSystem(config=config)


def create_custom_agent(base_url: str, model: str, api_key: Optional[str] = None) -> KYCAgentSystem:
    """Convenience: Create agent with custom OpenAI-compatible API"""
    config = LLMConfig(provider="custom", base_url=base_url, model=model, api_key=api_key)
    return KYCAgentSystem(config=config)

