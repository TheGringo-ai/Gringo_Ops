#!/bin/bash

APP_PATH="$HOME/Desktop/GringoGUILauncher.app"
DOCK_PLIST="$HOME/Library/Preferences/com.apple.dock.plist"

function log() {
  echo "[+] $1"
}

# Check if the app exists
if [ ! -d "$APP_PATH" ]; then
  echo "❌ App not found at: $APP_PATH"
  exit 1
fi

# Escape spaces in path for CFURLString
ESCAPED_PATH="file://$(echo "$APP_PATH" | sed 's/ /%20/g')"

# Check if the app is already in the Dock
if /usr/libexec/PlistBuddy -c "Print persistent-apps" "$DOCK_PLIST" | grep -q "$ESCAPED_PATH"; then
  log "App already in the Dock. Skipping."
  exit 0
fi

# Get current dock item count
INDEX=$(/usr/libexec/PlistBuddy -c "Print persistent-apps" "$DOCK_PLIST" | grep -c "tile-data")

log "Adding app to Dock at index $INDEX"

# Add app to Dock
/usr/libexec/PlistBuddy -c "Add :persistent-apps:$INDEX dict" "$DOCK_PLIST"
/usr/libexec/PlistBuddy -c "Add :persistent-apps:$INDEX:tile-data dict" "$DOCK_PLIST"
/usr/libexec/PlistBuddy -c "Add :persistent-apps:$INDEX:tile-data:file-data dict" "$DOCK_PLIST"
/usr/libexec/PlistBuddy -c "Add :persistent-apps:$INDEX:tile-data:file-data:_CFURLString string $ESCAPED_PATH" "$DOCK_PLIST"
/usr/libexec/PlistBuddy -c "Add :persistent-apps:$INDEX:tile-data:file-data:_CFURLStringType integer 15" "$DOCK_PLIST"
/usr/libexec/PlistBuddy -c "Add :persistent-apps:$INDEX:tile-type string file-tile" "$DOCK_PLIST"

# Reload Dock
log "Reloading Dock..."
killall Dock

log "✅ Done. App added to Dock."
