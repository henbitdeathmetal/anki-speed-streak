# Speed Streak 2.05 diagnostic build — corrected installation

[Download the diagnostic add-on](speed_streak_2_05_macos_diagnostic_2.ankiaddon).

1. Download the `.ankiaddon` file and leave it as a single file; do not unzip it.
2. Open Anki and select **Tools → Add-ons → Install from file**.
3. Select the downloaded file, then fully quit and reopen Anki.
4. Use Anki normally. If it closes unexpectedly, reopen it and select
   **Speed Streak → Help / Feedback → Copy Support Report**, then paste the report
   into your reply to the developer.

You do not need to delete your AnkiWeb version first. This package uses the
existing Speed Streak AnkiWeb installation identity (`1237336370`), so Anki
replaces that copy while retaining its configuration and `user_files` through
its normal update mechanism. Quit and reopen Anki to load the replacement.
If you have multiple manually installed Speed Streak copies, ensure only the
diagnostic copy is enabled before testing; use **Toggle Enabled**, not Delete.

Build `2.05-macos-diagnostic.2` corrects the manual installation identity used
by diagnostic build `.1`. The logging code, gameplay, visuals, audio and haptics
are unchanged from diagnostic `.1`. Relative to the published baseline
`2.05-user-requests.12`, only the initialization, build label, Help dialog,
diagnostic files and installation manifest differ.

This collects local evidence; it does not claim to fix or diagnose the shutdown.
The report includes the exact build/runtime versions and recent technical
events, including the preceding session. It excludes card content, card IDs,
deck/profile names, media filenames and exception messages. Nothing is uploaded
automatically. Logs are outside the add-on installation folder, so reinstalling
preserves them.

AnkiWeb has not been updated. Reinstalling/updating from AnkiWeb replaces this
diagnostic build with the public version, so keep the diagnostic build in place
for this investigation. **Help / Feedback** shows the diagnostic build ID.

[Package provenance and SHA256](speed_streak_2_05_macos_diagnostic_2.provenance.json).

Maintainer build command:

```powershell
python -B diagnostic-builds/build_installable_diagnostic.py
```
