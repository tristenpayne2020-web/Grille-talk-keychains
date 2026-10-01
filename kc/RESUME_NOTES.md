# Paused state (resume later)
- Packaged in Downloads\CarKeychains: 21 cars (cars_pkg.json).
- Approved-by-user specs are locked: cars/<id>/spec_APPROVED_by_user.py.
- Paused mid-batch (workflow stopped): c7_z06, g42_m240i_lci, lexus_is350, civic_11th, camry_xv80.
  Resume with car-keychains-batch4.js + batch5b_args.json (tracers reuse any partial files in their folders).
- Queued, not started (user: start later): queue_batch6.json (15 cars).
- After each batch: finalize (export, verify_plate, run_export3_all.py), add_cars_pkg.py <ids>, finalize.py.


## 2026-09-29 (after the Creality Print 7.3 update)
- Slicer settings the user asked for everything: top_shell_layers 6, wall_transition_angle 50, ironing_flow 25%, ironing_spacing 0.12 (lib/k2config.py KEYCHAIN).
- 7.3 CLI: CrealityPrint.exe --cli --slice 1 --outputdir DIR --need-gcode-file in.3mf -> DIR/plate_1.gcode (slices real multi-colour 3MFs). slicecheck.slice_3mf uses it.
- lib/verify_plate2.py = real slices of the delivered single/plate 3MFs (replaces verify_plate.py estimates).
- rebuild_all.py: rebuilds all packaged cars + NEW (c7_z06 g42_m240i_lci lexus_is350 civic_11th camry_xv80, user-approved and locked),
  checks the settings in the G-code, add_cars_pkg, finalize. Log rebuild_log.txt, status rebuild_status.json (--skip-done resumes).
- Design: batchB_args.json = queue_batch6 cars 1-5 (chiron, zonda, urus, gr86, brz), workflow run wf_bf72938e-c27, pool 3, 2 rounds.
  Next: batch6 cars 6-10 (g90_m5 f90_m5 ferrari_sf90 tesla_model3 tesla_models_plaid), 11-15 (jesko f40 huracan c6 c5), then queue_batch7.
  Snapshot specs to spec_SHOWN_<stamp>.py when showing drafts; lock approved ones as spec_APPROVED_by_user.py.
- USER: "don't change slicer settings per car - one master preset, I just add the geometry".
  lib/master_preset.py = ONE process preset "Grille Talk Keychain 0.20mm @Creality K2 0.4 nozzle" (inherits the K2 0.20mm Standard),
  installed in %APPDATA%\Creality\Creality Print\7.3\user\3477890751\process\ (+ copy & HOW_TO_USE in Downloads\CarKeychains\_MASTER_SLICER_PRESET).
  The installed preset is the source of truth (k2config.build reads it; GUI edits the user saves are picked up).
  Setting change from now on = edit the preset JSON (or user saves it in the GUI) + `python lib/apply_master.py <Downloads\CarKeychains> cars/*/out`
  (re-points / re-syncs every 3MF in seconds, no geometry rebuild). finalize.py does install + HOW_TO + apply_master at the end.
- USER removed the Pagani Zonda Cinque (stop work, drop from the list). cars/zonda_cinque left on disk, not packaged, removed from queue_batch6 + batchB_args.
- USER approved Bugatti Chiron + Lamborghini Urus exactly as shown in work/current_designs_20260929_155002.png -> run wf_bf72938e-c27 STOPPED,
  both restored from spec_SHOWN_20260929_155002.py (pixel-verified) and locked as spec_APPROVED_by_user.py (urus revision discarded ->
  work/spec_revision_discarded_lambo_urus.py). finish_cars.py --only=bugatti_chiron,lambo_urus builds/verifies/packages them.
- GR86 + BRZ: new run wf_79ea1558-861 (batchC_args.json, pool 2, 2 rounds). Next: g90_m5 f90_m5 ferrari_sf90 tesla_model3 tesla_models_plaid.
- PAUSED by the user at 16:35: GR86/BRZ run wf_79ea1558-861 stopped (resume with resumeFromRunId; completed agents are cached).
- TODO (user decision 2026-09-30, NOT started - wait until the user says continue): make NO-LOGO versions of EVERY car
  (user chose badge-free for all, trademark reasons). Add one global switch removing every badge (built-in badge types
  roundel/star/rings/shield/flags/pony/bar AND custom SHOW_BADGE badges), rebuild all packaged cars + re-verify + finalize.
  All future cars (queue_batch6/7) should be designed/packaged badge-free too (Jeep seven-slot grille = trade dress, note for Trackhawk).
- USER 2026-09-30: trackhawk REMOVED from queue_batch7. USER reports the Civic is NOT a one-swap in the slicer -> investigate + fix
  (check civic production 3MF part/filament assignment and colour changes per layer) when resuming. Do nothing until the user says continue.
- USER 2026-09-30: wants an EXTRA version of the G80 M3 and G87 M2 with aftermarket "snake eye" headlights (keep the originals too).
  Get the exact headlight style / reference photo from the user (or research) before designing. Not started.
- USER: Civic is fine (user error). queue_batch8.json = 12 new cars (viper, civic type R, F-150, Mini, Elantra N, Silverado, Escalade, X5M, X4M, Macan, Cayenne, Wrangler - Wrangler flagged: seven-slot grille trademark, ask first).
