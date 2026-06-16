"""
Calendar and Reminder Application
A Python application that displays a monthly calendar with the ability to set and manage reminders.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from reminder_manager import ReminderManager
from calendar_view import CalendarView


class CalendarReminderApp:
    """Main application class for the calendar and reminder system."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Calendar & Reminder Manager")
        self.root.geometry("900x700")
        
        # Initialize reminder manager
        self.reminder_manager = ReminderManager()
        
        # Setup GUI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Month/Year navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(nav_frame, text="< Previous", command=self.previous_month).pack(side=tk.LEFT, padx=2)
        
        self.month_label = ttk.Label(nav_frame, text="", font=("Arial", 14, "bold"))
        self.month_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(nav_frame, text="Next >", command=self.next_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Today", command=self.today).pack(side=tk.LEFT, padx=2)
        
        # Button frame
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Add Reminder", command=self.add_reminder).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="View Reminders", command=self.view_reminders).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_calendar).pack(side=tk.LEFT, padx=2)
        
        # Calendar frame
        calendar_frame = ttk.LabelFrame(main_frame, text="Calendar")
        calendar_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create calendar view
        self.calendar_view = CalendarView(calendar_frame, self.on_date_selected)
        self.calendar_view.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X)
        
        # Set initial month
        self.current_date = datetime.now()
        self.refresh_calendar()
        
    def refresh_calendar(self):
        """Refresh the calendar display."""
        self.calendar_view.set_date(self.current_date)
        self.month_label.config(
            text=self.current_date.strftime("%B %Y")
        )
        self.highlight_reminder_dates()
        
    def highlight_reminder_dates(self):
        """Highlight dates that have reminders."""
        reminders = self.reminder_manager.get_reminders_for_month(
            self.current_date.year,
            self.current_date.month
        )
        reminder_dates = [r['date'].split('-')[2] for r in reminders]
        self.calendar_view.highlight_dates(reminder_dates)
        
    def previous_month(self):
        """Navigate to previous month."""
        first_day = self.current_date.replace(day=1)
        self.current_date = first_day - timedelta(days=1)
        self.refresh_calendar()
        
    def next_month(self):
        """Navigate to next month."""
        last_day = self.current_date.replace(day=28) + timedelta(days=4)
        self.current_date = (last_day - timedelta(days=last_day.day - 1)).replace(day=1)
        self.refresh_calendar()
        
    def today(self):
        """Navigate to today."""
        self.current_date = datetime.now()
        self.refresh_calendar()
        
    def on_date_selected(self, date_str):
        """Handle date selection from calendar."""
        selected_date = datetime.strptime(date_str, "%Y-%m-%d")
        reminders = self.reminder_manager.get_reminders_for_date(date_str)
        
        if reminders:
            self.show_date_reminders(date_str, reminders)
        else:
            response = messagebox.askyesno(
                "Add Reminder",
                f"No reminders for {selected_date.strftime('%B %d, %Y')}.\n\nDo you want to add one?"
            )
            if response:
                self.add_reminder_for_date(date_str)
                
    def add_reminder(self):
        """Open dialog to add a new reminder."""
        dialog = ReminderDialog(self.root, self.reminder_manager)
        self.root.wait_window(dialog.window)
        self.refresh_calendar()
        self.status_var.set("Reminder added successfully")
        
    def add_reminder_for_date(self, date_str):
        """Add a reminder for a specific date."""
        dialog = ReminderDialog(self.root, self.reminder_manager, date_str)
        self.root.wait_window(dialog.window)
        self.refresh_calendar()
        
    def view_reminders(self):
        """View all reminders."""
        reminders = self.reminder_manager.get_all_reminders()
        if not reminders:
            messagebox.showinfo("Reminders", "No reminders set.")
            return
            
        RemindersWindow(self.root, self.reminder_manager, self.refresh_calendar)
        
    def show_date_reminders(self, date_str, reminders):
        """Show reminders for a specific date."""
        selected_date = datetime.strptime(date_str, "%Y-%m-%d")
        message = f"Reminders for {selected_date.strftime('%B %d, %Y')}:\n\n"
        for reminder in reminders:
            message += f"• {reminder['title']}\n  {reminder['description']}\n"
            
        response = messagebox.showinfo("Date Reminders", message)


class ReminderDialog:
    """Dialog for adding or editing reminders."""
    
    def __init__(self, parent, reminder_manager, date_str=None):
        """Initialize reminder dialog."""
        self.reminder_manager = reminder_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Add Reminder")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Make dialog modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI."""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Date
        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        self.date_entry = ttk.Entry(date_frame, width=15)
        self.date_entry.insert(0, self.date_str)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(date_frame, text="Select Date", command=self.select_date).pack(side=tk.LEFT)
        
        # Time
        ttk.Label(main_frame, text="Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(main_frame, width=15)
        self.time_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.time_entry.insert(0, "09:00")
        
        # Title
        ttk.Label(main_frame, text="Title:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=30)
        self.title_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(main_frame, height=6, width=35)
        self.description_text.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value="Personal")
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=["Personal", "Work", "Health", "Shopping", "Other"],
            state="readonly",
            width=27
        )
        category_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Priority
        ttk.Label(main_frame, text="Priority:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(
            main_frame,
            textvariable=self.priority_var,
            values=["Low", "Medium", "High"],
            state="readonly",
            width=27
        )
        priority_combo.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Save", command=self.save_reminder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
    def select_date(self):
        """Open date picker."""
        from tkinter.simpledialog import askstring
        date_str = simpledialog.askstring(
            "Select Date",
            "Enter date (YYYY-MM-DD):",
            initialvalue=self.date_str
        )
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date_str)
                self.date_str = date_str
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
                
    def save_reminder(self):
        """Save the reminder."""
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        
        if not title:
            messagebox.showerror("Validation Error", "Title is required")
            return
            
        if not description:
            messagebox.showerror("Validation Error", "Description is required")
            return
            
        try:
            datetime.strptime(self.date_entry.get(), "%Y-%m-%d")
            datetime.strptime(self.time_entry.get(), "%H:%M")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date or time format")
            return
            
        reminder = {
            "date": self.date_entry.get(),
            "time": self.time_entry.get(),
            "title": title,
            "description": description,
            "category": self.category_var.get(),
            "priority": self.priority_var.get()
        }
        
        self.reminder_manager.add_reminder(reminder)
        messagebox.showinfo("Success", "Reminder added successfully!")
        self.window.destroy()


class RemindersWindow:
    """Window to view and manage all reminders."""
    
    def __init__(self, parent, reminder_manager, refresh_callback=None):
        """Initialize reminders window."""
        self.reminder_manager = reminder_manager
        self.refresh_callback = refresh_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("All Reminders")
        self.window.geometry("800x500")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup reminders window UI."""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=5)
        self.category_filter = tk.StringVar(value="All")
        category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_filter,
            values=["All", "Personal", "Work", "Health", "Shopping", "Other"],
            state="readonly",
            width=15
        )
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_reminders())
        
        self.priority_filter = tk.StringVar(value="All")
        priority_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.priority_filter,
            values=["All", "Low", "Medium", "High"],
            state="readonly",
            width=15
        )
        priority_combo.pack(side=tk.LEFT, padx=5)
        priority_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_reminders())
        
        # Buttons
        button_frame = ttk.Frame(filter_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_reminders).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        
        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Date", "Time", "Title", "Category", "Priority"),
            height=15
        )
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Date", anchor=tk.W, width=100)
        self.tree.column("Time", anchor=tk.W, width=80)
        self.tree.column("Title", anchor=tk.W, width=300)
        self.tree.column("Category", anchor=tk.W, width=100)
        self.tree.column("Priority", anchor=tk.W, width=100)
        
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("Date", text="Date", anchor=tk.W)
        self.tree.heading("Time", text="Time", anchor=tk.W)
        self.tree.heading("Title", text="Title", anchor=tk.W)
        self.tree.heading("Category", text="Category", anchor=tk.W)
        self.tree.heading("Priority", text="Priority", anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_reminder_double_click)
        
        self.refresh_reminders()
        
    def refresh_reminders(self):
        """Refresh the reminders list."""
        self.tree.delete(*self.tree.get_children())
        reminders = self.reminder_manager.get_all_reminders()
        
        category_filter = self.category_filter.get()
        priority_filter = self.priority_filter.get()
        
        for idx, reminder in enumerate(reminders):
            if category_filter != "All" and reminder["category"] != category_filter:
                continue
            if priority_filter != "All" and reminder["priority"] != priority_filter:
                continue
                
            self.tree.insert(
                "",
                "end",
                iid=idx,
                values=(
                    reminder["date"],
                    reminder["time"],
                    reminder["title"],
                    reminder["category"],
                    reminder["priority"]
                )
            )
            
    def on_reminder_double_click(self, event):
        """Handle double-click on reminder."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)["values"]
            messagebox.showinfo(
                "Reminder Details",
                f"Date: {values[0]}\nTime: {values[1]}\nTitle: {values[2]}\nCategory: {values[3]}\nPriority: {values[4]}"
            )
            
    def delete_selected(self):
        """Delete selected reminder."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a reminder to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reminder?"):
            item = selection[0]
            values = self.tree.item(item)["values"]
            self.reminder_manager.delete_reminder(values[0], values[1], values[2])
            self.refresh_reminders()
            if self.refresh_callback:
                self.refresh_callback()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = CalendarReminderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
