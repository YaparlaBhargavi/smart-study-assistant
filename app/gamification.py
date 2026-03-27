import json
from datetime import datetime, timedelta
from typing import Dict, List


class GamificationEngine:
    """Complete gamification system"""

    def __init__(self):
        self.user_data = {}

    def get_or_create_user(self, user_id: str) -> Dict:
        """Get or create user data"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "points": 0,
                "level": 1,
                "streak": 0,
                "last_study": None,
                "achievements": [],
                "badges": [],
                "xp": 0,
            }
        return self.user_data[user_id]

    def add_points(self, user_id: str, points: int, activity: str) -> Dict:
        """Add points and update level"""
        user = self.get_or_create_user(user_id)
        user["points"] += points
        user["xp"] += points

        # Level up system
        xp_needed = user["level"] * 100
        leveled_up = False
        while user["xp"] >= xp_needed:
            user["level"] += 1
            user["xp"] -= xp_needed
            leveled_up = True
            xp_needed = user["level"] * 100

        # Update streak
        today = datetime.now().date()
        if user["last_study"]:
            last = datetime.fromisoformat(user["last_study"]).date()
            if today == last + timedelta(days=1):
                user["streak"] += 1
            elif today > last + timedelta(days=1):
                user["streak"] = 1
        else:
            user["streak"] = 1
        user["last_study"] = datetime.now().isoformat()

        # Check achievements
        new_achievements = self._check_achievements(user)

        return {
            "points_earned": points,
            "total_points": user["points"],
            "level": user["level"],
            "streak": user["streak"],
            "xp": user["xp"],
            "xp_to_next": (user["level"] * 100) - user["xp"],
            "new_achievements": new_achievements,
            "leveled_up": leveled_up,
        }

    def _check_achievements(self, user: Dict) -> List:
        """Check and award achievements"""
        achievements = []

        achievements_config = [
            (50, "Quick Learner", "Complete first study session"),
            (100, "100 Points", "Reach 100 points"),
            (500, "Scholar", "Reach 500 points"),
            (1000, "Master", "Reach 1000 points"),
            (7, "Week Warrior", "7-day streak"),
            (30, "Monthly Master", "30-day streak"),
        ]

        for threshold, badge, desc in achievements_config:
            if badge not in user["achievements"]:
                if (
                    badge in ["Week Warrior", "Monthly Master"]
                    and user["streak"] >= threshold
                ) or (
                    badge not in ["Week Warrior", "Monthly Master"]
                    and user["points"] >= threshold
                ):
                    user["achievements"].append(badge)
                    user["badges"].append({"badge": badge, "description": desc})
                    achievements.append({"badge": badge, "description": desc})

        return achievements

    def get_dashboard(self, user_id: str) -> Dict:
        """Get user dashboard data"""
        user = self.get_or_create_user(user_id)
        return {
            "stats": {
                "points": user["points"],
                "level": user["level"],
                "streak": user["streak"],
                "xp": user["xp"],
                "xp_progress": (user["xp"] / (user["level"] * 100)) * 100,
                "achievements_count": len(user["achievements"]),
                "badges": user["badges"],
            },
            "achievements": user["achievements"],
            "next_level_xp": (user["level"] * 100) - user["xp"],
        }


gamification = GamificationEngine()
