THE LAST OBSERVATORY / CASCADE
Original AI-assisted marble-run review draft — 2026-10-18

This is a new course. It replaces the earlier repeated circular route with
a roof launch, a broad crescent, a diagonal overpass, a high switchback,
a framed machine-hall passage, a front turnaround and arcade traverse,
a lower return switchback, and an S-curve into the receiving chamber.

START HERE
  renders/overview.png          Full actual-mesh color view
  renders/clay-overview.png     Full model in one neutral material
  renders/clay-comparison.png   Earlier orbital course and new Cascade at one scale
  renders/rear-overview.png     Opposite full view
  renders/route-inspection.png  Actual channel-only inspection, architecture hidden
  renders/new-route-sketch.png  Schematic sequence and floor heights
  renders/top-plan.png          Full actual-mesh top view
  renders/details.png           Color instrument, hall and receiving finish
  renders/clay-details.png      Same details in one neutral material
  The-Last-Observatory-Review.pdf
  verification/RESULTS.txt      Measurements and practical limits

EDITABLE SOURCES
  tools/course_model.py             Authoritative new route and banking
  cad/the-last-observatory.scad      Channel profile and observatory architecture
  tools/make_supports.py            Clearance-aware support layout and deck spine
  cad/route-data.scad, supports.scad Generated CAD inputs; regenerate after edits
  exports/the-last-observatory.stl  Cleaned complete course, one connected solid
  exports/marble-8mm.stl            Separate nominal 8 mm marble

Envelope 144 x 144 x 134.2 mm. The foundation is 3 mm thick. The open
channel is 10.4 mm wide, with a 2.4 mm nominal wall. It is a banked,
flat-bottom conduit, with vertical guards for access. Renders use illustrative
stone/teal/brass colors; no multicolor print configuration is supplied.

REPRODUCE ON THIS MINT MACHINE
From this package directory:

  python3 tools/course_model.py
  python3 tools/make_supports.py
  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl \
    -o verification/raw-openscad-course.stl cad/the-last-observatory.scad
  python3 tools/clean_export.py
  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl -D 'part="marble"' \
    -o exports/marble-8mm.stl cad/the-last-observatory.scad
  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl -D 'part="track"' \
    -o verification/route-only.stl cad/the-last-observatory.scad
  python3 tools/verify_observatory.py
  python3 tools/render_observatory.py
  python3 tools/sketch_route.py
  python3 tools/make_review_pdf.py

NumPy and Pillow are used. CAD export uses installed OpenSCAD 2021.01.
No software was installed. Everything ran headlessly through filesystem tools.
The optional tools/render_comparison.py uses the preserved earlier detailed
STL in the neighboring project. That earlier mesh is not duplicated here.

The raw CAD export is preserved. clean_export.py welds float-resolution
slivers at 0.0001 mm, retriangulates collinear edges without adding surface,
and removes four detached chips totaling about 7.51 cubic mm. The maximum
coordinate movement is below 0.000085 mm. See export-cleanup.json. This
cleanup is part of the reproducible export pipeline, not a CAD design edit.

REVIEW LIMITS
The digital mesh and static sphere-envelope checks pass. This is not a
rolling simulation or proof of printability. No slicing, support removal,
stiffness test, real marble test or print was performed. Retention at speed,
friction, seams, layer steps and catch settling remain unverified.

Before a print, review support generation around the stacked channels,
arch crowns, machine hall, instrument rings and 47.5 mm screened span.
Keep temporary support out of the rolling surfaces; inspect removal access
through the hall's side cutaway and both passage ends. Printer and material
are unresolved. No profile, G-code, STEP or native Onshape file is supplied.

ASSISTANCE_DISCLOSURE.txt explains authorship and testing status. No student
hours, manual authorship, program eligibility or acceptance are claimed.
Program AI-assistance rules and exact account requirements are unverified.
Nothing has been submitted, publicly published, or printed.

All earlier revisions remain beside this folder: halflife-week2,
halflife-observatory, halflife-observatory-detailed, and
halflife-observatory-composition. No week-one files were changed.
