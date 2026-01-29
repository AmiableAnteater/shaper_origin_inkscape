#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2022, 2026 Andreas Zielke
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
This extension adds functionality for Shaper Origin routers.
It allows to add a custom anchor in your document.
"""

import inkex
from shaper_origin_anchor_utils import *

ANCHOR_ID = "shaper_origin_custom_anchor"

class ShaperOriginCustomAnchorExtension(ShaperEffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--axis_orientation", 
                          help="Set axis orientation (RT, RB, LT, LB).", 
                          default="RT")
        pars.add_argument("--x_size",
                          type=float,
                          help="Size of X-axis (Y-axis will be twice as long).",
                          default=10.0)
        pars.add_argument("--x_placement", 
                          help="X-axis position of the custom anchor (l/m/r).",
                          default="l")
        pars.add_argument("--y_placement", 
                          help="Y-axis position of the custom anchor (t/m/b).",
                          default="b")
        

    def effect(self):
        current_anchor = self.svg.getElementById(ANCHOR_ID)
        if current_anchor is not None:
            current_anchor.delete()
    
        axis_orientation = AxisOrientation[self.options.axis_orientation]
        assert axis_orientation is not None
    
        width = self.svg.viewbox_width
        translate_x = 0
        if self.options.x_placement == "m":
            translate_x = width / 2
        elif self.options.x_placement == "r":
            translate_x = width
            
        height = self.svg.viewbox_height
        translate_y = 0
        if self.options.y_placement == "m":
            translate_y = height / 2
        elif self.options.y_placement == "b":
            translate_y = height
            
        current_layer = self.svg.get_current_layer()
        inverse_layer_transform = -current_layer.composed_transform()
        origin_transform = inverse_layer_transform @ \
                inkex.transforms.Transform(
                        f"translate({translate_x:.5f}, {translate_y:.5f})") 

        x_size_uu = self.du2uu(self.options.x_size)
        elem = create_anchor_polygon(axis_orientation, x_size=x_size_uu)
        elem = current_layer.add(elem)
        elem.set_id(ANCHOR_ID)
        elem.transform = origin_transform


if __name__ == '__main__':
    ShaperOriginCustomAnchorExtension().run()
