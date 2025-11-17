# Testing Plan - Milestone 1.2

**Extension:** YouTube Transcript Extractor v1.0.4
**Date:** November 10, 2025
**Tester:** User + AI Documentation
**Environment:** macOS (Claude Desktop)

---

## Testing Objectives

1. Verify all 4 tools work correctly
2. Test different video types and scenarios
3. Validate configuration functionality
4. Confirm file persistence works
5. Check error handling
6. Document any issues found

---

## Test Suite

### TS-001: Tool Availability Check

**Objective:** Verify all 4 tools are registered and available

**Steps:**
1. Open Claude Desktop
2. Check extension is enabled
3. List available tools

**Expected Result:**
- ✅ `youtube_extract_video` visible
- ✅ `youtube_extract_playlist` visible
- ✅ `configure_output_directory` visible
- ✅ `show_current_config` visible

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-002: Configuration Display

**Objective:** Verify current configuration can be displayed

**Test Command:**
```
Muéstrame la configuración actual de YouTube Transcript Extractor
```

**Expected Result:**
```json
{
  "output_directory": "/Users/[username]/YouTube-Transcripts",
  "extension_version": "1.0.4",
  "status": "active"
}
```

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-003: Video Extraction - English Auto-Generated

**Objective:** Test basic video transcription with English auto-generated subtitles

**Test Video:** https://www.youtube.com/watch?v=v9Rd_l6gLjU
- Language: English
- Type: Auto-generated subtitles
- Already tested: ✅ Works

**Test Command:**
```
Extrae la transcripción de https://www.youtube.com/watch?v=v9Rd_l6gLjU en formato JSON con timestamps
```

**Expected Result:**
- ✅ Metadata extracted (title, duration, views, etc.)
- ✅ Transcription text populated
- ✅ Timestamps included
- ✅ Language detected as "en"
- ✅ Method: yt-dlp (primary) or youtube-transcript-api (fallback)

**Status:** [✅] Passed (already confirmed)

**Notes:** User reported "EUREKA! funcionó!" - Full success

---

### TS-004: Video Extraction - Spanish Manual Subtitles

**Objective:** Test video with manual Spanish subtitles

**Test Video:** Find a Spanish video with manual subtitles
Suggested: https://www.youtube.com/watch?v=[Spanish educational video]

**Test Command:**
```
Extrae la transcripción en español de [URL]
```

**Expected Result:**
- ✅ Language detected as "es" or "es-ES"
- ✅ Full transcription in Spanish
- ✅ Manual subtitle preference over auto-generated

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-005: Video Extraction - Plain Text Format

**Objective:** Test plain text output (no timestamps)

**Test Command:**
```
Extrae la transcripción de https://www.youtube.com/watch?v=v9Rd_l6gLjU en formato texto plano
```

**Expected Result:**
- ✅ Transcription as continuous text
- ❌ No timestamp formatting
- ✅ Readable paragraphs

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-006: File Persistence Check

**Objective:** Verify transcriptions are saved to disk

**Steps:**
1. Extract a video transcription
2. Note the video ID from response
3. Check output directory for files

**Expected Files:**
```
~/YouTube-Transcripts/
├── [video_id]/
│   ├── metadata.json
│   ├── transcript.txt
│   └── transcript_timestamped.txt
```

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-007: Configuration Change

**Objective:** Test changing output directory

**Test Command:**
```
Configura el directorio de salida de YouTube Transcript Extractor a ~/Downloads/Transcripciones
```

**Expected Result:**
- ✅ Configuration updated
- ✅ Confirmation message
- ✅ New directory created if doesn't exist

**Verification:**
```
Muestra la configuración actual
```

Should show new path.

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-008: Video Without Transcription

**Objective:** Test error handling for videos without transcripts

**Test Video:** Find a video with no captions/subtitles
(Often: music videos, very old videos, or videos with disabled captions)

**Test Command:**
```
Extrae la transcripción de [URL sin transcripción]
```

**Expected Result:**
- ✅ Metadata still extracted
- ✅ Graceful error message
- ✅ Status: "no_transcription_available"
- ✅ No crash or exception

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-009: Playlist Extraction (Small)

**Objective:** Test playlist functionality with 3-5 videos

**Test Playlist:** Small educational playlist (3-5 videos)

**Test Command:**
```
Extrae las transcripciones de esta playlist: [URL]
```

**Expected Result:**
- ✅ All videos in playlist detected
- ✅ Each video processed sequentially
- ✅ Individual files for each video
- ✅ Summary of successes/failures

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-010: Language Detection - Multilingual Video

**Objective:** Test language detection with video that has multiple subtitle options

**Test Video:** Find video with ES, EN, FR subtitles available

**Test Commands:**
```
1. Extrae en español: [URL]
2. Extrae en inglés: [URL]
```

**Expected Result:**
- ✅ Correct language selected based on request
- ✅ Different transcription text for each language
- ✅ Language code in response matches request

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-011: Very Long Video

**Objective:** Test with long video (1+ hour)

**Test Video:** Long lecture or documentary

**Test Command:**
```
Extrae la transcripción de [long video URL]
```

**Expected Result:**
- ✅ Full transcription extracted
- ✅ File size reasonable
- ✅ No timeout or truncation

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-012: Recent Video

**Objective:** Test with very recent upload (last 24 hours)

**Test Video:** Find newly uploaded video

**Expected Result:**
- ✅ Metadata extracted
- ✅ Transcription extracted (if available)
- ⚠️ May fail if transcription not yet processed by YouTube

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-013: Invalid URL Handling

**Objective:** Test error handling for invalid URLs

**Test Commands:**
```
1. Extrae: https://www.youtube.com/watch?v=INVALID123
2. Extrae: https://not-youtube.com/video
3. Extrae: not-a-url-at-all
```

**Expected Result:**
- ✅ Graceful error message
- ✅ Clear indication of what went wrong
- ✅ No crash

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-014: Concurrent Requests

**Objective:** Test if extension handles multiple requests gracefully

**Test:**
1. Request video 1
2. Immediately request video 2 (don't wait)

**Expected Result:**
- ✅ Both process (sequentially or concurrently)
- ✅ No corruption or mixing of results
- ✅ Clear response for each

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

### TS-015: Extension Restart Stability

**Objective:** Test if extension survives Claude Desktop restart

**Steps:**
1. Extract a video
2. Quit Claude Desktop completely
3. Relaunch Claude Desktop
4. Extract another video

**Expected Result:**
- ✅ Extension still enabled
- ✅ Configuration preserved
- ✅ Functionality works after restart

**Status:** [ ] Not Started | [ ] In Progress | [ ] Passed | [ ] Failed

**Notes:**

---

## Test Results Summary

**Total Tests:** 15
**Passed:** [ ]
**Failed:** [ ]
**Skipped:** [ ]
**Success Rate:** [ ]%

---

## Issues Found

### Issue #1
**Severity:** [ ] Critical | [ ] Major | [ ] Minor | [ ] Cosmetic
**Description:**
**Steps to Reproduce:**
**Expected:**
**Actual:**
**Workaround:**

---

## Performance Metrics

**Average Extraction Time:**
- Short video (< 5 min): [ ] seconds
- Medium video (5-20 min): [ ] seconds
- Long video (> 1 hour): [ ] minutes

**Success Rate by Method:**
- yt-dlp primary: [ ]%
- yt-dlp fallback: [ ]%
- youtube-transcript-api: [ ]%

---

## Recommendations

**For v1.0.5 (if needed):**
1.
2.
3.

**For Future Versions:**
1.
2.
3.

---

## Sign-Off

**Tested By:** [ ]
**Date Completed:** [ ]
**Ready for Release:** [ ] Yes | [ ] No (see issues)

**Notes:**

---

**Next Step:** If all tests pass → Proceed to Milestone 1.3 (Release Preparation)
**If issues found:** Document, prioritize, fix critical/major issues before release
