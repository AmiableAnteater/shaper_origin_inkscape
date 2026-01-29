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

import inkex
from enum import Enum, auto
from shaper_origin_base import *


class AxisOrientation(Enum):
    """The four possible orientations of the coordinate system.
    X-axis towards right (R) or left (L), Y-axis towards top (T)
    or bottom (B)."""
    RT = auto()
    RB = auto()
    LT = auto()
    LB = auto()

 
def create_anchor_polygon(axis_orientation, x=0, y=0, x_size=10):
    """Creates a polygon that represent a custom anchor point for
    the Shaper Origin, see https://support.shapertools.com/hc/en-us/articles/4402965445019-custom-anchors"""
    assert axis_orientation is not None 
    y_size = 2 * x_size

    p0 = (x, y)
    if axis_orientation == AxisOrientation.RT:
        p1 = (x, y-y_size)
        p2 = (x+x_size, y)
    elif axis_orientation == AxisOrientation.RB:
        p1 = (x+x_size, y)
        p2 = (x, y+y_size)
    elif axis_orientation == AxisOrientation.LT:
        p1 = (x-x_size, y)
        p2 = (x, y-y_size)
    elif axis_orientation == AxisOrientation.LB:
        p1 = (x-x_size, y)
        p2 = (x, y+y_size)

    elem = inkex.Polygon()
    elem.set_points(p0, p1, p2)
    elem.style.set_color("#ff0000", "fill")
    return elem
