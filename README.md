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
1. [Download the ZIP-Archive of this repo by clicking on this link.](https://github.com/AmiableAnteater/shaper_origin_inkscape/archive/refs/heads/main.zip) (You can also click on the green button labeled "Code" at the top of this page and choose "Download ZIP".)
3. Unpack the ZIP file.
4. Open Inkscape and navigate to the Preferences menu. On Windows and Linux this is in the "Edit" menu. On Mac this is called "Settings" in the "Inkscape" menu.)
5. Within the Preferences dialog click on System - a list of various directories appears.
6. Open the "User extensions" directory by clicking on the "Open" button right next to it.
7. Copy all files from the ZIP archive into this directory, i.e. the files need to be placed directly into it, not into some subfolder.
8. Restart Inkscape
9. The "Extensions" menu should now contain a submenu called "Shaper Origin", which gives access to the three plugins.


## Before you start
These are some tipps that will make it easier for you to design things for the Shaper Origin in Inkscape.

Configure the **coordinate system** and the **dimensions** in your document so that they conform to the Shaper Origin system.
* Inkscape uses a coordinate system with a y-axis that points downwards. Your Shaper Origin uses a y-axis that points upwards.
  To change this, open the Preferences menu (as described in the section ["How to install"](#how-to-install)).
  Click on "Interface" in the left hand side of the dialog then remove the checkmark from the entry "Origin at upper left ..."
  You need to restart Inkscape (once) to apply this change.
* Open the document properties (Win/Linux: Ctrl-Shift-D, Mac: Command-Shift-D) and change the dimensions to Millimeter under "Front page" and "Display" (or choose Inches, if you are so inclined...).

**Single line fonts**
From my experience single line fonts are a bit overlooked in Inkscape. There is an extension called "Herschey Text", which is part of the regular Inkscape install. It comes with two single line fonts that are not very pretty in my eyes, but do the job for guides. If you are interested in more options, see the [webpage by Cutlings](https://cutlings.datafil.no/smoothed-single-line-fonts/), which contains a few fonts that are usable with the Hershey Text extension and the very clean [Relief SingleLine](https://github.com/isdat-type/Relief-SingleLine) font, which also contains instructions how to use it with the Hershey Text plugin.


## The extensions

### Place custom anchor
This is the simplest extension. It places a red triangle - as specified by 
[the description of custom anchor points](https://support.shapertools.com/hc/en-us/articles/4402965445019-custom-anchors)
into the document. You can set the parameters for axis orientation (which is probably useless, 
but I'm still experimenting with it), placement on the page and size. You can move the anchor
after placing. If you use the plugin again, it will replace an anchor placed previously with
the plugin. It cannot replace anchors, that you have created by hand.

As the dialog for the plugin is pretty self-explanatory I feel that I can skip documenting most
of the options in the dialog. One thing though - the size of the x-axis is specified in the 
dimension that you configured in the document properties. If you followed the ["Before you start"](#before-you-start)
tipps, this should be Millimeter or Inches.

### Cut type and depth
This is the plugin that I use the most. Before implementing this plugin I always had a template file that
included all different color settings for the different cut types that the Shaper Origin is able to do
and copied them over to my designs. Using the plugin you can set these types for selected shapes as well
as pre-encode the depths for cutting.

Usage is as follows:
* Select one or more shapes and/or paths.
* Click on the menu entry for the plugin (Extensions --> Shaper Origin --> Cut type and depth).
* A dialog opens; in this dialog you can choose the cut type in the first row. Unlike Shaper Studio
  the plugin is *not* able to differenciate shapes and disable nonsensical cut types like for
  example setting an "Inside cut" for an open path. It will assign the color combination for the
  cut type that you choose - be it routable or not. (The good thing is, that you can assing the
  same cut type and cut depth to many objects at the same time.)
* The second section of the dialog allows you to pre-encode the cutting depth for the selected
  shapes. Once again, the plugin is not able to block you from nonsensical actions like assigning
  a depth to a guide. If you want to pre-encode depth, tick the checkbox "Set cut depth?", enter
  the depth and it's dimension.
* The last section of the dialog allows you a "Live preview". If you check this and change anything
  in the dialog the change will be displayed in the document.
* **Important:** If you are happy with the entered values, always use the "Apply" button. The "Close"
  button will undo current changes, even if the live preview has been activated. This is standard
  Inkscape behaviour.

### Place dovetails
This is the most complicated plugin. It is able to generate cut paths for joining to boards using
dovetails. You can specify how wide your boards are, how thick each of the boards are, the geometry
of your dovetail and your straight router bits as well as the number and width of the dovetails.

The extension is only able to generate routing paths for dovetails with the same width. If you would
like to create dovetails with different sizes, you'll have to modify the results of the extension by hand.

