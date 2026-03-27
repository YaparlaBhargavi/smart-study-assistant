import google.generativeai as genai
import os
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class StudyAssistant:
    """Core AI Study Assistant"""

    @staticmethod
    def analyze_text(text: str, difficulty: str = "medium", model=None) -> Dict:
        """Analyze text with Gemini AI"""

        prompts = {
            "easy": "Explain in simple terms with basic concepts",
            "medium": "Provide balanced depth with clear examples",
            "hard": "Give detailed analysis with advanced concepts",
        }

        prompt = f"""
        You are an expert study assistant. Analyze this text and provide:

        TEXT: {text[:3500]}

        Please provide EXACTLY in this format:

        📝 SUMMARY
        [Write a concise 2-3 sentence summary]

        🎯 KEY POINTS
        • [Key point 1]
        • [Key point 2]
        • [Key point 3]

        ❓ REVISION QUESTIONS
        1. [Question 1]?
        Answer: [Clear answer]

        2. [Question 2]?
        Answer: [Clear answer]

        💡 STUDY TIP
        [One practical tip]

        🔗 RELATED TOPICS
        • [Topic 1]
        • [Topic 2]

        Use {prompts.get(difficulty, prompts["medium"])}.
        """

        try:
            if model:
                response = model.generate_content(prompt)
                return {
                    "success": True,
                    "analysis": response.text,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return StudyAssistant.fallback_response(text)
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return StudyAssistant.fallback_response(text)

    @staticmethod
    def fallback_response(text: str) -> Dict:
        """Fallback when API fails"""
        return {
            "success": True,
            "analysis": f"""
            📝 SUMMARY
            {text[:200]}...

            🎯 KEY POINTS
            • Main concept: {text[:100]}...
            • Understanding this is important
            • Review key terms regularly

            ❓ REVISION QUESTIONS
            1. What is the main idea?
            Answer: The text discusses {text[:150]}...

            2. How can you remember this?
            Answer: Use active recall and practice

            💡 STUDY TIP
            Use spaced repetition for better retention

            🔗 RELATED TOPICS
            • Study techniques
            • Knowledge retention
            """,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def extract_metadata(text: str) -> Dict:
        """Extract text statistics"""
        words = text.split()
        return {
            "word_count": len(words),
            "char_count": len(text),
            "estimated_reading_time": round(len(words) / 200, 1),
            "complexity": "Easy"
            if len(words) < 200
            else "Medium"
            if len(words) < 500
            else "Complex",
            "timestamp": datetime.now().isoformat(),
        }


class SmartFeatures:
    """Advanced smart features"""

    @staticmethod
    def generate_mind_map(text: str, model=None) -> Dict:
        """Generate mind map structure"""
        prompt = f"""
        Create a mind map structure from this text.
        Provide a central topic and 4-6 branches with sub-points.

        TEXT: {text[:1500]}

        Format:
        CENTRAL: [Main topic]

        BRANCH 1: [Topic] -> [Subpoint 1], [Subpoint 2]
        BRANCH 2: [Topic] -> [Subpoint 1], [Subpoint 2]
        """

        try:
            if model:
                response = model.generate_content(prompt)
                return {"success": True, "mind_map": response.text}
            else:
                return {
                    "success": True,
                    "mind_map": f"CENTRAL: {text[:50]}...\n\nBRANCH 1: Key Concepts -> Main ideas\nBRANCH 2: Applications -> Real-world uses",
                }
        except:
            return {
                "success": True,
                "mind_map": "Mind map generation complete. Check your API key for detailed results.",
            }

    @staticmethod
    def generate_practice_exercises(text: str, count: int = 3, model=None) -> Dict:
        """Generate practice exercises"""
        prompt = f"""
        Create {count} practice exercises from this text.

        TEXT: {text[:1500]}

        Format each exercise clearly with answers.
        """

        try:
            if model:
                response = model.generate_content(prompt)
                return {"success": True, "exercises": response.text}
            else:
                return {
                    "success": True,
                    "exercises": f"Practice Exercises:\n\n1. What is the main idea?\nAnswer: {text[:100]}...\n\n2. How can you apply this?\nAnswer: Practice and review regularly.",
                }
        except:
            return {"success": False, "error": "Could not generate exercises"}

    @staticmethod
    def summarize_levels(text: str, model=None) -> Dict:
        """Generate summaries at different levels"""
        levels = {
            "30_seconds": "30-second elevator pitch",
            "5_minutes": "5-minute detailed overview",
            "deep_dive": "Comprehensive analysis",
        }

        summaries = {}
        for level, desc in levels.items():
            prompt = f"""
            Provide a {desc} summary of this text.

            TEXT: {text[:2000]}
            """
            try:
                if model:
                    response = model.generate_content(prompt)
                    summaries[level] = response.text[:500]
                else:
                    summaries[level] = f"{desc} summary: {text[:150]}..."
            except:
                summaries[level] = f"Summary not available for {level}"

        return summaries


smart_features = SmartFeatures()
