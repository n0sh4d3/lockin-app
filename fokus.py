# todo
# block sites when locking in hard
# gamifying this shit would be fire (but hard tho)
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkLabel,
    CTkFrame,
    CTkProgressBar,
    CTkFont,
    set_appearance_mode,
    CTkTabview,
    CTkScrollableFrame,
    StringVar,
)

import time
import threading
import platform
import darkdetect
from datetime import datetime
from read_json_db import Database
from colors import *  # pyright: ignore[F403]

# ^  WHY NVIM IS STILL SHOWING WARNING???? (now it stopped) (ty magic comment)
# IT'S FUCKED AGAIN XDDD

from settings_manager import SettingsManager
from quotes.quotes_handler import QuoteHandler
from websiteblocker import WebsiteBlocker
import random
from pygame import mixer


class FokusApp:
    def __init__(self) -> None:
        self.DB = Database()
        self.settings_manager = SettingsManager()
        self.is_finished = False
        self.countdown_running = False
        self.countdown_thread = None

        self.current_theme = self.settings_manager.get("theme")
        self.setup_theme()

        self.total_focus_time = sum(int(time) for time in self.DB.focus_times)
        self.current_session_seconds = 0
        self.session_history = [int(time) for time in self.DB.focus_times]

        if self.current_theme == "light":
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")

        self.quotes = QuoteHandler()

        self.platform = platform.system().lower()
        self.init_website_blocker()

        self.sound_enabled = True

    def start(self):
        """App is running (lezz goo)"""
        self.app = CTk()
        self.app.title("Fokus")
        self.app.geometry("1100x750")
        self.app.configure(fg_color=self.clrs.NEUTRAL_900)
        self.app.resizable(False, False)

        self.header_font = CTkFont(family="SF Pro Display", size=32, weight="bold")
        self.subheader_font = CTkFont(family="SF Pro Display", size=17)
        self.timer_font = CTkFont(family="SF Pro Display", size=78, weight="bold")
        self.label_font = CTkFont(family="SF Pro Display", size=14)
        self.button_font = CTkFont(family="SF Pro Display", size=16, weight="bold")
        self.stats_font = CTkFont(family="SF Pro Display", size=28, weight="bold")
        self.tooltip_font = CTkFont(family="SF Pro Display", size=13)

        self.create_sidebar()
        self.create_main_container()

        self.show_setup_view()
        self.update_total_focus_time()
        self.start_system_theme_monitoring()

        self.app.mainloop()

    def setup_theme(self):
        """Setup colors based on current theme"""
        if self.current_theme == "system":
            actual_theme = self.get_system_theme()
        else:
            actual_theme = self.current_theme

        if actual_theme == "light":
            self.clrs = LightTheme()  # pyright: ignore[F405]
        else:
            self.clrs = DarkTheme()  # pyright: ignore[F405]

        self.active_theme = actual_theme

    def get_system_theme(self):
        """Get the current system"""
        try:
            if darkdetect.isDark():
                return "dark"
            else:
                return "light"
        except Exception:
            return "dark"

    def change_theme(self, theme_name):
        """Change the application theme"""
        self.current_theme = theme_name
        self.settings_manager.set("theme", theme_name)
        self.setup_theme()

        if self.active_theme == "light":
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")

        self.app.configure(fg_color=self.clrs.NEUTRAL_900)

        self.update_sidebar_colors()

        if hasattr(self, "main_container"):
            self.main_container.configure(fg_color="transparent")

        if hasattr(self, "current_view"):
            current_view = self.current_view
            if current_view == "setup":
                self.show_setup_view()
            elif current_view == "statistics":
                self.show_statistics_view()
            elif current_view == "settings":
                self.show_settings_view(True)
            elif current_view == "countdown":
                self.update_countdown_colors()
        else:
            self.show_setup_view()

    def update_countdown_colors(self):
        """Update countdown view colors without disrupting the timer"""
        if hasattr(self, "countdown_label"):
            self.countdown_label.configure(text_color=self.clrs.FG_COLOR)

        if hasattr(self, "progress_bar"):
            self.progress_bar.configure(
                fg_color=self.clrs.NEUTRAL_700, progress_color=self.clrs.PRIMARY
            )

        if hasattr(self, "header_container"):
            for widget in self.header_container.winfo_children():
                if isinstance(widget, CTkLabel):
                    if "Fokus Session" in widget.cget("text"):
                        widget.configure(text_color=self.clrs.FG_COLOR)
                    else:
                        widget.configure(text_color=self.clrs.NEUTRAL_400)

        if hasattr(self, "content_container"):
            for widget in self.content_container.winfo_children():
                if isinstance(widget, CTkFrame):
                    widget.configure(fg_color=self.clrs.NEUTRAL_800)

    def update_sidebar_colors(self):
        """Update sidebar colors after theme change"""
        if hasattr(self, "sidebar"):
            self.sidebar.configure(fg_color=self.clrs.NEUTRAL_800)

            if hasattr(self, "total_focus_display"):
                self.total_focus_display.configure(text_color=self.clrs.PRIMARY)

            self.update_navigation_colors()

    def update_navigation_colors(self):
        """Update navigation button colors"""
        nav_buttons = [
            ("Fokus Timer", getattr(self, "focus_nav_btn", None)),
            ("Statistics", getattr(self, "stats_nav_btn", None)),
            ("Settings", getattr(self, "settings_nav_btn", None)),
        ]

        current_view_map = {
            "setup": "Fokus Timer",
            "countdown": "Fokus Timer",
            "statistics": "Statistics",
            "settings": "Settings",
        }

        active_nav = current_view_map.get(
            getattr(self, "current_view", "setup"), "Fokus Timer"
        )

        for nav_text, btn in nav_buttons:
            if btn:
                if nav_text == active_nav:
                    btn.configure(
                        fg_color=self.clrs.PRIMARY,
                        text_color=self.clrs.FG_COLOR,
                        hover_color=self.clrs.PRIMARY_DARK,
                    )
                else:
                    btn.configure(
                        fg_color="transparent",
                        text_color=self.clrs.NEUTRAL_300,
                        hover_color=self.clrs.NEUTRAL_700,
                    )

    def create_sidebar(self):
        """Create the sidebar with navigation"""

        self.sidebar = CTkFrame(
            master=self.app,
            fg_color=self.clrs.NEUTRAL_800,
            corner_radius=0,
            width=220,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = CTkFrame(master=self.sidebar, fg_color="transparent", height=120)
        logo_frame.pack(fill="x", padx=20, pady=(30, 20))

        app_title = CTkLabel(
            master=logo_frame,
            text="Fokus",
            font=self.header_font,
            text_color=self.clrs.PRIMARY,
        )
        app_title.pack(anchor="w")

        app_tagline = CTkLabel(
            master=logo_frame,
            text="Excuses die here.",
            font=self.tooltip_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        app_tagline.pack(anchor="w", pady=(0, 10))

        self.focus_nav_btn = self.create_nav_button(
            "Fokus Timer", self.show_setup_view, True
        )
        self.stats_nav_btn = self.create_nav_button(
            "Statistics", self.show_statistics_view
        )
        self.settings_nav_btn = self.create_nav_button(
            "Settings", lambda: self.show_settings_view(True)
        )

        footer_frame = CTkFrame(master=self.sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=30)

        total_focus_label = CTkLabel(
            master=footer_frame,
            text="TOTAL FOCUS TIME",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        total_focus_label.pack(anchor="w")

        self.total_focus_time_var = StringVar(value="00h 00m")
        self.total_focus_display = CTkLabel(
            master=footer_frame,
            textvariable=self.total_focus_time_var,
            font=self.stats_font,
            text_color=self.clrs.PRIMARY,
        )
        self.total_focus_display.pack(anchor="w", pady=(5, 0))

    def create_nav_button(self, text, command, is_active=False):
        """Create a navigation button for the sidebar"""
        btn_frame = CTkFrame(master=self.sidebar, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2)

        btn = CTkButton(
            master=btn_frame,
            text=text,
            font=self.button_font,
            fg_color=self.clrs.PRIMARY if is_active else "transparent",
            text_color=self.clrs.FG_COLOR if is_active else self.clrs.NEUTRAL_300,
            hover_color=self.clrs.PRIMARY_DARK if is_active else self.clrs.NEUTRAL_700,
            corner_radius=8,
            height=45,
            anchor="w",
            command=command,
        )
        btn.pack(fill="x", padx=10)
        return btn

    def create_main_container(self):
        """Create the main container for content"""
        self.main_container = CTkFrame(
            master=self.app,
            fg_color="transparent",
        )
        self.main_container.pack(side="right", fill="both", expand=True)

        self.header_container = CTkFrame(
            master=self.main_container,
            fg_color="transparent",
            height=70,
        )
        self.header_container.pack(fill="x", padx=40, pady=(30, 0))

        self.content_container = CTkFrame(
            master=self.main_container,
            fg_color="transparent",
        )
        self.content_container.pack(fill="both", expand=True, padx=40, pady=20)

    def show_setup_view(self):
        """Display the timer setup view"""
        self.current_view = "setup"

        # hack v2
        self.stop_sound()

        self.update_navigation("Fokus Timer")

        for widget in self.header_container.winfo_children():
            widget.destroy()

        header_title = CTkLabel(
            master=self.header_container,
            text="Fokus Timer",
            font=self.header_font,
            text_color=self.clrs.FG_COLOR,
        )
        header_title.pack(anchor="w")

        header_subtitle = CTkLabel(
            master=self.header_container,
            text="Set the timer. Make it count",
            font=self.subheader_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        header_subtitle.pack(anchor="w")

        for widget in self.content_container.winfo_children():
            widget.destroy()

        setup_container = CTkFrame(
            master=self.content_container,
            fg_color=self.clrs.NEUTRAL_800,
            corner_radius=15,
        )
        setup_container.pack(expand=True, fill="both", pady=20)

        center_frame = CTkFrame(master=setup_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        presets_frame = CTkFrame(master=center_frame, fg_color="transparent")
        presets_frame.pack(pady=(0, 30))

        presets_label = CTkLabel(
            master=presets_frame,
            text="QUICK PRESETS",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        presets_label.pack(pady=(0, 10))

        preset_buttons_frame = CTkFrame(master=presets_frame, fg_color="transparent")
        preset_buttons_frame.pack()

        self.create_preset_button(preset_buttons_frame, "10 min", 10, 00)
        self.create_preset_button(preset_buttons_frame, "25 min", 25, 00)
        self.create_preset_button(preset_buttons_frame, "30 min", 30, 00)
        self.create_preset_button(preset_buttons_frame, "45 min", 45, 00)
        self.create_preset_button(preset_buttons_frame, "1 hour", 00, 1)
        self.create_preset_button(preset_buttons_frame, "2 hours", 00, 2)

        time_frame = CTkFrame(master=center_frame, fg_color="transparent")
        time_frame.pack(pady=10)

        time_input_label = CTkLabel(
            master=time_frame,
            text="CUSTOM DURATION",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        time_input_label.pack(pady=(0, 15))

        time_inputs = CTkFrame(master=time_frame, fg_color="transparent")
        time_inputs.pack()

        hours_container = CTkFrame(master=time_inputs, fg_color="transparent")
        hours_container.pack(side="left", padx=(0, 20))

        self.hours_entry = CTkEntry(
            master=hours_container,
            placeholder_text="00",
            width=125,
            height=100,
            font=self.timer_font,
            fg_color=self.clrs.NEUTRAL_700,
            border_color=self.clrs.NEUTRAL_600,
            border_width=1,
            text_color=self.clrs.FG_COLOR,
            placeholder_text_color=self.clrs.NEUTRAL_500,
            justify="center",
            corner_radius=12,
        )
        self.hours_entry.pack()

        self.hours_label = CTkLabel(
            master=hours_container,
            text="HOURS",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        self.hours_label.pack(anchor="center", pady=(5, 0))

        minutes_container = CTkFrame(master=time_inputs, fg_color="transparent")
        minutes_container.pack(side="left")

        self.minutes_entry = CTkEntry(
            master=minutes_container,
            placeholder_text="00",
            width=125,
            height=100,
            font=self.timer_font,
            fg_color=self.clrs.NEUTRAL_700,
            border_color=self.clrs.NEUTRAL_600,
            border_width=1,
            text_color=self.clrs.FG_COLOR,
            placeholder_text_color=self.clrs.NEUTRAL_500,
            justify="center",
            corner_radius=12,
        )
        self.minutes_entry.pack()

        self.minutes_label = CTkLabel(
            master=minutes_container,
            text="MINUTES",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        self.minutes_label.pack(anchor="center", pady=(5, 0))

        self.status_label = CTkLabel(
            master=center_frame,
            text="",
            font=self.label_font,
            text_color=self.clrs.WARNING,
        )
        self.status_label.pack(pady=20)

        self.start_button = CTkButton(
            master=center_frame,
            text="START FOCUS SESSION",
            font=self.button_font,
            corner_radius=30,
            fg_color=self.clrs.PRIMARY,
            text_color=self.clrs.FG_COLOR,
            hover_color=self.clrs.PRIMARY_DARK,
            height=50,
            width=250,
            command=self.start_countdown,
        )
        self.start_button.pack(pady=10)

        motivation = CTkLabel(
            master=setup_container,
            text=self.quotes.get_random_quote(),
            font=self.tooltip_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        motivation.pack(side="bottom", pady=15)

    def create_preset_button(self, master, text, mins=0, hours=0):
        """Create a preset time button"""
        btn = CTkButton(
            master=master,
            text=text,
            font=self.label_font,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            corner_radius=8,
            width=70,
            height=35,
            command=lambda: self.set_preset_time(hours, mins),
        )
        btn.pack(side="left", padx=5)

    def set_preset_time(self, hours, minutes):
        """Set time from a preset button"""
        self.hours_entry.delete(0, "end")
        self.minutes_entry.delete(0, "end")

        if hours > 0:
            self.hours_entry.insert("00", str(hours))

        if minutes > 0:
            self.minutes_entry.insert("00", str(minutes))

    def show_countdown_view(self):
        """Display the countdown view"""
        self.current_view = "countdown"
        self.update_navigation("Fokus Timer")

        for widget in self.header_container.winfo_children():
            widget.destroy()

        header_title = CTkLabel(
            master=self.header_container,
            text="Fokus Session",
            font=self.header_font,
            text_color=self.clrs.FG_COLOR,
        )
        header_title.pack(anchor="w")

        header_subtitle = CTkLabel(
            master=self.header_container,
            text=self.quotes.get_random_header(),
            font=self.subheader_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        header_subtitle.pack(anchor="w")

        for widget in self.content_container.winfo_children():
            widget.destroy()

        countdown_container = CTkFrame(
            master=self.content_container,
            fg_color=self.clrs.NEUTRAL_800,
            corner_radius=15,
        )
        countdown_container.pack(expand=True, fill="both", pady=20)

        center_frame = CTkFrame(master=countdown_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        status_frame = CTkFrame(
            master=center_frame,
            fg_color=self.clrs.PRIMARY,
            corner_radius=20,
            height=40,
            width=150,
        )
        status_frame.pack_propagate(False)
        status_frame.pack(pady=(0, 30))

        status_label = CTkLabel(
            master=status_frame,
            text="FOCUSING",
            font=self.button_font,
            text_color=self.clrs.FG_COLOR,
        )
        status_label.place(relx=0.5, rely=0.5, anchor="center")

        self.countdown_label = CTkLabel(
            master=center_frame,
            text="00:00:00",
            font=self.timer_font,
            text_color=self.clrs.FG_COLOR,
        )
        self.countdown_label.pack(pady=20)

        self.progress_frame = CTkFrame(master=center_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(10, 30))

        self.progress_bar = CTkProgressBar(
            master=self.progress_frame,
            width=400,
            height=10,
            corner_radius=5,
            fg_color=self.clrs.NEUTRAL_700,
            progress_color=self.clrs.PRIMARY,
        )
        self.progress_bar.pack()
        self.progress_bar.set(1.0)

        buttons_frame = CTkFrame(master=center_frame, fg_color="transparent")
        buttons_frame.pack(pady=(20, 0))

        self.pause_button = CTkButton(
            master=buttons_frame,
            text="PAUSE",
            font=self.button_font,
            corner_radius=30,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            height=50,
            width=130,
            command=self.toggle_pause,
        )
        self.pause_button.pack(side="left", padx=(0, 10))

        self.cancel_button = CTkButton(
            master=buttons_frame,
            text="END SESSION",
            font=self.button_font,
            corner_radius=30,
            fg_color=self.clrs.DANGER,
            text_color=self.clrs.FG_COLOR,
            hover_color="#E11D48",
            height=50,
            width=130,
            command=self.cancel_countdown,
        )
        self.cancel_button.pack(side="left")

        note_frame = CTkFrame(master=countdown_container, fg_color="transparent")
        note_frame.pack(side="bottom", fill="x", padx=30, pady=20)

        note_label = CTkLabel(
            master=note_frame,
            text=self.quotes.get_random_focus_tips(),
            font=self.tooltip_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        note_label.pack()

    def show_completion_view(self):
        """Display the completion view"""

        self.update_navigation("Focus Timer")

        self.play_sound()

        for widget in self.header_container.winfo_children():
            widget.destroy()

        header_title = CTkLabel(
            master=self.header_container,
            text="Session Complete",
            font=self.header_font,
            text_color=self.clrs.FG_COLOR,
        )
        header_title.pack(anchor="w")

        header_subtitle = CTkLabel(
            master=self.header_container,
            text=self.quotes.get_random_success(),
            font=self.subheader_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        header_subtitle.pack(anchor="w")

        for widget in self.content_container.winfo_children():
            widget.destroy()

        completion_container = CTkFrame(
            master=self.content_container,
            fg_color=self.clrs.NEUTRAL_800,
            corner_radius=15,
        )
        completion_container.pack(expand=True, fill="both", pady=20)

        center_frame = CTkFrame(master=completion_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        success_badge = CTkFrame(
            master=center_frame,
            fg_color=self.clrs.SUCCESS,
            corner_radius=50,
            width=100,
            height=100,
        )
        success_badge.pack_propagate(False)
        success_badge.pack(pady=(0, 30))

        checkmark = CTkLabel(
            master=success_badge,
            text="✓",
            font=CTkFont(size=60, weight="bold"),
            text_color=self.clrs.FG_COLOR,
        )
        checkmark.place(relx=0.5, rely=0.5, anchor="center")

        success_title = CTkLabel(
            master=center_frame,
            text=self.quotes.get_random_success(),
            font=CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color=self.clrs.FG_COLOR,
        )
        success_title.pack(pady=(0, 10))

        stats_frame = CTkFrame(
            master=center_frame,
            fg_color=self.clrs.NEUTRAL_700,
            corner_radius=15,
        )
        stats_frame.pack(pady=20, fill="x", expand=True)

        time_stat_frame = CTkFrame(master=stats_frame, fg_color="transparent")
        time_stat_frame.pack(padx=30, pady=20)

        hours, remainder = divmod(self.current_session_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            session_time_str = f"{hours}h {minutes}m"
        else:
            session_time_str = f"{minutes}m {seconds}s"

        time_label = CTkLabel(
            master=time_stat_frame,
            text="SESSION LENGTH",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        time_label.pack(anchor="w")

        time_value = CTkLabel(
            master=time_stat_frame,
            text=session_time_str,
            font=self.stats_font,
            text_color=self.clrs.PRIMARY,
        )
        time_value.pack(anchor="w")

        buttons_frame = CTkFrame(master=center_frame, fg_color="transparent")
        buttons_frame.pack(pady=(30, 0))

        stats_button = CTkButton(
            master=buttons_frame,
            text="VIEW STATISTICS",
            font=self.button_font,
            corner_radius=30,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            height=50,
            width=180,
            command=self.show_statistics_view,
        )
        stats_button.pack(side="left", padx=(0, 10))

        new_session_button = CTkButton(
            master=buttons_frame,
            text="NEW SESSION",
            font=self.button_font,
            corner_radius=30,
            fg_color=self.clrs.SUCCESS,
            text_color=self.clrs.FG_COLOR,
            hover_color=self.clrs.SUCCESS_DARK,
            height=50,
            width=180,
            command=self.show_setup_view,
        )
        new_session_button.pack(side="left")

        self.update_total_focus_time()

    def show_statistics_view(self):
        """Display the statistics view"""

        # hack
        self.stop_sound()

        self.current_view = "statistics"
        self.update_navigation("Statistics")

        for widget in self.header_container.winfo_children():
            widget.destroy()

        header_title = CTkLabel(
            master=self.header_container,
            text="Focus Statistics",
            font=self.header_font,
            text_color=self.clrs.FG_COLOR,
        )
        header_title.pack(anchor="w")

        header_subtitle = CTkLabel(
            master=self.header_container,
            text="Track your productivity progress",
            font=self.subheader_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        header_subtitle.pack(anchor="w")

        for widget in self.content_container.winfo_children():
            widget.destroy()

        stats_container = CTkScrollableFrame(
            master=self.content_container,
            fg_color=self.clrs.NEUTRAL_800,
            corner_radius=15,
        )
        stats_container.pack(expand=True, fill="both", pady=20)

        summary_frame = CTkFrame(master=stats_container, fg_color="transparent")
        summary_frame.pack(fill="x", padx=30, pady=30)

        summary_title = CTkLabel(
            master=summary_frame,
            text="FOCUS SUMMARY",
            font=CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=self.clrs.FG_COLOR,
        )
        summary_title.pack(anchor="w", pady=(0, 15))

        stats_cards = CTkFrame(master=summary_frame, fg_color="transparent")
        stats_cards.pack(fill="x")

        self.create_stat_card(
            stats_cards,
            "TOTAL FOCUS TIME",
            self.format_time(self.total_focus_time),
            self.clrs.SUCCESS,
        )

        avg_time = self.total_focus_time // max(len(self.DB.focus_times), 1)
        self.create_stat_card(
            stats_cards,
            "AVERAGE",
            self.format_time(avg_time),
            self.clrs.PRIMARY,
        )

        self.create_stat_card(
            stats_cards,
            "COMPLETED",
            str(len(self.DB.focus_times)),
            self.clrs.WARNING,
        )

        sessions_frame = CTkFrame(master=stats_container, fg_color="transparent")
        sessions_frame.pack(fill="x", padx=30, pady=20)

        sessions_title = CTkLabel(
            master=sessions_frame,
            text="RECENT SESSIONS",
            font=CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=self.clrs.FG_COLOR,
        )
        sessions_title.pack(anchor="w", pady=(0, 15))

        if not self.DB.focus_times:
            no_data = CTkLabel(
                master=sessions_frame,
                text="No sessions recorded yet. Complete a focus session to see data here.",
                font=self.label_font,
                text_color=self.clrs.NEUTRAL_400,
            )
            no_data.pack(pady=20)
        else:
            total_sessions = len(self.DB.dates)
            for i, (session_date, session_time) in enumerate(
                reversed(list(zip(self.DB.dates, self.DB.focus_times))),
            ):
                self.create_session_item(
                    sessions_frame, total_sessions - i, int(session_time), session_date
                )

    def create_stat_card(self, master, title, value, color):
        """Create a statistics card"""
        card = CTkFrame(
            master=master,
            fg_color=self.clrs.NEUTRAL_700,
            corner_radius=10,
        )
        card.pack(side="left", padx=(0, 15), pady=5, fill="both", expand=True)

        card_title = CTkLabel(
            master=card,
            text=title,
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        card_title.pack(anchor="w", padx=15, pady=(15, 5))

        card_value = CTkLabel(
            master=card,
            text=value,
            font=self.stats_font,
            text_color=color,
        )
        card_value.pack(anchor="w", padx=15, pady=(0, 15))

    def create_session_item(self, master, number, session_time, session_date=""):
        """Create a session history item with rename and delete options"""
        item = CTkFrame(
            master=master,
            fg_color=self.clrs.NEUTRAL_700,
            corner_radius=10,
            height=60,
        )
        item.pack(fill="x", pady=5)
        item.pack_propagate(False)

        display_date = (
            session_date if session_date else datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        session_name = f"Session #{number}"
        if hasattr(self.DB, "session_names") and (number - 1) < len(
            self.DB.session_names
        ):
            session_name = self.DB.session_names[number - 1]

        session_info = CTkLabel(
            master=item,
            text=f"{session_name} • {display_date}",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
            anchor="w",
        )
        session_info.pack(side="left", padx=15, fill="x", expand=True)

        session_duration = CTkLabel(
            master=item,
            text=self.format_time(session_time),
            font=CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=self.clrs.PRIMARY,
            width=80,
            anchor="e",
        )
        session_duration.pack(side="right", padx=(10, 10))

        delete_btn = CTkButton(
            master=item,
            # God invented ascii so i'll use ascii
            text="x",
            font=CTkFont(size=16),
            fg_color=self.clrs.DANGER,
            text_color=self.clrs.FG_COLOR,
            hover_color="#E11D48",
            width=36,
            height=36,
            corner_radius=18,
            command=lambda: self.show_delete_confirmation(number - 1),
        )
        delete_btn.pack(side="right", padx=(5, 10))

        rename_btn = CTkButton(
            master=item,
            # + >>>> fucking pen emoji
            text="+",
            font=CTkFont(size=16),
            fg_color=self.clrs.PRIMARY,
            text_color=self.clrs.FG_COLOR,
            hover_color=self.clrs.PRIMARY_DARK,
            width=36,
            height=36,
            corner_radius=18,
            command=lambda: self.show_rename_dialog(number - 1),
        )
        rename_btn.pack(side="right", padx=(5, 5))

    def set_navigation_state(self, enabled=True):
        """Enable or disable navigation buttons"""
        state = "normal" if enabled else "disabled"

        if hasattr(self, "focus_nav_btn"):
            self.focus_nav_btn.configure(state=state)
        if hasattr(self, "stats_nav_btn"):
            self.stats_nav_btn.configure(state=state)
        if hasattr(self, "settings_nav_btn"):
            self.settings_nav_btn.configure(state=state)

    def show_settings_view(self, enable: bool):
        """Display the settings view"""
        self.current_view = "settings"
        self.update_navigation("Settings")
        for widget in self.header_container.winfo_children():
            widget.destroy()
        header_title = CTkLabel(
            master=self.header_container,
            text="Settings",
            font=self.header_font,
            text_color=self.clrs.FG_COLOR,
        )
        header_title.pack(anchor="w")
        header_subtitle = CTkLabel(
            master=self.header_container,
            text="Customize your experience",
            font=self.subheader_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        header_subtitle.pack(anchor="w")
        for widget in self.content_container.winfo_children():
            widget.destroy()
        settings_container = CTkFrame(
            master=self.content_container,
            fg_color=self.clrs.NEUTRAL_800,
            corner_radius=15,
        )
        settings_container.pack(expand=True, fill="both", pady=20)
        settings_tabs = CTkTabview(
            master=settings_container,
            fg_color=self.clrs.NEUTRAL_800,
            segmented_button_fg_color=self.clrs.NEUTRAL_700,
            segmented_button_selected_color=self.clrs.PRIMARY,
            segmented_button_selected_hover_color=self.clrs.PRIMARY_DARK,
            segmented_button_unselected_hover_color=self.clrs.NEUTRAL_600,
            segmented_button_unselected_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.FG_COLOR,
        )
        settings_tabs.pack(fill="both", expand=True, padx=30, pady=30)
        general_tab = settings_tabs.add("General")
        appearance_tab = settings_tabs.add("Appearance")
        notifications_tab = settings_tabs.add("Notifications")

        self.create_settings_section(general_tab, "Sound Settings")
        sound_frame = CTkFrame(master=general_tab, fg_color="transparent")
        sound_frame.pack(fill="x", pady=5)
        sound_label = CTkLabel(
            master=sound_frame,
            text="Play sound when session ends",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
        )
        sound_label.pack(side="left")

        # Create the toggle button with proper functionality
        sound_switch = CTkButton(
            master=sound_frame,
            text="ON" if self.sound_enabled else "OFF",
            font=self.label_font,
            fg_color=self.clrs.SUCCESS if self.sound_enabled else self.clrs.NEUTRAL_700,
            text_color=self.clrs.FG_COLOR
            if self.sound_enabled
            else self.clrs.NEUTRAL_300,
            hover_color=self.clrs.SUCCESS_DARK
            if self.sound_enabled
            else self.clrs.NEUTRAL_600,
            width=60,
            height=30,
            corner_radius=15,
            command=self.toggle_sound_setting,
        )
        sound_switch.pack(side="right")

        self.create_website_blocking_section(general_tab)
        self.create_settings_section(appearance_tab, "Theme Settings")
        self.create_theme_section(appearance_tab)

        self.create_settings_section(notifications_tab, "Notification Settings")

        reminder_frame = CTkFrame(master=notifications_tab, fg_color="transparent")
        reminder_frame.pack(fill="x", pady=5)
        reminder_label = CTkLabel(
            master=reminder_frame,
            text="Remind me to take breaks",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
        )
        reminder_label.pack(side="left")
        reminder_switch = CTkButton(
            master=reminder_frame,
            text="i'm pussy",
            font=self.label_font,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            width=60,
            height=30,
            corner_radius=15,
        )
        reminder_switch.pack(side="right")

        version_frame = CTkFrame(master=settings_container, fg_color="transparent")
        version_frame.pack(side="bottom", fill="x", padx=30, pady=20)
        version_label = CTkLabel(
            master=version_frame,
            # this just looks cool
            text="Focus v0.5.1",
            font=self.tooltip_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        version_label.pack(side="right")

    def create_theme_section(self, appearance_tab):
        """Create the theme selection section"""
        theme_frame = CTkFrame(master=appearance_tab, fg_color="transparent")
        theme_frame.pack(fill="x", pady=5)

        theme_label = CTkLabel(
            master=theme_frame,
            text="Application Theme",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
        )
        theme_label.pack(side="left")

        theme_buttons_frame = CTkFrame(master=theme_frame, fg_color="transparent")
        theme_buttons_frame.pack(side="right")

        dark_btn = CTkButton(
            master=theme_buttons_frame,
            text="Dark",
            font=self.label_font,
            fg_color=self.clrs.PRIMARY
            if self.current_theme == "dark"
            else self.clrs.NEUTRAL_700,
            text_color=self.clrs.FG_COLOR
            if self.current_theme == "dark"
            else self.clrs.NEUTRAL_300,
            hover_color=self.clrs.PRIMARY_DARK
            if self.current_theme == "dark"
            else self.clrs.NEUTRAL_600,
            width=80,
            height=30,
            corner_radius=15,
            command=lambda: self.change_theme("dark"),
        )
        dark_btn.pack(side="right", padx=5)

        light_btn = CTkButton(
            master=theme_buttons_frame,
            text="Light",
            font=self.label_font,
            fg_color=self.clrs.PRIMARY
            if self.current_theme == "light"
            else self.clrs.NEUTRAL_700,
            text_color=self.clrs.FG_COLOR
            if self.current_theme == "light"
            else self.clrs.NEUTRAL_300,
            hover_color=self.clrs.PRIMARY_DARK
            if self.current_theme == "light"
            else self.clrs.NEUTRAL_600,
            width=80,
            height=30,
            corner_radius=15,
            command=lambda: self.change_theme("light"),
        )
        light_btn.pack(side="right", padx=5)

        system_btn = CTkButton(
            master=theme_buttons_frame,
            text="System",
            font=self.label_font,
            fg_color=self.clrs.PRIMARY
            if self.current_theme == "system"
            else self.clrs.NEUTRAL_700,
            text_color=self.clrs.FG_COLOR
            if self.current_theme == "system"
            else self.clrs.NEUTRAL_300,
            hover_color=self.clrs.PRIMARY_DARK
            if self.current_theme == "system"
            else self.clrs.NEUTRAL_600,
            width=80,
            height=30,
            corner_radius=15,
            command=lambda: self.change_theme("system"),
        )
        system_btn.pack(side="right", padx=5)

    def create_settings_section(self, master, title):
        """Create a settings section with header"""
        section_title = CTkLabel(
            master=master,
            text=title,
            font=CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=self.clrs.FG_COLOR,
        )
        section_title.pack(anchor="w", pady=(15, 10))

        divider = CTkFrame(
            master=master,
            fg_color=self.clrs.NEUTRAL_700,
            height=1,
        )
        divider.pack(fill="x", pady=(0, 10))

    def valid_time(self):
        """Validate time inputs and convert to seconds"""
        self.status_label.configure(text="")

        hours_str = self.hours_entry.get()
        minutes_str = self.minutes_entry.get()

        if hours_str == "" and minutes_str == "":
            self.status_label.configure(
                text="You think typing nothing will lock you in? Dumbass, focus or quit."
            )
            return None

        try:
            hours = int(hours_str) if hours_str else 0
            minutes = int(minutes_str) if minutes_str else 0

            if hours < 0 or minutes < 0:
                self.status_label.configure(
                    text="Negative time? Did your brain short-circuit or what?"
                )
                return None

            if minutes >= 60:
                self.status_label.configure(
                    text="Bro, 60 minutes is an hour. Stop wasting time pretending to work."
                )
                return None

            total_seconds = hours * 3600 + minutes * 60

            if total_seconds == 0:
                self.status_label.configure(
                    text="Zero minutes? Either quit whining or actually try."
                )
                return None

            return total_seconds

        except ValueError:
            self.status_label.configure(
                text="Typing letters? Congrats, you just lost focus before you started."
            )
            return None

    def start_countdown(self):
        """Start the countdown process"""
        if self.countdown_running:
            return

        total_seconds = self.valid_time()
        if total_seconds is None:
            return

        self.current_session_seconds = total_seconds

        if self.settings_manager.get("website_blocking_enabled", False) and hasattr(
            self, "website_blocker"
        ):
            if not self.website_blocker.is_admin():
                self.status_label.configure(
                    text="Admin privileges required for website blocking. Run as administrator."
                )
                return

            if not self.website_blocker.start_blocking():
                self.status_label.configure(
                    text="Failed to start website blocking. Check permissions."
                )
                return

        self.show_countdown_view()
        self.set_navigation_state(False)

        self.total_countdown_seconds = total_seconds
        self.is_finished = False
        self.countdown_running = True
        self.is_paused = False

        self.countdown_thread = threading.Thread(
            target=self.run_countdown, args=(total_seconds,)
        )
        self.countdown_thread.daemon = True
        self.countdown_thread.start()

    def run_countdown(self, seconds_remaining):
        """Run the actual countdown in a separate thread"""
        self.remaining_seconds = seconds_remaining
        start_time = time.time()
        end_time = start_time + seconds_remaining

        while self.remaining_seconds > 0 and self.countdown_running:
            if not self.is_paused:
                self.remaining_seconds = end_time - time.time()
                if self.remaining_seconds <= 0:
                    break

                hours, remainder = divmod(int(self.remaining_seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                progress = self.remaining_seconds / self.total_countdown_seconds

                self.app.after(0, lambda: self.update_countdown_ui(time_str, progress))
            else:
                end_time = time.time() + self.remaining_seconds

            time.sleep(0.1)

        if self.countdown_running and not self.is_paused:
            self.is_finished = True
            self.record_session()
            self.app.after(0, self.countdown_finished)

    def toggle_pause(self):
        """Pause or resume the countdown"""
        if not self.countdown_running:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_button.configure(text="RESUME")
            self.fuck_you_dialog(option="pause")
        else:
            self.pause_button.configure(text="PAUSE")

    def update_countdown_ui(self, time_str, progress):
        """Update UI elements during countdown"""
        self.countdown_label.configure(text=time_str)
        self.progress_bar.set(progress)

    def record_session(self):
        """Record the completed session"""

        completed_time = self.total_countdown_seconds
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.session_history.append(completed_time)
        self.DB.save_to_json(date=current_date, focus_time=str(completed_time))

        self.total_focus_time += completed_time

    def update_total_focus_time(self):
        """Update the total focus time display"""

        self.total_focus_time = sum(int(time) for time in self.DB.focus_times)

        hours, remainder = divmod(self.total_focus_time, 3600)
        minutes, _ = divmod(remainder, 60)

        self.total_focus_time_var.set(f"{hours:02d}h {minutes:02d}m")

    def countdown_finished(self):
        """Called when countdown completes"""
        self.countdown_running = False
        self.is_paused = False

        if hasattr(self, "website_blocker"):
            self.website_blocker.stop_blocking()

        self.set_navigation_state(True)
        self.show_completion_view()

    def cancel_countdown(self):
        """Cancel the running countdown"""
        if self.countdown_running:
            self.fuck_you_dialog(option="exit")

            if hasattr(self, "dialog_result") and self.dialog_result == "quit":
                self.countdown_running = False
                self.is_paused = False

                if hasattr(self, "website_blocker"):
                    self.website_blocker.stop_blocking()

                if self.countdown_thread:
                    self.countdown_thread.join(0.5)

                self.show_setup_view()
                self.set_navigation_state(True)

    def update_navigation(self, active_nav):
        """Update navigation buttons to reflect active section"""
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, CTkFrame):
                for btn_container in widget.winfo_children():
                    if isinstance(btn_container, CTkButton):
                        if btn_container.cget("text") == active_nav:
                            btn_container.configure(
                                fg_color=self.clrs.PRIMARY,
                                text_color=self.clrs.FG_COLOR,
                                hover_color=self.clrs.PRIMARY_DARK,
                            )
                        else:
                            btn_container.configure(
                                fg_color="transparent",
                                text_color=self.clrs.NEUTRAL_300,
                                hover_color=self.clrs.NEUTRAL_700,
                            )

    def format_time(self, seconds):
        """Format seconds to a readable time string"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def fuck_you_dialog(self, option: str):
        """Show brutal roast dialog when user tries to pause or quit — no mercy version."""
        from customtkinter import CTkToplevel, CTkLabel, CTkButton, CTkFrame

        self.dialog_result = None

        pause_titles = [
            "YOU’RE LOSING TO COMFORT.",
            "DISCIPLINE SLIPPING.",
            "HESITATION = FAILURE.",
            "STILL MENTALLY WEAK?",
            "YOU THINK WINNERS PAUSE?",
            "STOP PRETENDING TO GRIND.",
            "YOU'RE NOT TIRED, YOU'RE SOFT.",
            "COMFORT IS A PRISON.",
            "YOU’RE NOT PAUSING, YOU’RE LOSING.",
            "MENTAL WEAKNESS SHOWING.",
            "GRIND PAUSES? NEVER.",
            "YOU’RE SURRENDERING IN SLOW MOTION.",
            "THIS IS WHERE LOSERS BAIL.",
            "PAUSE? OR JUST GIVE UP?",
            "FEAR HIDES BEHIND THAT PAUSE.",
            "STOP PAUSING, START WINNING.",
            "YOU’RE A GHOST OF POTENTIAL.",
        ]

        exit_titles = [
            "BACK TO LOSER HABITS?",
            "YOU NEVER REALLY WANTED IT.",
            "QUITTING. AGAIN.",
            "THIS IS WHY YOU STAY BROKE.",
            "YOU'RE BUILT TO LOSE.",
            "GO AHEAD. WASTE ANOTHER DAY.",
            "EXIT = EXCUSE.",
            "YOU’RE QUITTING ON YOU.",
            "NO GLORY FOR QUITTERS.",
            "SAME SHIT, SAME FAILURE.",
            "EXIT NOW, REGRET FOREVER.",
            "QUITTING IS YOUR TRUE TALENT.",
            "EXIT = DEATH OF DREAMS.",
            "RUNNING FROM PAIN, RUNNING FROM GROWTH.",
            "LOSERS EXIT, WINNERS FIGHT.",
            "YOU’RE A LEGEND OF LETTING GO.",
        ]

        pause_roasts = [
            "Paused? Why not just admit you're scared of success?",
            "You pause every time it gets hard — no wonder you're stuck.",
            "Comfort wins again. You're folding in real time.",
            "Hesitation is the language of the lazy.",
            "Pausing doesn’t recharge you. It rewires you to give up.",
            "Your brain's begging to go soft — and you're letting it.",
            "You're not ‘taking a break’ — you're avoiding growth.",
            "You don't need rest. You need to grow the fuck up.",
            "Stop acting like the grind owes you comfort.",
            "Pause? Nah, you’re just scared of effort.",
            "Every pause is a step back from greatness.",
            "You call that a break? It’s a breakdown.",
            "Comfort’s got you in a chokehold, huh?",
            "You pause when it’s hard, losers fold early.",
            "That pause is a silent apology to failure.",
            "Mental softening in progress — keep it up.",
            "You don’t pause a grind, you surrender it.",
            "Pause now, cry later.",
            "Pausing is procrastination’s ugly cousin.",
        ]

        exit_roasts = [
            "This is why your life looks the same every year.",
            "Close the app. Close your potential. Same thing.",
            "Quitting now guarantees you stay exactly where you are.",
            "Every time you exit, your dreams fade a little more.",
            "You're not tired. You're undisciplined.",
            "You were never serious about this.",
            "You run the second it stops being easy. That’s why you lose.",
            "You’ve built a habit of quitting — congrats.",
            "Quitting is the language of the average.",
            "Exiting? You’re just running from the hard truth.",
            "Quitters write their own obituary.",
            "Exiting means you never really wanted it.",
            "Every quit adds another brick to your failure wall.",
            "Your quit streak is your legacy.",
            "Quit now, stay average forever.",
            "You exit the battlefield while others claim victory.",
            "Quitting is your version of ‘trying.’",
            "Exiting? More like surrendering to your excuses.",
            "You don’t quit the game — you lose the game.",
        ]

        shame_labels = [
            "This is the exact moment your future self will hate you for.",
            "You’re at war with your weaker self.\nDon’t let them win again.",
            "Lock in, or stay mediocre. No one’s coming to save you.",
            "Every second you waste builds the life you’ll regret.",
            "You either suffer now or suffer forever.\nMake the fucking choice.",
            "You said you wanted to change. Prove it.",
            "Discipline is earned, not given.\nKeep going.",
            "This is what separates the real from the fake.\nAct accordingly.",
            "This is the exact moment your dreams die.",
            "Your future self just facepalmed.",
            "This pause is the grave of your ambitions.",
            "You’re betraying the person you said you’d become.",
            "Mediocrity just moved in.",
            "Every second wasted builds a prison around your potential.",
            "Discipline doesn’t knock twice — don’t ignore it.",
            "Your legacy is decided right now — what’s it gonna be?",
            "You’re fighting two battles: yourself and your excuses.",
            "The hardest war is the one inside you.",
        ]

        quit_button_texts = [
            "GIVE UP LIKE ALWAYS",
            "QUIT AND STAY BROKE",
            "RUN FROM GROWTH",
            "KILL THE MOMENTUM",
            "COWARD’S EXIT",
            "GIVE UP AND STAY BASIC",
            "QUITTERS HAVE NO FUTURE",
            "DIE WITH YOUR DREAMS",
            "COWARD’S WAY OUT",
            "LOSE WITH PRIDE",
            "SAY BYE TO SUCCESS",
            "EXIT = FAILURE",
            "RUNNING SCARED",
            "NO BALLS BUTTON",
        ]

        continue_button_texts = [
            "LOCK THE FUCK IN",
            "PROVE YOU’RE DIFFERENT",
            "GRIND DOESN’T PAUSE",
            "GET BACK TO WAR",
            "FOCUS OR DIE BROKE",
        ]

        if option == "pause":
            title_text = random.choice(pause_titles)
            roast_text = random.choice(pause_roasts)
        elif option == "exit":
            title_text = random.choice(exit_titles)
            roast_text = random.choice(exit_roasts)
        else:
            title_text = "WEAK MOVE DETECTED"
            roast_text = "You’re not even sure if you're pausing or quitting.\nThat's how lost you are."

        shame_text = random.choice(shame_labels)
        quit_text = random.choice(quit_button_texts)
        continue_text = random.choice(continue_button_texts)

        dialog = CTkToplevel(self.app)
        dialog.title("NO ESCAPE")
        dialog.geometry("500x300")
        dialog.configure(fg_color=self.clrs.NEUTRAL_800)
        dialog.resizable(False, False)
        dialog.transient(self.app)
        dialog.grab_set()
        dialog.after(10, lambda: dialog.focus())

        title_label = CTkLabel(
            master=dialog,
            text=title_text,
            font=self.subheader_font,
            text_color=self.clrs.PRIMARY,
        )
        title_label.pack(pady=(20, 10))

        roast_label = CTkLabel(
            master=dialog,
            text=roast_text,
            font=self.subheader_font,
            text_color=self.clrs.WARNING,
            justify="center",
            wraplength=450,
        )
        roast_label.pack(pady=20)

        shame_label = CTkLabel(
            master=dialog,
            text=shame_text,
            font=self.subheader_font,
            text_color=self.clrs.NEUTRAL_300,
            justify="center",
        )
        shame_label.pack(pady=10)

        def quit_like_coward():
            self.dialog_result = "quit"
            dialog.destroy()

            self.countdown_running = False
            self.is_paused = False

            if hasattr(self, "website_blocker"):
                self.website_blocker.stop_blocking()

            if self.countdown_thread:
                self.countdown_thread.join(0.5)

            self.show_setup_view()
            self.set_navigation_state(True)

        def get_back_to_work():
            self.dialog_result = "continue"
            if option == "pause":
                self.toggle_pause()
            dialog.destroy()

        buttons_frame = CTkFrame(master=dialog, fg_color="transparent")
        buttons_frame.pack(pady=30)

        quit_btn = CTkButton(
            master=buttons_frame,
            text=quit_text,
            font=self.button_font,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            width=160,
            height=40,
            corner_radius=8,
            command=quit_like_coward,
        )
        quit_btn.pack(side="left", padx=(0, 20))

        continue_btn = CTkButton(
            master=buttons_frame,
            text=continue_text,
            font=self.button_font,
            fg_color=self.clrs.SUCCESS,
            text_color=self.clrs.FG_COLOR,
            hover_color=self.clrs.SUCCESS_DARK,
            width=160,
            height=40,
            corner_radius=8,
            command=get_back_to_work,
        )
        continue_btn.pack(side="left")

        dialog.bind("<Escape>", lambda e: get_back_to_work())
        dialog.after(100, lambda: continue_btn.focus())

    def show_rename_dialog(self, session_index):
        """Show dialog to rename a session"""
        from customtkinter import CTkToplevel

        dialog = CTkToplevel(self.app)
        dialog.title("Rename Session")
        dialog.geometry("400x250")
        dialog.configure(fg_color=self.clrs.NEUTRAL_900)
        dialog.resizable(False, False)
        dialog.transient(self.app)
        dialog.grab_set()
        dialog.after(10, lambda: dialog.focus())

        title_label = CTkLabel(
            master=dialog,
            text="Enter new session name:",
            font=self.subheader_font,
            text_color=self.clrs.FG_COLOR,
        )
        title_label.pack(pady=20)

        current_name = f"Session #{session_index + 1}"
        if hasattr(self.DB, "session_names") and session_index < len(
            self.DB.session_names
        ):
            current_name = self.DB.session_names[session_index]

        name_entry = CTkEntry(
            master=dialog,
            width=300,
            height=40,
            font=self.label_font,
            fg_color=self.clrs.NEUTRAL_700,
            border_color=self.clrs.NEUTRAL_600,
            text_color=self.clrs.FG_COLOR,
        )
        name_entry.pack(pady=10)
        name_entry.insert(0, current_name)

        char_counter = CTkLabel(
            master=dialog,
            text=f"{len(current_name)}/19",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
        )
        char_counter.pack(pady=(0, 10))

        def on_text_change(*args):
            current_text = name_entry.get()
            char_count = len(current_text)

            char_counter.configure(text=f"{char_count}/19")

            if char_count > 19:
                char_counter.configure(text_color="#FF4444")
                name_entry.configure(border_color="#FF4444")
            elif char_count >= 17:
                char_counter.configure(text_color="#FFAA00")
                name_entry.configure(border_color=self.clrs.NEUTRAL_600)
            else:
                char_counter.configure(text_color=self.clrs.FG_COLOR)
                name_entry.configure(border_color=self.clrs.NEUTRAL_600)

            if char_count > 19:
                name_entry.delete(19, "end")

        name_entry.bind("<KeyRelease>", on_text_change)
        name_entry.bind("<KeyPress>", lambda e: dialog.after(1, on_text_change))

        dialog.after(100, lambda: name_entry.focus())
        dialog.after(110, lambda: name_entry.select_range(0, "end"))

        def save_rename():
            new_name = name_entry.get().strip()
            if new_name:
                if not hasattr(self.DB, "session_names"):
                    self.DB.session_names = [
                        f"Session #{i + 1}" for i in range(len(self.DB.focus_times))
                    ]

                while len(self.DB.session_names) <= session_index:
                    self.DB.session_names.append(
                        f"Session #{len(self.DB.session_names) + 1}"
                    )

                self.DB.session_names[session_index] = new_name
                try:
                    self.DB.save_session_names()
                except AttributeError:
                    pass

                self.show_statistics_view()
            dialog.destroy()

        def cancel_rename():
            dialog.destroy()

        buttons_frame = CTkFrame(master=dialog, fg_color="transparent")
        buttons_frame.pack(pady=20)

        cancel_btn = CTkButton(
            master=buttons_frame,
            text="Cancel",
            font=self.button_font,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            width=100,
            height=40,
            corner_radius=8,
            command=cancel_rename,
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = CTkButton(
            master=buttons_frame,
            text="Save",
            font=self.button_font,
            fg_color=self.clrs.SUCCESS,
            text_color=self.clrs.FG_COLOR,
            hover_color=self.clrs.SUCCESS_DARK,
            width=100,
            height=40,
            corner_radius=8,
            command=save_rename,
        )
        save_btn.pack(side="left")

        name_entry.bind("<Return>", lambda e: save_rename())
        dialog.bind("<Escape>", lambda e: cancel_rename())

    def show_delete_confirmation(self, session_index):
        """Show confirmation dialog for deleting a session"""
        from customtkinter import CTkToplevel

        dialog = CTkToplevel(self.app)
        dialog.title("Delete Session")
        dialog.geometry("400x200")
        dialog.configure(fg_color=self.clrs.NEUTRAL_900)
        dialog.resizable(False, False)

        dialog.transient(self.app)
        dialog.grab_set()
        dialog.after(10, lambda: dialog.focus())

        warning_label = CTkLabel(
            master=dialog,
            text="Are you sure you want to delete this session?",
            font=self.subheader_font,
            text_color=self.clrs.FG_COLOR,
        )
        warning_label.pack(pady=20)

        subtitle_label = CTkLabel(
            master=dialog,
            text="This action cannot be undone.",
            font=self.label_font,
            text_color=self.clrs.NEUTRAL_400,
        )
        subtitle_label.pack(pady=(0, 20))

        def confirm_delete():
            if session_index < len(self.DB.focus_times):
                del self.DB.focus_times[session_index]
            if session_index < len(self.DB.dates):
                del self.DB.dates[session_index]
            if hasattr(self.DB, "session_names") and session_index < len(
                self.DB.session_names
            ):
                del self.DB.session_names[session_index]

            try:
                self.DB.save_all_data()
            except AttributeError:
                pass

            self.total_focus_time = sum(int(time) for time in self.DB.focus_times)
            self.update_total_focus_time()
            self.show_statistics_view()
            dialog.destroy()

        def cancel_delete():
            dialog.destroy()

        buttons_frame = CTkFrame(master=dialog, fg_color="transparent")
        buttons_frame.pack(pady=20)

        cancel_btn = CTkButton(
            master=buttons_frame,
            text="Cancel",
            font=self.button_font,
            fg_color=self.clrs.NEUTRAL_700,
            text_color=self.clrs.NEUTRAL_300,
            hover_color=self.clrs.NEUTRAL_600,
            width=100,
            height=40,
            corner_radius=8,
            command=cancel_delete,
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        delete_btn = CTkButton(
            master=buttons_frame,
            text="Delete",
            font=self.button_font,
            fg_color=self.clrs.DANGER,
            text_color=self.clrs.FG_COLOR,
            hover_color="#E11D48",
            width=100,
            height=40,
            corner_radius=8,
            command=confirm_delete,
        )
        delete_btn.pack(side="left")

        dialog.bind("<Escape>", lambda e: cancel_delete())

    def start_system_theme_monitoring(self):
        """Start monitoring system theme changes (if you want real-time updates)"""
        if self.current_theme == "system":

            def check_system_theme():
                if self.current_theme == "system":
                    new_system_theme = self.get_system_theme()
                    if (
                        hasattr(self, "active_theme")
                        and new_system_theme != self.active_theme
                    ):
                        self.setup_theme()
                        if new_system_theme == "light":
                            set_appearance_mode("light")
                        else:
                            set_appearance_mode("dark")

                        self.app.configure(fg_color=self.clrs.NEUTRAL_900)
                        self.update_sidebar_colors()

                        if hasattr(self, "current_view"):
                            current_view = self.current_view
                            if current_view == "setup":
                                self.show_setup_view()
                            elif current_view == "statistics":
                                self.show_statistics_view()
                            elif current_view == "settings":
                                self.show_settings_view(True)
                            elif current_view == "countdown":
                                self.update_countdown_colors()

                self.app.after(5000, check_system_theme)

            self.app.after(1000, check_system_theme)

    def init_website_blocker(self):
        """Initialize website blocker"""
        self.website_blocker = WebsiteBlocker(self.platform)

        blocked_sites = self.settings_manager.get("blocked_sites", [])

        # it's just to shut up ruff/pyright whatver gives me fucking error
        if blocked_sites is not None:
            for site in blocked_sites:
                self.website_blocker.add_blocked_site(site)
        else:
            print("")

    def create_website_blocking_section(self, master):
        """Create website blocking settings section"""
        self.create_settings_section(master, "Website Blocking")

        blocking_frame = CTkFrame(master=master, fg_color="transparent")
        blocking_frame.pack(fill="x", pady=5)

        blocking_label = CTkLabel(
            master=blocking_frame,
            text="Block websites during focus sessions",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
        )
        blocking_label.pack(side="left")

        blocking_enabled = self.settings_manager.get("website_blocking_enabled", False)

        def toggle_blocking():
            current = self.settings_manager.get("website_blocking_enabled", False)
            new_value = not current
            self.settings_manager.set("website_blocking_enabled", new_value)

            if new_value:
                blocking_switch.configure(
                    text="ON",
                    fg_color=self.clrs.SUCCESS,
                    hover_color=self.clrs.SUCCESS_DARK,
                )
            else:
                blocking_switch.configure(
                    text="OFF",
                    fg_color=self.clrs.NEUTRAL_700,
                    hover_color=self.clrs.NEUTRAL_600,
                )

        blocking_switch = CTkButton(
            master=blocking_frame,
            text="ON" if blocking_enabled else "OFF",
            font=self.label_font,
            fg_color=self.clrs.SUCCESS if blocking_enabled else self.clrs.NEUTRAL_700,
            text_color=self.clrs.FG_COLOR
            if blocking_enabled
            else self.clrs.NEUTRAL_300,
            hover_color=self.clrs.SUCCESS_DARK
            if blocking_enabled
            else self.clrs.NEUTRAL_600,
            width=60,
            height=30,
            corner_radius=15,
            command=toggle_blocking,
        )
        blocking_switch.pack(side="right")

        sites_frame = CTkFrame(master=master, fg_color="transparent")
        sites_frame.pack(fill="x", pady=(10, 5))

        sites_label = CTkLabel(
            master=sites_frame,
            text="Blocked websites:",
            font=self.label_font,
            text_color=self.clrs.FG_COLOR,
        )
        sites_label.pack(anchor="w")

        input_frame = CTkFrame(master=master, fg_color="transparent")
        input_frame.pack(fill="x", pady=5)

        self.site_entry = CTkEntry(
            master=input_frame,
            placeholder_text="Enter website (e.g., facebook.com)",
            width=300,
            height=35,
            font=self.label_font,
            fg_color=self.clrs.NEUTRAL_700,
            border_color=self.clrs.NEUTRAL_600,
            text_color=self.clrs.FG_COLOR,
        )
        self.site_entry.pack(side="left", padx=(0, 10))

        def add_site():
            site = self.site_entry.get().strip()
            if site and hasattr(self, "website_blocker"):
                self.website_blocker.add_blocked_site(site)

                blocked_sites = list(self.website_blocker.blocked_sites)
                self.settings_manager.set("blocked_sites", blocked_sites)

                self.site_entry.delete(0, "end")
                self.refresh_blocked_sites_list()

        add_button = CTkButton(
            master=input_frame,
            text="Add",
            font=self.label_font,
            fg_color=self.clrs.PRIMARY,
            text_color=self.clrs.FG_COLOR,
            hover_color=self.clrs.PRIMARY_DARK,
            width=80,
            height=35,
            corner_radius=8,
            command=add_site,
        )
        add_button.pack(side="left")

        self.site_entry.bind("<Return>", lambda e: add_site())

        self.sites_list_frame = CTkScrollableFrame(
            master=master, fg_color=self.clrs.NEUTRAL_700, corner_radius=8, height=150
        )
        self.sites_list_frame.pack(fill="x", pady=(10, 0))

        self.refresh_blocked_sites_list()

    def refresh_blocked_sites_list(self):
        """Refresh the blocked sites list display"""
        for widget in self.sites_list_frame.winfo_children():
            widget.destroy()

        if not hasattr(self, "website_blocker"):
            return

        for site in sorted(self.website_blocker.blocked_sites):
            site_frame = CTkFrame(master=self.sites_list_frame, fg_color="transparent")
            site_frame.pack(fill="x", pady=2)

            site_label = CTkLabel(
                master=site_frame,
                text=site,
                font=self.label_font,
                text_color=self.clrs.FG_COLOR,
                anchor="w",
            )
            site_label.pack(side="left", fill="x", expand=True, padx=(10, 0))

            def remove_site(site_to_remove=site):
                self.website_blocker.remove_blocked_site(site_to_remove)

                blocked_sites = list(self.website_blocker.blocked_sites)
                self.settings_manager.set("blocked_sites", blocked_sites)

                self.refresh_blocked_sites_list()

            remove_button = CTkButton(
                master=site_frame,
                text="×",
                font=CTkFont(size=16),
                fg_color=self.clrs.DANGER,
                text_color=self.clrs.FG_COLOR,
                hover_color="#E11D48",
                width=30,
                height=30,
                corner_radius=15,
                command=remove_site,
            )
            remove_button.pack(side="right", padx=(5, 10))

    def toggle_sound_setting(self):
        """Toggle the sound setting and refresh the settings view"""
        self.sound_enabled = not self.sound_enabled
        self.show_settings_view(True)

    def play_sound(self):
        """Play sound only if sound is enabled"""
        if not self.sound_enabled:
            return

        def _play():
            mixer.init()
            mixer.music.load("alarms/ring1.mp3")
            mixer.music.play()
            mixer.music.set_volume(1)
            while mixer.music.get_busy():
                time.sleep(0.1)
            mixer.quit()

        thread = threading.Thread(target=_play, daemon=True)
        thread.start()

    def stop_sound(self):
        """Stop sound regardless of setting"""
        mixer.init()
        mixer.music.stop()
        mixer.quit()
