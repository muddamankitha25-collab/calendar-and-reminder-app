"""
Reminder Manager Module
Handles storage, retrieval, and management of reminders.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class ReminderManager:
    """Manages reminders with persistent storage."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the reminder manager.
        
        Args:
            data_dir: Directory to store reminder data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.reminders_file = self.data_dir / "reminders.json"
        self.load_reminders()
        
    def load_reminders(self) -> None:
        """Load reminders from file."""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.reminders = []
        else:
            self.reminders = []
            
    def save_reminders(self) -> None:
        """Save reminders to file."""
        with open(self.reminders_file, 'w') as f:
            json.dump(self.reminders, f, indent=2)
            
    def add_reminder(self, reminder: Dict) -> None:
        """
        Add a new reminder.
        
        Args:
            reminder: Dictionary containing reminder data
        """
        reminder["id"] = len(self.reminders) + 1
        reminder["created_at"] = datetime.now().isoformat()
        self.reminders.append(reminder)
        self.save_reminders()
        
    def delete_reminder(self, date: str, time: str, title: str) -> bool:
        """
        Delete a reminder.
        
        Args:
            date: Reminder date (YYYY-MM-DD)
            time: Reminder time (HH:MM)
            title: Reminder title
            
        Returns:
            True if deleted, False otherwise
        """
        for idx, reminder in enumerate(self.reminders):
            if (reminder["date"] == date and 
                reminder["time"] == time and 
                reminder["title"] == title):
                self.reminders.pop(idx)
                self.save_reminders()
                return True
        return False
        
    def update_reminder(self, reminder_id: int, updated_data: Dict) -> bool:
        """
        Update an existing reminder.
        
        Args:
            reminder_id: ID of reminder to update
            updated_data: Dictionary with updated fields
            
        Returns:
            True if updated, False otherwise
        """
        for reminder in self.reminders:
            if reminder.get("id") == reminder_id:
                reminder.update(updated_data)
                reminder["updated_at"] = datetime.now().isoformat()
                self.save_reminders()
                return True
        return False
        
    def get_all_reminders(self) -> List[Dict]:
        """
        Get all reminders sorted by date and time.
        
        Returns:
            List of reminder dictionaries
        """
        return sorted(
            self.reminders,
            key=lambda x: (x.get("date", ""), x.get("time", ""))
        )
        
    def get_reminders_for_date(self, date: str) -> List[Dict]:
        """
        Get reminders for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            List of reminders for the date
        """
        return [r for r in self.reminders if r["date"] == date]
        
    def get_reminders_for_month(self, year: int, month: int) -> List[Dict]:
        """
        Get reminders for a specific month.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            List of reminders for the month
        """
        month_str = f"{year}-{month:02d}"
        return [r for r in self.reminders if r["date"].startswith(month_str)]
        
    def get_reminders_by_category(self, category: str) -> List[Dict]:
        """
        Get reminders by category.
        
        Args:
            category: Category name
            
        Returns:
            List of reminders in the category
        """
        return [r for r in self.reminders if r.get("category") == category]
        
    def get_reminders_by_priority(self, priority: str) -> List[Dict]:
        """
        Get reminders by priority.
        
        Args:
            priority: Priority level (Low, Medium, High)
            
        Returns:
            List of reminders with the priority
        """
        return [r for r in self.reminders if r.get("priority") == priority]
        
    def get_upcoming_reminders(self, days: int = 7) -> List[Dict]:
        """
        Get upcoming reminders within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming reminders
        """
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        upcoming = []
        for reminder in self.reminders:
            try:
                reminder_date = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
                if today <= reminder_date <= end_date:
                    upcoming.append(reminder)
            except ValueError:
                continue
                
        return sorted(upcoming, key=lambda x: x["date"])
        
    def get_overdue_reminders(self) -> List[Dict]:
        """
        Get reminders that are overdue.
        
        Returns:
            List of overdue reminders
        """
        from datetime import datetime
        
        today = datetime.now().date()
        overdue = []
        
        for reminder in self.reminders:
            try:
                reminder_date = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
                if reminder_date < today:
                    overdue.append(reminder)
            except ValueError:
                continue
                
        return sorted(overdue, key=lambda x: x["date"])
        
    def mark_reminder_complete(self, reminder_id: int) -> bool:
        """
        Mark a reminder as complete.
        
        Args:
            reminder_id: ID of reminder to mark complete
            
        Returns:
            True if marked, False otherwise
        """
        return self.update_reminder(reminder_id, {"completed": True})
        
    def clear_completed_reminders(self) -> int:
        """
        Clear all completed reminders.
        
        Returns:
            Number of reminders cleared
        """
        before_count = len(self.reminders)
        self.reminders = [r for r in self.reminders if not r.get("completed", False)]
        self.save_reminders()
        return before_count - len(self.reminders)
        
    def export_reminders(self, filename: str) -> None:
        """
        Export reminders to a JSON file.
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.reminders, f, indent=2)
            
    def import_reminders(self, filename: str) -> int:
        """
        Import reminders from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            Number of reminders imported
        """
        with open(filename, 'r') as f:
            imported = json.load(f)
            
        count = 0
        for reminder in imported:
            if isinstance(reminder, dict):
                self.add_reminder(reminder)
                count += 1
                
        return count
        
    def get_statistics(self) -> Dict:
        """
        Get reminder statistics.
        
        Returns:
            Dictionary with reminder statistics
        """
        stats = {
            "total_reminders": len(self.reminders),
            "by_category": {},
            "by_priority": {},
            "completed": len([r for r in self.reminders if r.get("completed", False)]),
            "pending": len([r for r in self.reminders if not r.get("completed", False)])
        }
        
        for reminder in self.reminders:
            category = reminder.get("category", "Unknown")
            priority = reminder.get("priority", "Unknown")
            
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
        return stats
        
    def search_reminders(self, query: str) -> List[Dict]:
        """
        Search reminders by title or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching reminders
        """
        query_lower = query.lower()
        return [
            r for r in self.reminders
            if query_lower in r.get("title", "").lower() or
               query_lower in r.get("description", "").lower()
        ]
