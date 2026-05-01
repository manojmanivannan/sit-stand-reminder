# Sit Stand Reminder

A cross-platform application to remind you to take breaks while working.

## Description

This application cycles through 3 modes every 30 minutes:

1. Sit   — 20 minutes
2. Stand —  8 minutes
3. Walk  —  2 minutes

At the start of each 30-minute cycle it reminds you to sit. After 20 minutes, it reminds you to stand. After 8 more minutes, it reminds you to walk. After 2 more minutes, the cycle repeats.

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Running from source

```
uv sync
uv run python sit_stand_reminder.py
```

### Building a standalone binary

```
uv sync
uv run pyinstaller --clean sit_stand_reminder.spec
```

The binary will be generated under the `dist` directory.

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
