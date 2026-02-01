# shaper_origin_inkscape
A collection of [Inkscape](https://inkscape.org/) extensions to create routing paths used on the awesome [Shaper Origin](https://www.shapertools.com/) handheld CNC router.

The following functionalities are provided by the extensions:
* placing a [custom anchor point](https://support.shapertools.com/hc/en-us/articles/4402965445019-custom-anchors)
* assigning the [cut type](https://support.shapertools.com/hc/en-us/articles/115002894673-cut-types) and the [encoded cutting depth](https://support.shapertools.com/hc/en-us/articles/10400926390683-Encoded-depth) to selected shapes.
  This eliminates the need to remember the different color combinations for fill and stroke and lowers the risk of routing to the wrong depth. 
* generation of cut paths for [dovetail joints](https://en.wikipedia.org/wiki/Dovetail_joint) based on parameters like the number of tails, the width of the tails, the angle of the router bit etc.

## Caveat
SHAPER ORIGIN is trademark of Shaper Tools, Inc., registered in the United States and/or other jurisdictions.
Shaper Tools, Inc. is in no way associated with this software.

The software is developed as a hobby project in the hope that it will be useful but *without any warranty*; without even the implied warranty of merchantability or *fitness for a particular purpose*.

**Use at your own risk.**


## How to install
1. Click on the green button labeled "Code" at the top of this page.
2. A menu appears, click on the last line "Download ZIP".
3. Unpack the ZIP file.
4. Open Inkscape and navigate to the Preferences menu. On Windows and Linux this is in the "Edit" menu. On Mac this is called "Settings" in the "Inkscape" menu.)
5. Within the Preferences dialog click on System - a list of various directories appears.
6. Open the "User extensions" directory by clicking on the "Open" button right next to it.
7. Copy all files from the ZIP archive into this directory, i.e. the files need to be placed directly into it, not into some subfolder.
8. Restart Inkscape
9. The "Extensions" menu should now contain a submenu called "Shaper Origin", which gives access to the three plugins.


## Before you start
These are some tipps that will make it easier for you to design things for the Shaper Origin in Inkscape.

Configure the coordinate system and the dimensions in your document so that they conform to the Shaper Origin system.
* Inkscape uses a coordinate system with a y-axis that points downwards. Your Shaper Origin uses a y-axis that points upwards.
  To change this, open the Preferences menu (as described in the section ["How to install"](how-to-install)).
  Click on "Interface" in the left hand side of the dialog then remove the checkmark from the entry "Origin at upper left ..."
  You need to restart Inkscape (once) to apply this change.
* Open the document properties (Win/Linux: Ctrl-Shift-D, Mac: Command-Shift-D) and change the dimensions to Millimeter under "Front page" and "Display" (or choose Inches, if you are so inclined...).
