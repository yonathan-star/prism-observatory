THE LAST OBSERVATORY
Original AI-assisted marble-course draft for Yonathan's review
2026-10-18

A fallen star enters a broken beacon, follows two descending orbital
conduits around a ruined celestial instrument, then crosses a gateway into
the receiving chamber below. This is a fictional story embodied in real CAD
geometry. There are no lights, motors or electronics in the design.

START HERE
  renders/overview.png                  Complete model, rendered from actual STL
  The-Last-Observatory-Review.pdf         Illustrated story and geometry report
  STORY_AND_DESIGN.txt                  Narrative and concrete design decisions
  ASSISTANCE_DISCLOSURE.txt             Honest authorship and testing status
  verification/RESULTS.txt               Digital checks and their limits

EDITABLE MODEL AND MESHES
  cad/the-last-observatory.scad          Authoritative parametric OpenSCAD source
  exports/the-last-observatory.stl       Base, course, integral supports and scenery
  exports/marble-8mm.stl                Separate nominal 8 mm rolling marble

The complete course has a 144 x 144 mm footprint and is about 124.1 mm tall.
Its foundation is 3 mm thick. The source's 'part' option selects 'complete',
'marble', 'assembly', or 'track'. 'Assembly' positions the separate marble
for inspection only. 'Track' is a geometry inspection configuration, not the
complete supported print. Recheck exports after any source changes.

The rendered stone, teal and brass colors are illustrative materials. The
complete STL is one solid part; no validated multicolor print setup is supplied.
The detail image explicitly hides outer conduit geometry in one inspection
view to reveal the inner gateway. The overview and STL show the full model.

REPRODUCE ON THIS MINT MACHINE
From this package directory:

  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl \
    -o exports/the-last-observatory.stl cad/the-last-observatory.scad

  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl \
    -D 'part="marble"' -o exports/marble-8mm.stl cad/the-last-observatory.scad

  python3 tools/verify_observatory.py
  python3 tools/render_observatory.py
  python3 tools/make_review_pdf.py

The scripts use installed NumPy and Pillow. CAD export uses OpenSCAD 2021.01.
No software was installed for this task. Geometry renders use a CPU triangle
renderer and do not depend on the desktop, a display, or image generation.

REVIEW STATUS
The package prepares a digital design for human review. It is not a physical
success claim or a completed/accepted program submission. Printer-specific
slicing, temporary supports, removal access and physical rolling remain
untested. Keep the integral piers, beams and cradle; they are structural.
Inspect support generation around stacked channels and the celestial rings.
Keep temporary supports out of rolling surfaces and the receiving chamber.
No printer profile, G-code, STEP file or native Onshape document is included.
Program AI-assistance rules and exact account requirements are unverified.

The simpler Capitol Switchback version remains preserved in the separate
halflife-week2 directory beside this project. No original week-one files were
changed. Nothing has been submitted, publicly published or printed.
