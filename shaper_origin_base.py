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
from lxml import etree
from enum import Enum


# utilizing code from https://gitlab.com/inkscape/extensions/-/merge_requests/516#diff-content-7a6d15da55d7e43d96f93f758b21b3f1b59619eb
def registerNS(prefix, url):
    """Register the given prefix as a namespace url."""
    inkex.NSS[prefix] = url
    inkex.elements._utils.SSN[url] = prefix


def add_namespace(self, prefix, url):
    """Adds an xml namespace to the xml parser with the desired prefix.

    If the prefix or url are already in use with different values, this
    function will raise an error. Remove any attributes or elements using
    this namespace before calling this function in order to rename it.

    .. versionadded:: 1.3
    """
    if self.nsmap.get(prefix, None) == url:
        registerNS(prefix, url)
        return

    # Attempt to clean any existing namespaces
    if prefix in self.nsmap or url in self.nsmap.values():
        nskeep = [k for k, v in self.nsmap.items() if k != prefix and v != url]
        etree.cleanup_namespaces(self, keep_ns_prefixes=nskeep)
        if prefix in self.nsmap:
            raise KeyError("ns prefix already used with a different url")
        if url in self.nsmap.values():
            raise ValueError("ns url already used with a different prefix")

    # These are globals, but both will overwrite previous uses.
    registerNS(prefix, url)
    etree.register_namespace(prefix, url)

    # Set and unset an attribute to add the namespace to this root element.
    self.set(f"{prefix}:temp", "1")
    self.set(f"{prefix}:temp", None)


inkex.elements._svg.SvgDocumentElement.add_namespace = add_namespace

def set_points(self, *points):
    points = " ".join(f"{p[0]},{p[1]}" for p in points)
    self.update(**{"points": points})

inkex.elements._polygons.Polygon.set_points = set_points


SHAPER_NAMESPACE_KEY = "shaper"
SHAPER_NAMESPACE_URL = "http://www.shapertools.com/namespaces/shaper"



class RoutingType(Enum):
    GUIDE = ("#0068ff", "#0068ff")
    INTERIOR = ("#ffffff", "#000000")
    EXTERIOR = ("#000000", "#000000")
    ON_LINE = (None, "#7f7f7f")
    POCKET = ("#7f7f7f", None)
    
    def __init__(self, fill, stroke):
        self.fill = inkex.colors.Color(color=fill, space="rgb")
        self.stroke = inkex.colors.Color(color=stroke, space="rgb")

    def apply_to(self, inkex_element, set_hairline=True):
        inkex_element.style.set_color(self.fill, "fill")
        inkex_element.style.set_color(self.stroke, "stroke")
        if set_hairline:
            inkex_element.style['vector-effect'] = 'non-scaling-stroke'
            inkex_element.style['-inkscape-stroke'] = 'hairline'
            #inkex_element.style['stroke-width'] = '0.2'



__FONT_SIZE__ = 4
__LINE_HEIGHT__ = __FONT_SIZE__ * 1.6

class ShaperEffectExtension(inkex.EffectExtension):
    def effect(self):
        self.svg.add_namespace(SHAPER_NAMESPACE_KEY, SHAPER_NAMESPACE_URL)
        self.shaper_effect()
        
    def shaper_effect(self):
        # type: () -> Any
        """Apply some effects on the document or local context"""
        raise NotImplementedError(f"No effect handle for {self.name}")
        
    def add_depth_info(self, element, depth, dimension):
        encoded_depth = "{:.3f}".format(depth) + dimension
        element.set("shaper:cutDepth", encoded_depth)

    def du2uu(self, doc_unit_value):
        """Converts a length specified in document units to user units."""
        return doc_unit_value / self.svg.inkscape_scale

    def du2uu_points(self, points_iterable):
        """Converts a list of x/y-tuples specified in mm to a list of tuples 
        in user units."""
        retval = [(self.du2uu(p[0]), self.du2uu(p[1])) for p in points_iterable]
        return retval

    def add_text(self, x, y, text, font_size=__FONT_SIZE__, bold=False):
        text_element = inkex.TextElement()
        tspan_element = inkex.Tspan()
        tspan_element.text = text
        text_element.append(tspan_element)

        RoutingType.GUIDE.apply_to(text_element)
        text_element.style['stroke'] = 'none'
        # For some reason this approach does not work with bold text.
        # I could not figure out why, so I tried a different solution
        font_size_uu = self.du2uu(font_size)
        text_element.style['font-size'] = f'{font_size_uu}'
        #doc_unit = self.svg.document_unit
        #text_element.style['font-size'] = f'{font_size}{doc_unit}'
        text_element.set('x', str(self.du2uu(x)))
        text_element.set('y', str(self.du2uu(y)))

        if bold:
            text_element.style["font-weight"] = "bold"

        self.svg.get_current_layer().add(text_element)

