CAPITOL SWITCHBACK
Original AI-assisted CAD draft for Half-Life week two
Prepared 2026-10-18 for Yonathan's review

STATUS
The CAD review package is prepared. This is not a completed, accepted, or
submitted program entry. Nothing has been printed or physically tested.
Program AI-assistance rules and the account's exact submission requirements
have not been verified. No student work hours or personal learning claims
are supplied.

OPEN FIRST
  renders/overview.png                Overall view from the actual STL meshes
  Capitol-Switchback-Review.pdf        Compact illustrated review report
  DESIGN_NOTES.txt                     Dimensions, reasoning, and pending checks
  REVIEW_WRITEUP.txt                   Honest project-description draft
  ASSISTANCE_DISCLOSURE.txt            What was generated and what remains undone

EDITABLE SOURCE AND PRINTABLE MESHES
  cad/capitol-switchback.scad          Parametric OpenSCAD source
  exports/capitol-switchback-course.stl
                                     Base, trough, posts, backstop and tray;
                                     one connected solid, millimetre units
  exports/marble-8mm.stl               Separate nominal 8 mm marble

Open the SCAD source in OpenSCAD. The 'part' parameter selects 'course',
'marble', or 'assembly'. 'Assembly' displays the marble at the inlet for
inspection only. Export course and marble separately for slicing. Recheck
the geometry after changing any dimensions. No STEP file or native Onshape
feature tree is included; OpenSCAD is the authoritative editable source.

REPRODUCE THE EXPORTS ON THIS MINT MACHINE
From this package directory, run:

  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl \
    -D 'part="course"' -o exports/capitol-switchback-course.stl \
    cad/capitol-switchback.scad

  QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
    /home/yon/.local/bin/openscad --export-format binstl \
    -D 'part="marble"' -o exports/marble-8mm.stl \
    cad/capitol-switchback.scad

  python3 tools/verify_geometry.py
  python3 tools/render_geometry.py
  python3 tools/make_review_pdf.py

The Python utilities use installed NumPy and Pillow. OpenSCAD is 2021.01.
The AppImage flags avoid FUSE and desktop use. No new software was installed.

VERIFICATION EVIDENCE
  verification/geometry-report.json   Actual STL measurements and clearance tests
  verification/RESULTS.txt             Human-readable results and scope
  verification/openscad-course.log     OpenSCAD/CGAL export evidence

The static clearance test samples an ideal 8 mm sphere from a release centre
6 mm forward of the backstop to the end of the trough, then into the tray.
This is a geometric envelope test, not a simulation or proof of successful
physical rolling. See the report for sample spacing and limits.

BEFORE ANY FUTURE PRINT
Use millimetres and preserve the course orientation with its flat base on
the bed. Keep the integral cylindrical posts: they are part of the model.
Review a printer-specific slice for unsupported undersides and bridge spans;
temporary supports may still be needed outside the rolling channel. Keep
generated supports out of the channel and catch-tray interior. Review the
marble separately for surface finish and support scars. No printer profile,
G-code, validated print settings, or physical success claim is included.

REFERENCE
The Merbl guide informed the size and clearance checks, not the course layout:
https://github.com/karnxx/merbl/blob/main/guide.md
The two-hairpin layout, retained support arrangement and catch-tray geometry
in this package were created for this request.

No existing week-one project files were changed. No submission, publication,
printer action, or DAVIS action was performed.
