import os
import sys
import tkinter as tk
import winsound
from datetime import datetime
from time import sleep
from tkinter import messagebox

from PIL import Image, ImageTk


def get_bundle_dir() -> str:
    """Returns the directory where bundled assets are stored."""
    try:
        return getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    except NameError:
        return os.getcwd()


# Asset paths (images and sounds)
BUNDLE_DIR = get_bundle_dir()
assets = {
    "SIT DOWN": {
        "image": os.path.join(BUNDLE_DIR, "images/sit_down.png"),
        "audio": os.path.join(BUNDLE_DIR, "audio/sit.wav"),
    },
    "STAND UP": {
        "image": os.path.join(BUNDLE_DIR, "images/stand_up.png"),
        "audio": os.path.join(BUNDLE_DIR, "audio/stand.wav"),
    },
    "WALK": {
        "image": os.path.join(BUNDLE_DIR, "images/walk.png"),
        "audio": os.path.join(BUNDLE_DIR, "audio/walk.wav"),
    },
}

# Reminder minutes
SIT_FOR = 20
STAND_FOR = 8
WALK_FOR = 2

assert SIT_FOR + STAND_FOR + WALK_FOR == 30, "X + Y + Z must equal 30."

SIT_REMINDER_MINUTES = [30 - (SIT_FOR + STAND_FOR + WALK_FOR), 30]
STAND_REMINDER_MINUTES = [SIT_FOR, 30 + SIT_FOR]
WALK_REMINDER_MINUTES = [SIT_FOR + STAND_FOR, 30 + SIT_FOR + STAND_FOR]

# Counters for reminders
counters = {
    "SIT DOWN": {"completed": 0, "ignored": 0},
    "STAND UP": {"completed": 0, "ignored": 0},
    "WALK": {"completed": 0, "ignored": 0},
}

# Global mute variable
global_mute = {"mute": False}


def play_audio(title: str):
    """Plays the corresponding audio alert for a given reminder title."""
    if not global_mute["mute"]:
        winsound.PlaySound(assets[title]["audio"], winsound.SND_FILENAME)


def show_reminder(title: str):
    """Displays a reminder popup with auto-close after 60 seconds."""
    play_audio(title)

    root = tk.Tk()
    root.title(title)
    root.geometry("400x600")
    root.resizable(False, False)

    # Load Image
    img = Image.open(assets[title]["image"]).resize(
        (200, 400), Image.Resampling.LANCZOS
    )
    img_tk = ImageTk.PhotoImage(img)

    # UI Elements
    label = tk.Label(root, text=f"{title} Reminder!", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    image_label = tk.Label(root, image=img_tk)
    image_label.pack()

    message = (
        f"{'Sat down':<20}{counters['SIT DOWN']['completed']:>2} times\n"
        f"{'Stood up':<20}{counters['STAND UP']['completed']:>2} times\n"
        f"{'Ignored sitting':<20}{counters['SIT DOWN']['ignored']:2} times\n"
        f"{'Ignored standing':<17}{counters['STAND UP']['ignored']:>2} times"
    )

    msg_label = tk.Label(root, text=message, justify="left", font=("Arial", 10))
    msg_label.pack(pady=5)

    response = {"clicked": None}  # Track user response

    def mark_done():
        response["clicked"] = "Done"
        root.destroy()

    def mark_skip():
        response["clicked"] = "Skip"
        root.destroy()

    def open_settings():
        settings_win = tk.Toplevel(root)
        settings_win.title("Reminder Settings")
        settings_win.geometry("350x250")
        settings_win.resizable(False, False)

        tk.Label(
            settings_win,
            text="Set cycle (must sum to 30 minutes)",
            font=("Arial", 10, "bold"),
        ).pack(pady=10)

        tk.Label(settings_win, text="Sit for X minutes:").pack()
        sit_entry = tk.Entry(settings_win)
        sit_entry.insert(0, str(SIT_FOR))
        sit_entry.pack()

        tk.Label(settings_win, text="Stand for Y minutes:").pack()
        stand_entry = tk.Entry(settings_win)
        stand_entry.insert(0, str(STAND_FOR))
        stand_entry.pack()

        tk.Label(settings_win, text="Walk for Z minutes:").pack()
        walk_entry = tk.Entry(settings_win)
        walk_entry.insert(0, str(WALK_FOR))
        walk_entry.pack()

        def save_settings():
            global \
                SIT_REMINDER_MINUTES, \
                STAND_REMINDER_MINUTES, \
                WALK_REMINDER_MINUTES, \
                SIT_FOR, \
                STAND_FOR, \
                WALK_FOR
            try:
                x = int(sit_entry.get())
                SIT_FOR = x
                y = int(stand_entry.get())
                STAND_FOR = y
                z = int(walk_entry.get())
                WALK_FOR = z
                if x + y + z != 30:
                    messagebox.showerror("Invalid Input", "X + Y + Z must equal 30.")
                    return
                # Calculate reminder minutes for a 30-min cycle
                SIT_REMINDER_MINUTES = [0]
                STAND_REMINDER_MINUTES = [x]
                WALK_REMINDER_MINUTES = [x + y]
                # Repeat for each hour
                SIT_REMINDER_MINUTES += [m + 30 for m in SIT_REMINDER_MINUTES]
                STAND_REMINDER_MINUTES += [m + 30 for m in STAND_REMINDER_MINUTES]
                WALK_REMINDER_MINUTES += [m + 30 for m in WALK_REMINDER_MINUTES]
                settings_win.destroy()
            except Exception:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")

        tk.Button(settings_win, text="Save", command=save_settings).pack(pady=10)

    # Settings button (top right, gear icon)
    btn_settings = tk.Button(
        root, text="\u2699", command=open_settings, font=("Arial", 14), width=2
    )
    btn_settings.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)

    # Buttons
    btn_done = tk.Button(root, text="Done", command=mark_done, width=10)
    btn_done.pack(side="left", padx=20, pady=20)

    # Mute/Unmute Checkbox between buttons
    mute_var = tk.IntVar(value=1 if global_mute["mute"] else 0)

    def toggle_mute():
        global_mute["mute"] = mute_var.get() == 1

    chk = tk.Checkbutton(root, text="Mute", variable=mute_var, command=toggle_mute)
    chk.pack(side="left", padx=10, pady=20)

    btn_skip = tk.Button(root, text="Skip", command=mark_skip, width=10)
    btn_skip.pack(side="left", padx=20, pady=20)

    # Auto-close after 59 seconds
    root.after(59000, lambda: root.destroy())
    root.mainloop()

    # Update counters
    if response["clicked"] == "Done":
        counters[title]["completed"] += 1
    else:
        counters[title]["ignored"] += 1


def reminder_loop():
    """Main loop that triggers reminders at set intervals without duplicate triggers."""
    last_triggered_minute = -1

    while True:
        sleep(1)
        current_minute = datetime.now().minute

        if current_minute == last_triggered_minute:
            continue  # Skip duplicate triggers within the same minute

        last_triggered_minute = current_minute  # Update last triggered time

        if current_minute in SIT_REMINDER_MINUTES:  # Sit down reminder
            show_reminder("SIT DOWN")

        elif current_minute in STAND_REMINDER_MINUTES:  # Stand up reminder
            show_reminder("STAND UP")

        elif current_minute in WALK_REMINDER_MINUTES:  # Walk reminder
            show_reminder("WALK")


if __name__ == "__main__":
    reminder_loop()
