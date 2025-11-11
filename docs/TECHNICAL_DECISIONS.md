# Technical Decisions Log

**Project:** YouTube Extract MCP Extension (Phase 1)
**Period:** November 7-10, 2025
**AI Assistant:** Claude Sonnet 4.5

This document records key technical decisions made during development and the rationale behind them.

---

## Architecture Decisions

### AD-001: Use Bash Wrapper Instead of Direct uv Command

**Context:** Initial implementation used direct `uv` command in manifest, causing "spawn uv ENOENT" errors.

**Decision:** Create `run.sh` wrapper script that:
- Searches for `uv` in common installation paths
- Falls back to Python venv if `uv` not found
- Handles first-time dependency installation

**Rationale:**
- GUI apps on macOS don't inherit terminal PATH
- Different users install `uv` in different locations
- Provides graceful fallback for users without `uv`
- Enables zero-configuration experience

**Trade-offs:**
- ✅ More reliable across different environments
- ✅ Better error handling
- ⚠️ Slightly slower first startup (one-time venv creation)
- ⚠️ Additional maintenance burden (two installation methods)

**Alternatives Considered:**
1. Direct `uv` with full path - Rejected (not portable)
2. Python-only approach - Rejected (slower than uv when available)
3. Require users to set PATH - Rejected (poor UX)

**Status:** ✅ Implemented in v1.0.1
**Files:** `.mcpb-build/server/run.sh`, `.mcpb-build/manifest.json`

---

## AD-002: Upgrade to youtube-transcript-api 1.2.3

**Context:** Initial versions used non-existent (1.1.1) then outdated (0.6.0) API versions.

**Decision:** Upgrade to latest stable version 1.2.3 (October 2025)

**Rationale:**
- Latest version has modern instance-based API
- Better maintained and supported
- Fixes bugs present in older versions
- Official PyPI recommendation

**Trade-offs:**
- ✅ Most reliable and up-to-date
- ✅ Better API design (instance methods)
- ✅ Active maintenance
- ⚠️ Requires understanding new API patterns

**Alternatives Considered:**
1. Stay on 0.6.0 - Rejected (outdated, less reliable)
2. Use 0.x latest (0.6.2) - Rejected (still old API design)

**Status:** ✅ Implemented in v1.0.4
**Files:** `.mcpb-build/server/youtube_extract_mcp.py` (PEP 723), `run.sh`

---

## AD-003: Instance Method Pattern for YouTubeTranscriptApi

**Context:** Code was calling `YouTubeTranscriptApi.list(video_id)` as class method, causing "missing argument" error.

**Decision:** Create instance first, then call method:
```python
ytt_api = YouTubeTranscriptApi()
transcript_list = ytt_api.list(video_id)
```

**Rationale:**
- This is the correct API pattern per official documentation
- Instance methods allow for future configuration options
- Matches modern Python API design conventions

**Trade-offs:**
- ✅ Correct usage per docs
- ✅ More flexible for future features
- ⚠️ Requires one extra line of code
- ✅ More Pythonic

**Alternatives Considered:**
1. Try to use as class method - Not possible (API design)
2. Monkey-patch to make it work - Rejected (fragile, unmaintainable)

**Status:** ✅ Implemented in v1.0.4
**Files:** `.mcpb-build/server/youtube_extract_mcp.py` (line 637-638)

---

## AD-004: Comprehensive PATH in Manifest Environment

**Context:** GUI apps have limited PATH, causing issues finding binaries.

**Decision:** Add comprehensive PATH to manifest env vars:
```json
"PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:${HOME}/.local/bin:${HOME}/.cargo/bin"
```

**Rationale:**
- Covers common installation locations on macOS/Linux
- Homebrew (Intel and Apple Silicon)
- Cargo (Rust toolchain)
- User local installations
- System paths

**Trade-offs:**
- ✅ High compatibility across systems
- ✅ Finds tools in most locations
- ⚠️ Long PATH string
- ⚠️ May need updates for future platforms

**Alternatives Considered:**
1. Minimal PATH - Rejected (too many failures)
2. Platform-specific PATHs - Rejected (complex, hard to maintain)
3. Dynamic PATH detection - Rejected (adds complexity)

**Status:** ✅ Implemented in v1.0.1
**Files:** `.mcpb-build/manifest.json` (env section)

---

## AD-005: Pure Python PNG Generation (No PIL Dependency)

**Context:** MCPB requires 512x512 PNG icon, but adding PIL would increase complexity.

**Decision:** Generate PNG using Python's built-in `struct` and `zlib` modules.

**Rationale:**
- No external dependencies needed
- Small code footprint (~50 lines)
- Valid PNG that passes validation
- Easier for users to modify/regenerate

**Trade-offs:**
- ✅ Zero dependencies
- ✅ Self-contained
- ✅ Educational value
- ⚠️ Limited to simple solid-color PNGs
- ⚠️ Need external tool for complex icons

**Alternatives Considered:**
1. Use PIL/Pillow - Rejected (heavy dependency)
2. Use ImageMagick - Rejected (external tool requirement)
3. Pre-generate and commit - Accepted for placeholder, but provide generation code

**Status:** ✅ Implemented in v1.0.0
**Files:** `.mcpb-build/scripts/create-icon.sh`, code in commit history

---

## AD-006: Keep Triple-Fallback System Unchanged

**Context:** Server already had working triple-fallback for transcription extraction.

**Decision:** Don't modify existing fallback logic, only fix API calls.

**Rationale:**
- Existing system already tested and proven (99%+ success rate)
- Risk of breaking working functionality
- Focus on packaging, not algorithm changes
- Separation of concerns

**Trade-offs:**
- ✅ Minimal risk
- ✅ Proven reliability
- ✅ Faster implementation
- ⚠️ Inherits any existing limitations

**Alternatives Considered:**
1. Refactor fallback system - Rejected (out of scope, risky)
2. Simplify to single method - Rejected (lower success rate)

**Status:** ✅ Maintained through all versions
**Files:** `.mcpb-build/server/youtube_extract_mcp.py` (lines 455-738)

---

## AD-007: Semantic Versioning with Rapid Iteration

**Context:** Multiple bugs required rapid version releases.

**Decision:** Use semantic versioning strictly:
- 1.0.0: Initial release
- 1.0.1-1.0.4: Patch versions for bug fixes
- Reserve 1.1.x for features (future)

**Rationale:**
- Clear version progression
- Users understand patch = bug fix
- Follows industry standards
- Easy to track which fix applies when

**Trade-offs:**
- ✅ Standard and familiar
- ✅ Clear communication
- ⚠️ Many versions in short time (but justified)

**Alternatives Considered:**
1. Use 0.x versions - Rejected (project is production-ready)
2. Beta tags (1.0.0-beta.1, etc.) - Rejected (not helpful for patches)

**Status:** ✅ Applied consistently
**Files:** All version bumps followed this pattern

---

## AD-008: Detailed CHANGELOG with Root Cause Analysis

**Context:** Rapid iteration meant users needed to understand what each version fixed.

**Decision:** Include detailed root cause analysis in CHANGELOG:
- What was wrong
- Why it was wrong
- What changed
- Impact (before/after)

**Rationale:**
- Helps users decide if they need to upgrade
- Educational value
- Transparency builds trust
- Useful for future debugging

**Trade-offs:**
- ✅ Excellent user communication
- ✅ Self-documenting bugs
- ⚠️ Takes longer to write
- ⚠️ CHANGELOG gets long

**Alternatives Considered:**
1. Brief one-liner changes - Rejected (insufficient context)
2. GitHub issues for details - Rejected (fragmented information)

**Status:** ✅ Maintained through all versions
**Files:** `.mcpb-build/CHANGELOG.md`

---

## AD-009: Branch Naming Convention Compliance

**Context:** Initial push failed with 403 error due to wrong branch name.

**Decision:** Use required naming pattern: `claude/[description]-[session-id]`

**Rationale:**
- Git server enforces this pattern
- Provides clear attribution
- Session ID enables tracking
- Prevents push failures

**Trade-offs:**
- ✅ Works with server requirements
- ✅ Clear ownership
- ⚠️ Longer branch names

**Alternatives Considered:**
1. Custom branch names - Not allowed by server
2. Push to main directly - Rejected (user wanted review first)

**Status:** ✅ Implemented immediately when discovered
**Branch:** `claude/phase1-mcpb-extension-011CUoiXLWW3AJxqTkSC88vp`

---

## AD-010: Hybrid uv/venv Approach

**Context:** Users may or may not have `uv` installed.

**Decision:** Support both installation methods automatically:
1. Try `uv` first (if available) - Fast
2. Fall back to `venv` (always available) - Reliable

**Rationale:**
- Best of both worlds
- Respects user's tool choices
- Guarantees installation works
- Performance when possible, reliability always

**Trade-offs:**
- ✅ Maximum compatibility
- ✅ Optimal performance when available
- ✅ Guaranteed to work
- ⚠️ More complex installation script
- ⚠️ Two code paths to maintain

**Alternatives Considered:**
1. uv-only - Rejected (excludes users without it)
2. venv-only - Rejected (slower than necessary)
3. Let user choose - Rejected (poor UX, adds configuration)

**Status:** ✅ Implemented in v1.0.1
**Files:** `.mcpb-build/server/run.sh` (lines 10-27)

---

## Lessons Learned

### Technical Lessons

1. **GUI vs CLI Environment**
   - GUI apps have restricted PATH on macOS
   - Always provide full paths or search mechanisms
   - Test in actual GUI environment, not just terminal

2. **API Version Specificity**
   - Check PyPI for actual available versions
   - Don't assume versions exist
   - Latest != always best, but usually is
   - Verify against source code, not examples

3. **Class vs Instance Methods**
   - Read official API documentation carefully
   - Error messages can be misleading
   - Test method invocation patterns explicitly

4. **Dependency Management**
   - PEP 723 inline metadata is powerful
   - Version constraints matter critically
   - Silent failures are worst failures

### Process Lessons

1. **Iterative User Testing Essential**
   - Real environment reveals issues dev can't predict
   - Fast feedback loops enable rapid fixes
   - User screenshots/JSON extremely valuable

2. **Documentation as Debugging Tool**
   - Detailed commit messages help track changes
   - CHANGELOG provides context for decisions
   - Comments in code prevent repeat mistakes

3. **Progressive Complexity**
   - Start simple (direct uv)
   - Add fallbacks when needed (wrapper script)
   - Don't over-engineer upfront

4. **Validation at Every Step**
   - Run mcpb validate after every manifest change
   - Build package to catch integration issues
   - Git commit provides rollback points

---

## Future Recommendations

### For Phase 2 (HTTP Transport)

**Consider:**
- Similar wrapper approach for http server startup
- Environment variable validation
- Health check endpoints
- Graceful degradation if http unavailable

**Avoid:**
- Assuming http libraries are installed
- Hard-coding ports (conflict potential)
- Skipping SSL/TLS considerations

### For Phase 3 (Remote Deployment)

**Consider:**
- Configuration validation before deployment
- Environment-specific builds
- Rollback mechanisms
- Monitoring and error reporting

**Avoid:**
- Deploying without testing in target environment
- Assuming cloud provider SDKs are intuitive
- Skipping cost estimation

---

## References

- [MCPB Specification](https://github.com/anthropics/mcpb)
- [youtube-transcript-api PyPI](https://pypi.org/project/youtube-transcript-api/)
- [youtube-transcript-api GitHub](https://github.com/jdepoix/youtube-transcript-api)
- [PEP 723 - Inline Script Metadata](https://peps.python.org/pep-0723/)
- [uv Documentation](https://github.com/astral-sh/uv)

---

**Document Maintained By:** AI Development Team
**Last Updated:** November 10, 2025
**Status:** Living Document (update as new decisions are made)
