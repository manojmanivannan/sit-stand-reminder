import os
import sys
import tkinter as tk
import winsound
from datetime import datetime
from time import sleep

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

        if current_minute in {0, 30}:  # Sit down reminder every 30 minutes
            show_reminder("SIT DOWN")

        elif current_minute in {20, 50}:  # Stand up reminder 20 mins after sitting
            show_reminder("STAND UP")

        elif current_minute in {28, 58}:  # Walk reminder 8 mins after standing
            show_reminder("WALK")


if __name__ == "__main__":
    reminder_loop()
