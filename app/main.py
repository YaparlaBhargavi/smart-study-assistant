import os
import json
import logging
import uuid
import io
from datetime import datetime, timedelta
from collections import Counter
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_file, session
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")  # Required for session
CORS(app)

# Configure Gemini AI - FIXED MODEL NAME
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning("GEMINI_API_KEY not found in environment variables")
    api_key = "YOUR_API_KEY_HERE"

genai.configure(api_key=api_key)

# Try different model names (newer models)
model = None
model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro"]
for model_name in model_names:
    try:
        model = genai.GenerativeModel(model_name)
        logger.info(f"Successfully loaded model: {model_name}")
        break
    except Exception as e:
        logger.warning(f"Failed to load {model_name}: {e}")

if not model:
    logger.error("Could not load any Gemini model")
    model = None

# Store study sessions
study_sessions = []
study_users = {}

# ============ HELPER CLASSES ============


class StudyAssistant:
    """Core AI Assistant Logic"""

    @staticmethod
    def analyze_text(text, difficulty="medium"):
        """Analyze text and return structured learning output"""
        global model

        if not model:
            return StudyAssistant.fallback_response(text)

        difficulty_levels = {
            "easy": "simple language, basic concepts",
            "medium": "balanced depth with examples",
            "hard": "detailed analysis with advanced concepts",
        }

        prompt = f"""
        You are a Smart Study Assistant AI. Analyze the following educational text and provide a structured response.

        TEXT: {text[:3000]}

        DIFFICULTY LEVEL: {difficulty_levels.get(difficulty, difficulty_levels["medium"])}

        FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

        📝 SUMMARY
        Write a concise summary in 2-3 sentences.

        🎯 KEY POINTS
        • Point 1
        • Point 2
        • Point 3
        • Point 4 (if applicable)

        ❓ REVISION QUESTIONS
        1. Question 1?
        Answer: Clear answer with explanation

        2. Question 2?
        Answer: Clear answer with explanation

        💡 STUDY TIP
        Provide one practical tip for remembering this topic.

        🔗 RELATED TOPICS
        Suggest 2-3 related topics for further study.

        Make sure the content is accurate, educational, and well-structured.
        """

        try:
            response = model.generate_content(prompt)
            return {
                "success": True,
                "analysis": response.text,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return StudyAssistant.fallback_response(text)

    @staticmethod
    def fallback_response(text):
        """Fallback response if API fails"""
        return {
            "success": True,
            "analysis": f"""
            📝 SUMMARY
            Here's a quick summary of your text: {text[:200]}...

            🎯 KEY POINTS
            • Main concept: {text[:100]}...
            • Understanding this helps with broader learning
            • Practice and review regularly
            • Connect with existing knowledge

            ❓ REVISION QUESTIONS
            1. What is the main idea of this text?
            Answer: The text discusses {text[:150]}...

            2. How can you apply this knowledge?
            Answer: Review the concepts and practice regularly.

            💡 STUDY TIP
            Break complex topics into smaller chunks and use active recall.

            🔗 RELATED TOPICS
            • Study techniques
            • Note-taking strategies
            • Knowledge retention
            """,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def extract_metadata(text):
        """Extract metadata from text"""
        return {
            "word_count": len(text.split()),
            "char_count": len(text),
            "estimated_reading_time": round(len(text.split()) / 200, 1),
            "complexity": "Easy"
            if len(text.split()) < 200
            else "Medium"
            if len(text.split()) < 500
            else "Complex",
            "timestamp": datetime.now().isoformat(),
        }


class AdvancedStudyFeatures:
    """Advanced AI features for study assistant"""

    @staticmethod
    def detect_topics(text):
        """Auto-detect subject/topic using keywords"""
        topic_keywords = {
            "Computer Science": [
                "algorithm",
                "code",
                "programming",
                "data",
                "software",
                "AI",
                "ML",
                "python",
                "java",
                "javascript",
                "machine learning",
                "artificial intelligence",
            ],
            "Mathematics": [
                "equation",
                "function",
                "calculus",
                "algebra",
                "geometry",
                "formula",
                "theorem",
                "matrix",
                "vector",
                "statistics",
            ],
            "Science": [
                "experiment",
                "hypothesis",
                "theory",
                "molecule",
                "atom",
                "physics",
                "chemistry",
                "biology",
                "cell",
                "DNA",
                "chemical",
            ],
            "History": [
                "century",
                "war",
                "revolution",
                "empire",
                "ancient",
                "civilization",
                "king",
                "president",
                "battle",
                "historical",
            ],
            "Literature": [
                "author",
                "poem",
                "novel",
                "character",
                "theme",
                "metaphor",
                "story",
                "writing",
                "chapter",
                "literary",
            ],
            "Business": [
                "market",
                "strategy",
                "management",
                "finance",
                "customer",
                "product",
                "marketing",
                "sales",
                "investment",
                "business",
            ],
        }

        text_lower = text.lower()
        scores = {}

        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                scores[topic] = score

        if scores:
            return max(scores, key=scores.get)
        return "General Study"

    @staticmethod
    def calculate_confidence_score(text):
        """Calculate confidence/understanding score"""
        words = text.split()
        sentences = [s for s in text.split(".") if s.strip()]

        if not words:
            return 0

        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        score = 70
        if avg_word_length > 8:
            score -= 10
        if avg_sentence_length > 20:
            score -= 10
        if len(words) < 50:
            score += 5
        if len(words) > 500:
            score -= 5

        return min(max(score, 0), 100)

    @staticmethod
    def create_study_plan(text):
        """Create personalized study plan"""
        words = len(text.split())
        estimated_time = words / 200

        plan = {
            "total_time_minutes": round(estimated_time, 1),
            "techniques": [
                "Active Recall",
                "Spaced Repetition",
                "Pomodoro Technique",
                "Feynman Technique",
            ],
            "sessions": [],
        }

        if estimated_time <= 30:
            plan["sessions"].append(
                {
                    "duration": round(estimated_time, 1),
                    "activity": "Quick Review & Summary",
                    "technique": "Active Recall",
                }
            )
        else:
            plan["sessions"] = [
                {
                    "duration": 25,
                    "activity": "First Read & Summarize",
                    "technique": "SQ3R",
                },
                {"duration": 5, "activity": "Break", "technique": "Pomodoro"},
                {
                    "duration": 25,
                    "activity": "Key Points & Questions",
                    "technique": "Active Recall",
                },
                {"duration": 5, "activity": "Break", "technique": "Pomodoro"},
                {
                    "duration": 15,
                    "activity": "Review & Test Yourself",
                    "technique": "Self-Assessment",
                },
            ]

        return plan

    @staticmethod
    def generate_flashcards(text, num_cards=3):
        """Generate flashcards from text"""
        global model

        if not model:
            return [
                {"question": "What is the main concept?", "answer": text[:100] + "..."},
                {
                    "question": "Why is this important?",
                    "answer": "Understanding this helps build knowledge.",
                },
                {
                    "question": "How can you apply this?",
                    "answer": "Practice and review regularly.",
                },
            ]

        prompt = f"""
        Create {num_cards} flashcards from this text for studying.
        Format each as:
        Q: [Question]
        A: [Answer]

        Make questions test understanding, not just memorization.

        Text: {text[:1000]}
        """

        try:
            response = model.generate_content(prompt)
            flashcards = []
            lines = response.text.split("\n")
            current_q = None
            current_a = None

            for line in lines:
                if line.startswith("Q:"):
                    if current_q and current_a:
                        flashcards.append({"question": current_q, "answer": current_a})
                    current_q = line[2:].strip()
                    current_a = None
                elif line.startswith("A:") and current_q:
                    current_a = line[2:].strip()
                    flashcards.append({"question": current_q, "answer": current_a})
                    current_q = None

            if len(flashcards) == 0:
                flashcards = [
                    {
                        "question": "What is the main concept?",
                        "answer": text[:100] + "...",
                    },
                    {
                        "question": "Key takeaway?",
                        "answer": "Review the text for details.",
                    },
                ]

            return flashcards[:num_cards]
        except Exception as e:
            logger.error(f"Flashcard generation error: {e}")
            return [
                {"question": "What is the main concept?", "answer": text[:100] + "..."},
                {
                    "question": "Why is this important?",
                    "answer": "Understanding this helps build knowledge.",
                },
            ]

    @staticmethod
    def generate_practice_questions(text, count=3):
        """Generate different types of questions"""
        global model

        if not model:
            return "1. What is the main idea?\nAnswer: Based on the text provided.\n\n2. Key takeaway?\nAnswer: Review the material."

        prompt = f"""
        Generate {count} practice questions from this text. Include different types:
        1. Multiple Choice (with 4 options)
        2. True/False
        3. Short Answer

        Text: {text[:800]}

        Format clearly.
        """

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return "1. What did you learn from this text?\n2. How can you apply this knowledge?"


class Gamification:
    """Add game-like features for engagement"""

    def __init__(self):
        self.user_points = 0
        self.achievements = []
        self.streak_days = 0
        self.last_study_date = None

    def add_points(self, points, activity):
        """Add points for studying"""
        self.user_points += points

        achievements_to_check = [
            (50, "First Steps 🌱", "Completed first study session"),
            (100, "100 Points 🎯", "Reached 100 points!"),
            (500, "500 Points 🏆", "Achieved 500 points!"),
            (1000, "1000 Points 👑", "Master level reached!"),
        ]

        new_achievements = []
        for threshold, badge, desc in achievements_to_check:
            if self.user_points >= threshold and badge not in self.achievements:
                self.achievements.append(badge)
                new_achievements.append({"badge": badge, "description": desc})

        return {
            "points_earned": points,
            "total_points": self.user_points,
            "achievements": self.achievements,
            "new_achievements": new_achievements,
            "activity": activity,
        }

    def update_streak(self):
        """Update study streak"""
        today = datetime.now().date()

        if self.last_study_date:
            last_date = (
                self.last_study_date
                if isinstance(self.last_study_date, datetime)
                else datetime.fromisoformat(self.last_study_date).date()
            )
            if today == last_date + timedelta(days=1):
                self.streak_days += 1
            elif today > last_date + timedelta(days=1):
                self.streak_days = 1
        else:
            self.streak_days = 1

        self.last_study_date = datetime.now().isoformat()

        streak_bonus = 0
        if self.streak_days >= 7:
            streak_bonus = 50
            message = f"🔥 {self.streak_days} day streak! +{streak_bonus} bonus points!"
        elif self.streak_days >= 3:
            streak_bonus = 20
            message = f"🔥 {self.streak_days} day streak! +{streak_bonus} bonus points!"
        else:
            message = f"{self.streak_days} day streak! Keep going!"

        if streak_bonus > 0:
            self.add_points(streak_bonus, "streak_bonus")

        return {
            "streak": self.streak_days,
            "message": message,
            "bonus_points": streak_bonus,
        }

    def get_dashboard(self):
        """Get dashboard data"""
        return {
            "stats": {
                "points": self.user_points,
                "level": 1 + (self.user_points // 100),
                "streak": self.streak_days,
                "achievements_count": len(self.achievements),
                "badges": self.achievements,
                "xp": self.user_points % 100,
                "xp_progress": self.user_points % 100,
            },
            "achievements": self.achievements,
        }


class StudyAnalytics:
    """Track study patterns and provide insights"""

    def __init__(self):
        self.study_sessions = []

    def log_session(self, text_length, difficulty, time_spent, topic):
        """Log a study session"""
        session = {
            "timestamp": datetime.now().isoformat(),
            "text_length": text_length,
            "difficulty": difficulty,
            "time_spent": time_spent,
            "topic": topic,
        }
        self.study_sessions.append(session)

        if len(self.study_sessions) > 100:
            self.study_sessions.pop(0)

    def get_insights(self):
        """Generate study insights"""
        if not self.study_sessions:
            return {
                "total_sessions": 0,
                "total_study_time_hours": 0,
                "avg_session_duration_minutes": 0,
                "favorite_topic": "None",
                "preferred_difficulty": "medium",
                "recommendations": [
                    "Start your first study session to see insights!",
                    "Use the study tools to analyze your text",
                    "Track your progress with the dashboard",
                ],
            }

        total_sessions = len(self.study_sessions)
        total_time = sum(s["time_spent"] for s in self.study_sessions)
        avg_time = total_time / total_sessions if total_sessions > 0 else 0

        # Get favorite topic
        topics = [s["topic"] for s in self.study_sessions if s.get("topic")]
        favorite_topic = Counter(topics).most_common(1)[0][0] if topics else "General"

        # Get preferred difficulty
        difficulties = [s["difficulty"] for s in self.study_sessions]
        preferred_difficulty = (
            Counter(difficulties).most_common(1)[0][0] if difficulties else "medium"
        )

        return {
            "total_sessions": total_sessions,
            "total_study_time_hours": round(total_time / 60, 1),
            "avg_session_duration_minutes": round(avg_time, 1),
            "favorite_topic": favorite_topic,
            "preferred_difficulty": preferred_difficulty,
            "average_score_percent": 75,
            "recommendations": [
                "Study consistently for better results",
                "Use active recall techniques",
                "Review material within 24 hours",
                "Create flashcards for key concepts",
            ],
        }


# Initialize features
study_analytics = StudyAnalytics()
gamification = Gamification()
advanced_features = AdvancedStudyFeatures()

# ============ ROUTES ============


@app.route("/")
def home():
    """Main landing page"""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return jsonify(
            {
                "message": "Smart Study Assistant API is running!",
                "status": "active",
                "model_loaded": model is not None,
            }
        )


@app.route("/advanced")
def advanced():
    """Advanced features page"""
    try:
        return render_template("advanced.html")
    except Exception as e:
        logger.error(f"Error rendering advanced: {e}")
        return jsonify({"message": "Advanced features available via API"})


@app.route("/dashboard")
def dashboard():
    """Dashboard page"""
    try:
        return render_template("dashboard.html")
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return jsonify(
            {"error": str(e), "message": "Dashboard template not found"}
        ), 404


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "Smart Study Assistant",
            "version": "3.0.0",
            "timestamp": datetime.now().isoformat(),
            "model_loaded": model is not None,
            "features": [
                "summarization",
                "flashcards",
                "quiz",
                "analytics",
                "gamification",
            ],
        }
    )


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        text = data.get("text", "").strip()
        difficulty = data.get("difficulty", "medium")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        if len(text) < 10:
            return jsonify(
                {"error": "Text too short. Please provide at least 10 characters."}
            ), 400

        result = StudyAssistant.analyze_text(text, difficulty)
        metadata = StudyAssistant.extract_metadata(text)

        session = {
            "id": len(study_sessions) + 1,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "timestamp": metadata["timestamp"],
            "difficulty": difficulty,
        }
        study_sessions.append(session)

        if len(study_sessions) > 100:
            study_sessions.pop(0)

        # Add gamification points
        points = min(50, max(10, len(text.split()) // 10))
        gamification.add_points(points, "study_session")

        # Log analytics
        topic = text[:50]
        reading_time = metadata.get("estimated_reading_time", len(text.split()) / 200)
        study_analytics.log_session(len(text.split()), difficulty, reading_time, topic)

        return jsonify(
            {
                "success": True,
                "analysis": result["analysis"],
                "metadata": metadata,
                "session_id": session["id"],
                "gamification": gamification.get_dashboard(),
            }
        )

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/advanced/analyze", methods=["POST"])
def advanced_analyze():
    """Advanced analysis endpoint"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        difficulty = data.get("difficulty", "medium")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        topic = advanced_features.detect_topics(text)
        confidence = advanced_features.calculate_confidence_score(text)
        study_plan = advanced_features.create_study_plan(text)

        return jsonify(
            {
                "success": True,
                "advanced": {
                    "topic": topic,
                    "confidence_score": confidence,
                    "study_plan": study_plan,
                },
            }
        )
    except Exception as e:
        logger.error(f"Advanced analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/quiz", methods=["POST"])
def generate_quiz():
    """Generate interactive quiz from text"""
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        questions = advanced_features.generate_practice_questions(text, 5)

        return jsonify(
            {
                "success": True,
                "quiz": questions,
                "instructions": "Answer all questions to test your understanding!",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/flashcards", methods=["POST"])
def generate_flashcards():
    """Generate flashcards"""
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        flashcards = advanced_features.generate_flashcards(text)

        return jsonify({"success": True, "flashcards": flashcards})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Get recent study sessions"""
    return jsonify({"sessions": study_sessions[-10:], "total": len(study_sessions)})


@app.route("/api/gamification", methods=["GET"])
def get_gamification():
    """Get gamification data"""
    return jsonify(gamification.get_dashboard())


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Get analytics data"""
    return jsonify(study_analytics.get_insights())


@app.route("/api/compare", methods=["POST"])
def compare_topics():
    """Compare two texts"""
    try:
        data = request.get_json()
        text1 = data.get("text1", "")
        text2 = data.get("text2", "")

        if not text1 or not text2:
            return jsonify({"error": "Both texts required"}), 400

        if model:
            prompt = f"""
            Compare and contrast these two topics:

            TOPIC 1: {text1[:500]}
            TOPIC 2: {text2[:500]}

            Provide similarities and differences.
            """
            response = model.generate_content(prompt)
            comparison = response.text
        else:
            comparison = "Comparison available with Gemini API."

        return jsonify({"success": True, "comparison": comparison})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset_progress():
    """Reset user progress"""
    try:
        global gamification, study_analytics, study_sessions
        gamification = Gamification()
        study_analytics = StudyAnalytics()
        study_sessions = []
        return jsonify({"success": True, "message": "Progress reset successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/summaries", methods=["POST"])
def multi_level_summaries():
    """Generate multi-level summaries"""
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        summaries = {
            "30_seconds": f"Quick summary: {text[:200]}...",
            "5_minutes": f"Detailed summary: {text[:500]}...",
            "deep_dive": f"Comprehensive analysis: {text[:800]}...",
        }

        return jsonify({"success": True, "summaries": summaries})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
