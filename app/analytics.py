from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List


class LearningAnalytics:
    """Track and analyze learning patterns"""

    def __init__(self):
        self.sessions = []

    def log_session(
        self,
        user_id: str,
        topic: str,
        duration: int,
        difficulty: str,
        score: int = None,
    ):
        """Log a study session"""
        session = {
            "user_id": user_id,
            "topic": topic,
            "duration": duration,
            "difficulty": difficulty,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "day": datetime.now().strftime("%A"),
            "hour": datetime.now().hour,
        }
        self.sessions.append(session)

        # Keep last 500 sessions
        if len(self.sessions) > 500:
            self.sessions.pop(0)

    def get_insights(self, user_id: str) -> Dict:
        """Get personalized learning insights"""
        user_sessions = [s for s in self.sessions if s["user_id"] == user_id]

        if not user_sessions:
            return {"message": "No study data yet. Start studying to see insights!"}

        # Topics studied
        topics = [s["topic"] for s in user_sessions]
        topic_counts = Counter(topics)
        favorite_topic = topic_counts.most_common(1)[0][0] if topics else "None"

        # Study patterns
        hours = [s["hour"] for s in user_sessions]
        most_active_hour = Counter(hours).most_common(1)[0][0] if hours else 0

        days = [s["day"] for s in user_sessions]
        most_active_day = Counter(days).most_common(1)[0][0] if days else "Monday"

        # Average metrics
        avg_duration = sum(s["duration"] for s in user_sessions) / len(user_sessions)
        total_study_time = sum(s["duration"] for s in user_sessions)

        # Difficulty preference
        difficulties = [s["difficulty"] for s in user_sessions]
        preferred_difficulty = (
            Counter(difficulties).most_common(1)[0][0] if difficulties else "medium"
        )

        # Performance trend
        scores = [s["score"] for s in user_sessions if s.get("score")]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_sessions": len(user_sessions),
            "total_study_time_hours": round(total_study_time / 60, 1),
            "avg_session_duration_minutes": round(avg_duration, 1),
            "favorite_topic": favorite_topic,
            "most_active_hour": f"{most_active_hour}:00",
            "most_active_day": most_active_day,
            "preferred_difficulty": preferred_difficulty,
            "average_score_percent": round(avg_score, 1),
            "topic_breakdown": dict(topic_counts.most_common(5)),
            "recommendations": self._generate_recommendations(user_sessions, avg_score),
        }

    def _generate_recommendations(self, sessions: List, avg_score: float) -> List:
        """Generate personalized recommendations"""
        recommendations = []

        if len(sessions) < 5:
            recommendations.append("📚 Study more consistently to see better results")

        if avg_score < 60:
            recommendations.append("🎯 Review topics more thoroughly before quizzes")
        elif avg_score > 80:
            recommendations.append("🏆 Great performance! Try harder topics")

        if len(sessions) > 10:
            recommendations.append(
                "💪 Consistent effort! Consider teaching others to reinforce learning"
            )

        recommendations.append("✨ Use flashcards for better retention")
        recommendations.append("🔄 Practice active recall instead of passive reading")

        return recommendations[:4]


analytics = LearningAnalytics()
