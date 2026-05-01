# Sit Stand Reminder

A cross-platform desktop application to remind you to take breaks while working.

## Description

This application cycles through 3 modes every 30 minutes:

1. Sit   — 20 minutes
2. Stand —  8 minutes
3. Walk  —  2 minutes

At the start of each 30-minute cycle it reminds you to sit. After 20 minutes, it reminds you to stand. After 8 more minutes, it reminds you to walk. After 2 more minutes, the cycle repeats.

## Features

- **Persistent dashboard** — A small window shows your current phase, a live countdown to the next transition, and completion counters.
- **Themed UI** — Modern light and dark themes powered by [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap).
- **Settings dialog** — Customize cycle times, pick a theme, toggle sound, and set the reminder auto-close delay.
- **Keyboard shortcuts** — Press `Enter` to confirm, `Escape` to skip, `M` to mute, and `S` for settings inside any reminder popup.
- **Auto-close countdown** — Reminder popups show a live progress bar and close automatically if unattended.
- **Cross-platform** — Runs on Windows, macOS, and Linux.

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Running from source

```
uv sync
uv run python -m sit_stand_reminder
```

**macOS note:** If `uv` installs a standalone CPython that does not include Tcl/Tk, you may see an error like `Cannot find a usable init.tcl`. Install Tcl/Tk via Homebrew and export the paths before running:

```
brew install tcl-tk
export TCL_LIBRARY="$(brew --prefix tcl-tk)/lib/tcl9.0"
export TK_LIBRARY="$(brew --prefix tcl-tk)/lib/tk9.0"
uv run python -m sit_stand_reminder
```

End users who download the pre-built release binary do **not** need to install Tcl/Tk.

### Running tests

```
uv sync
uv run pytest tests/ -v
```

### Building a standalone binary

```
uv sync
uv run pyinstaller --clean sit_stand_reminder.spec
```

The binary will be generated under the `dist` directory.

## Configuration

Settings and counters are saved automatically to your platform's config directory:

- **macOS:** `~/Library/Application Support/sit-stand-reminder/config.json`
- **Windows:** `%APPDATA%\sit-stand-reminder\config.json`
- **Linux:** `~/.config/sit-stand-reminder/config.json`

## Downloading pre-built binaries

Get the latest binaries for your platform from the [releases page](https://github.com/manojmanivannan/sit-stand-reminder/releases).

## Autostart on login

### Windows

Place a shortcut to the `.exe` in your Windows startup folder (`Win+R` → `shell:startup`).

### Linux

Create a `.desktop` file in `~/.config/autostart/`:

```ini
[Desktop Entry]
Type=Application
Name=Sit Stand Reminder
Exec=/path/to/sit_stand_reminder
```

### macOS

Download the `sit-stand-reminder-macos.zip` from releases, extract it, and move the binary to your Applications folder (or wherever you prefer).

**First launch:** macOS Gatekeeper blocks unsigned apps. To bypass this, right-click the binary and select **Open**, then click **Open** again in the dialog. You only need to do this once. Alternatively, run this in Terminal:

```
xattr -d com.apple.quarantine /path/to/sit-stand-reminder-macos
```

For autostart, add the binary to Login Items in **System Settings → General → Login Items & Extensions**, or create a LaunchAgent plist in `~/Library/LaunchAgents/`.

## Release

Create a new release by pushing a version tag (e.g., `0.0.14`). The CI workflow will build binaries for Windows, macOS, and Linux and attach them to the release.
