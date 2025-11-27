# Windows Installation Guide

**YouTube Transcript Extractor** - Special instructions for Windows users

---

## ⚠️ Important: Python Setup Required

Windows users need to install Python correctly **before** installing this extension.

### Quick Fix

If you're seeing this error:
```
Server disconnected
Could not attach to MCP server
```

It means Claude Desktop can't find Python. Follow the steps below.

---

## Step 1: Install Python

### Download Python

1. Go to: https://www.python.org/downloads/
2. Download **Python 3.11 or later**
3. Run the installer

### ⚠️ CRITICAL During Installation

**YOU MUST CHECK THIS BOX:**

```
☑️ Add Python to PATH
```

**Without this, the extension won't work!**

### Installation Screenshots

When you see the installer:
1. **First screen:** Check "Add python.exe to PATH" ✅
2. Click "Install Now"
3. Wait for installation to complete
4. Click "Close"

---

## Step 2: Verify Python Installation

Open **PowerShell** (not Command Prompt) and run:

```powershell
python --version
```

**Expected output:**
```
Python 3.11.x
```

If you see this, Python is correctly installed! ✅

### If Python Not Found

If you get an error like:
```
'python' is not recognized as an internal or external command
```

Then Python is not in your PATH. You have two options:

#### Option A: Reinstall Python (Easiest)

1. Uninstall Python from "Add or Remove Programs"
2. Re-download from python.org
3. **THIS TIME, CHECK "Add Python to PATH"** ✅
4. Install again

#### Option B: Add Python to PATH Manually

1. Find where Python is installed (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python311\`)
2. Open "Environment Variables":
   - Right-click "This PC" → Properties
   - Advanced system settings
   - Environment Variables
   - Under "User variables", select "Path"
   - Click "Edit"
   - Click "New"
   - Add Python path (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python311\`)
   - Add Scripts path too (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\`)
   - Click OK on all dialogs
3. **Restart your computer** (important!)
4. Try `python --version` again

---

## Step 3: Install the Extension

Once Python is working:

1. **Download** the `.mcpb` file from the release
2. **Close Claude Desktop completely** (Quit, not just close window)
3. **Double-click** the `.mcpb` file
   - Or: Claude Desktop → Settings → Extensions → Advanced → "Install Extension..."
4. **Restart Claude Desktop**

---

## Step 4: Test the Extension

Try this command in Claude:

```
Extrae la transcripción de https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Success looks like:**
- ✅ Metadata appears (title, duration, etc.)
- ✅ Transcription text is extracted
- ✅ No error messages

**Still broken looks like:**
- ❌ "Server disconnected" error
- ❌ "Could not attach to MCP server" error

If still broken, see "Troubleshooting" below.

---

## Troubleshooting

### Problem: "Server disconnected" after installing Python

**Solution:** Restart your computer and Claude Desktop

Sometimes Windows needs a full restart for PATH changes to take effect.

### Problem: Multiple Python versions installed

**Check which Python is being used:**
```powershell
where python
```

This shows all Python installations. The first one listed is what will be used.

**If you have multiple Pythons:**
- Make sure Python 3.11+ is first in PATH
- Or uninstall older versions

### Problem: Python Launcher (py) exists but python command doesn't

Windows has a "Python Launcher" (`py`) separate from the `python` command.

**Test if you have py:**
```powershell
py --version
```

**If py works but python doesn't:**

Create a symlink (requires Administrator PowerShell):
```powershell
# Run PowerShell as Administrator
New-Item -ItemType SymbolicLink -Path "C:\Windows\python.exe" -Target "C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe"
```

Replace the path with your actual Python installation path.

**Or simpler:** Just reinstall Python with "Add to PATH" checked.

### Problem: Extension works but transcriptions fail

This is a different issue. The server is running but something else is wrong.

**Check:**
1. Internet connection (needs to reach YouTube)
2. Video actually has transcriptions
3. Output directory is writable

---

## Advanced: Using Python Launcher (py)

If you prefer using the Python Launcher (`py`), you can modify the extension:

**NOT RECOMMENDED for most users.** Only if you know what you're doing.

---

## Common Windows-Specific Issues

### Issue: Antivirus blocking Python

Some antivirus software blocks Python scripts.

**Solution:**
- Add Python to antivirus exceptions
- Add Claude Desktop to antivirus exceptions

### Issue: Windows Store Python

If you installed Python from Windows Store:

**Problem:** It might not work correctly with system PATH.

**Solution:**
1. Uninstall Windows Store Python
2. Install from python.org instead
3. Check "Add Python to PATH"

### Issue: Permissions error

**Error:** "Access denied" or similar

**Solution:**
- Run Claude Desktop as Administrator (right-click → "Run as administrator")
- Or check output directory permissions

---

## Still Having Issues?

### Get More Information

Open "Developer Configuration" in Claude Desktop:
- Settings → Developer
- Look at the error message
- Check the logs

### Report the Issue

If none of this helps, please report the issue:

**Include:**
1. Python version: `python --version`
2. Where Python is installed: `where python`
3. Full error message from Claude Desktop
4. Windows version

**Report to:**
- GitHub Issues: https://github.com/SOCIUM-CR/youtube-extract-mcp-server/issues
- Include "[Windows]" in the title

---

## Summary Checklist

Before installing the extension:

- [ ] Python 3.11+ installed
- [ ] "Add Python to PATH" was checked during install
- [ ] `python --version` works in PowerShell
- [ ] Computer restarted after Python install (if PATH was changed)
- [ ] Claude Desktop completely closed before installing extension
- [ ] Extension installed (double-click .mcpb file)
- [ ] Claude Desktop restarted

If all checkboxes are checked and it still doesn't work, see Troubleshooting above.

---

## Why Is This Necessary?

Unlike Node.js (which comes with Claude Desktop), Python must be installed separately.

This extension needs Python to:
- Run the MCP server
- Install dependencies (yt-dlp, etc.)
- Process YouTube videos

Once Python is properly set up, everything else is automatic.

---

**Last Updated:** November 10, 2025
**Extension Version:** 1.0.6
**Tested On:** Windows 10, Windows 11
