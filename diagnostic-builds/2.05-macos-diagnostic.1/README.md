# Speed Streak 2.05 diagnostic build

This is an optional test build for investigating unexpected Anki shutdowns.
It has not been uploaded to AnkiWeb and does not claim to fix the shutdown.

[Download the add-on](speed_streak_2_05_macos_diagnostic_1.ankiaddon).

Install the downloaded `.ankiaddon` file through Anki's **Tools → Add-ons →
Install from file**, then restart Anki. Use Anki normally. If Anki closes again,
reopen it and select **Speed Streak → Help / Feedback → Copy Support Report**.
Copy the report soon after reopening, then paste it into your reply to the developer.

The package starts from the published 2.05 archive obtained on September 30, 2026,
with internal build ID `2.05-user-requests.12`. Its diagnostic build ID is
`2.05-macos-diagnostic.1`. Its existing gameplay, visual, audio and haptic
implementation files are unchanged. Changes are limited to initialization,
the build label, the Help dialog and two diagnostic files.

Logs stay on your computer, survive reinstalling the add-on, and retain recent
events from the previous Anki session. They include technical events and build
and runtime versions, but exclude card content, card IDs, deck/profile names,
media filenames and exception messages. Nothing is uploaded automatically.

A missing shutdown marker is a clue, not a diagnosis: crashes, force quits,
power loss and logging failures can all leave a session without that marker.
The last recorded operation alone does not establish the cause of a shutdown.

Package SHA256:
`cc1b459e72d6e717d1861183d80fd7aac3f9ab9fec7f5bcd0407b403ad09992a`.
The [provenance file](speed_streak_2_05_macos_diagnostic_1.provenance.json)
records the baseline hash and the five modified package entries.

The Python and JavaScript diagnostic source is included inside the add-on archive.
