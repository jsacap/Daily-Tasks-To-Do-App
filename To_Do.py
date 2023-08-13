import tkinter as tk
import customtkinter as ctk
import datetime as dt
import json
import os
from tkinter import filedialog


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Daily Goals')
        self.geometry('930x500')
        ctk.set_appearance_mode('Dark')
        ctk.set_default_color_theme('dark-blue')

        self.today = dt.datetime.today()
        self.formatted_date = self.today.strftime('%A the %d' + ('th' if 4 <= self.today.day <= 20 or 24 <= self.today.day <= 30 else {
            1: 'st', 2: 'nd', 3: 'rd'}.get(self.today.day % 10, 'th')) + ' of %B %Y')

        # Center window on open
        self.center_window(900, 550, y_offset=200)

    def center_window(self, window_width, window_height, y_offset=1200):
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate centered position horizontally
        x = (screen_width - window_width) // 2

        # Calculate vertical position
        y = (screen_height - window_height) // 2 - y_offset

        # Set window's geometry
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create ALL frames
        self.main_frame = ctk.CTkFrame(self, width=1050, height=800)
        self.app_frame = ctk.CTkFrame(self.main_frame, width=700, height=600)
        self.menu_frame = ctk.CTkScrollableFrame(self.main_frame, width=200)
        self.right_frame = ctk.CTkFrame(self.main_frame, width=300)

        # Configure main frames
        self.configure_main_frames()

        # Preconfigurations
        self.archive_button_row = 10
        self.total_todo = 0
        self.total_complete = 0

        # Initialize UI elements
        self.initialize_ui()

    def configure_main_frames(self):
        # Configure grid weights
        self.main_frame.grid()
        self.main_frame.grid_columnconfigure((0, 2), weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Configure grid positions
        self.app_frame.grid(row=2, column=2)
        self.menu_frame.grid(row=2, column=0, padx=40, sticky='nsew')
        self.right_frame.grid(row=2, column=3, padx=40, sticky='nsew')

    def initialize_ui(self):
        # Create UI elements
        self.create_left_menu()
        self.create_main_title()
        self.create_stats_labels()
        self.create_scrollable_frame()
        self.add_task_entry_widgets()

        # Load previous day's goals
        self.create_archive_buttons()
        self.menu_frame.update_idletasks()

    def create_left_menu(self):
        # Create labels and buttons for the left menu
        left_frame_title = ctk.CTkLabel(
            self.menu_frame, text='M E N U', font=ctk.CTkFont(size=16, weight='bold'))
        left_frame_title.grid(row=0, columnspan=2, pady=(10, 30))
        archive_list_title = ctk.CTkLabel(
            self.menu_frame, text='ARCHIVE LIST', font=ctk.CTkFont(size=12, weight='bold'))
        archive_list_title.grid(row=5, columnspan=2, pady=(15, 5))
        new_day_button = ctk.CTkButton(
            self.menu_frame, text='New Day / Clear All', command=self.clear_tasks)
        new_day_button.grid(row=1, column=0, pady=(10, 10))
        collect_left_tasks = ctk.CTkButton(
            self.menu_frame, text='Save', command=self.snapshot
        )
        collect_left_tasks.grid(row=2, column=0, pady=(10, 20))

    def create_main_title(self):
        # Create main title label
        self.title_label = ctk.CTkLabel(
            self.main_frame, text=f'Daily Goals', font=ctk.CTkFont(size=50, weight='bold'))
        self.title_label.grid(row=0, column=1, columnspan=2, pady=(10, 20))

        self.subtitle = ctk.CTkLabel(
            self.main_frame, text=self.formatted_date, font=ctk.CTkFont(size=14))
        self.subtitle.grid(row=1, column=1, columnspan=2)

    def create_stats_labels(self):
        # Create labels for task statistics
        right_frame_title = ctk.CTkLabel(
            self.right_frame, text='STATS', font=ctk.CTkFont(size=16, weight='bold'))
        right_frame_title.grid(row=0, columnspan=2, pady=(10, 30))
        self.tasks_label = ctk.CTkLabel(
            self.right_frame, text=f'To Do - {self.total_todo}', font=ctk.CTkFont(size=12, weight='bold'))
        self.tasks_label.grid(row=5, column=0, sticky='w')
        self.completed_label = ctk.CTkLabel(
            self.right_frame, text=f'Completed - {self.total_complete}', font=ctk.CTkFont(size=12, weight='bold'))
        self.completed_label.grid(row=6, column=0)

    def create_scrollable_frame(self):
        # Create scrollable frame for tasks
        self.left_scrollable_frame = ctk.CTkScrollableFrame(
            self.app_frame, width=350, height=300)
        self.left_scrollable_frame.grid(row=3, column=1)

        # Create entry widgets for adding tasks

    def add_task_entry_widgets(self):
        self.task_entry = ctk.CTkEntry(
            self.left_scrollable_frame, placeholder_text='Add a task')
        self.task_entry.pack(fill='x')
        self.task_entry.bind('<Return>', self.add_task)

        # Create the add button for the task after input
        add_button = ctk.CTkButton(
            self.main_frame, text='ADD', width=150, command=self.add_task)
        add_button.grid(row=6, column=2, padx=10, pady=10)
        save_as_button = ctk.CTkButton(
            self.menu_frame, text='Save As...', width=150, command=self.save_snapshot_as)
        save_as_button.grid(row=3, column=0)

    # Creates checkbox for task entry widget

    def add_task(self, event=None):
        task = self.task_entry.get()
        if task:
            task_label = ctk.CTkCheckBox(
                self.left_scrollable_frame, text=task, font=ctk.CTkFont(size=16))
            task_label.pack(pady=2, anchor='w')
            self.total_todo += 1
            self._update_task_labels()
            self.task_entry.delete(0, ctk.END)

            task_label.bind('<Button-1>', lambda event,
                            label=task_label: self.mark_complete(label))
            task_label.bind('<Button-3>', lambda event,
                            label=task_label: self.delete_task(label))

    def delete_task(self, task_label):
        if task_label.get() == 0:
            self.total_todo -= 1

        else:
            self.total_complete -= 1

        task_label.destroy()
        self._update_task_labels()

    def mark_complete(self, task_label):
        if task_label.get() == 0:
            self.total_complete -= 1
            self.total_todo += 1
        else:
            self.total_complete += 1
            self.total_todo -= 1
        self._update_task_labels()

    def clear_tasks(self):
        # Clear all tasks and reset statistics
        for widget in self.left_scrollable_frame.winfo_children():
            widget.destroy()
        self.total_todo = 0
        self.total_complete = 0
        self._update_task_labels()
        self.add_task_entry_widgets()

    def _update_task_labels(self):
        # Update statistics labels
        self.tasks_label.configure(
            text=f'To-Do\n {self.total_todo}\n', font=ctk.CTkFont(size=12, weight='bold'))
        self.completed_label.configure(
            text=f'Completed\n {self.total_complete}', font=ctk.CTkFont(size=12, weight='bold'))

    def create_archive_buttons(self):
        # Create buttons based on archived files
        archived_dir = os.path.join(os.path.dirname(__file__), 'archived')
        for filename in os.listdir(archived_dir):
            if filename.endswith('.json'):
                date_str = os.path.splitext(
                    filename)[0]  # Remove .json extension
                button = ctk.CTkButton(
                    self.menu_frame, text=date_str, command=lambda file=filename: self.load_and_show_tasks(
                        file),
                    corner_radius=8, fg_color='transparent', hover=False, height=0)
                button.grid(row=self.archive_button_row,
                            column=0, pady=(5, 2))
                self.archive_button_row += 1

    def load_archived_file(self, filename):
        with open(filename, 'r') as f:
            tasks = json.load(f)
        return tasks

    def load_and_show_tasks(self, filename):
        # Get the current working directory
        script_dir = os.path.dirname(__file__)

        # Construct the full path to the archived file
        full_file_path = os.path.join(script_dir, 'archived', filename)

        # Load tasks from archived file and display
        tasks = self.load_archived_file(full_file_path)
        print("Full File Path:", full_file_path)

        # Load tasks from archived file and display
        tasks = self.load_archived_file(full_file_path)

        self.clear_tasks()
        for task in tasks:
            task_label = ctk.CTkCheckBox(
                self.left_scrollable_frame, text=task['task'], font=ctk.CTkFont(size=16))
            task_label.pack(pady=2, anchor='w')
            if task['completed']:
                task_label.select()
                self.total_complete += 1
            else:
                self.total_todo += 1
            self._update_task_labels()
            task_label.bind('<Button-1>', lambda event,
                            label=task_label: self.mark_complete(label))
            task_label.bind('<Button-3>', lambda event,
                            label=task_label: self.delete_task(label))

    def snapshot(self):
        current_date = dt.datetime.now()
        formatted_date = current_date.strftime('%A %d-%m-%Y')
        filename = f'{formatted_date}.json'

        script_dir = os.path.dirname(__file__)
        archived_dir = os.path.join(script_dir, 'archived')
        filename_path = os.path.join(archived_dir, filename)

        tasks = []
        for widget in self.left_scrollable_frame.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                task_text = widget.cget('text')
                completed = widget.get()
                tasks.append({"task": task_text, "completed": completed})

        if os.path.exists(filename_path):
            with open(filename_path, 'w') as f:
                json.dump(tasks, f, indent=4)
            print(f'Data saved to {filename_path}')
        else:
            if not os.path.exists(archived_dir):
                os.makedirs(archived_dir)
            with open(filename_path, 'w') as f:
                json.dump(tasks, f, indent=4)
            print(f'New data saved to {filename_path}')

    def save_snapshot_as(self):
        current_date = dt.datetime.now()
        formatted_date = current_date.strftime('%A %d-%m-%Y')

        # Open a file dialog to choose the directory and filename for saving
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f'{formatted_date}.json',
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            print("Save operation canceled.")
            return

        tasks = []
        for widget in self.left_scrollable_frame.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                task_text = widget.cget('text')
                completed = widget.get()
                tasks.append({"task": task_text, "completed": completed})

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                existing_tasks = json.load(f)
                tasks.extend(existing_tasks)

        with open(file_path, 'w') as f:
            json.dump(tasks, f, indent=4)

        print(f'Data saved to {file_path}')


if __name__ == "__main__":
    app = App()
    app.mainloop()
