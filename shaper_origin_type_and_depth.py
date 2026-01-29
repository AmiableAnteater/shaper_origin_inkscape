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
#
"""
This extension adds functionality for Shaper Origin routers.
It allows to set the cut type and cut depth for shapes in your document.
"""

import inkex
from shaper_origin_base import *


class ShaperOriginTypeAndDepthExtension(ShaperEffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--routing_type", help="Determine cut type")

        pars.add_argument("--use_depth", type=inkex.Boolean, help="Whether to add depth information to path or not.", default=True)
        pars.add_argument("--depth", type=float, default=5.0, help="Cut depth")
        pars.add_argument("--depth_dimension", help="Use metric or imperial system")
        

    def shaper_effect(self):
        routing_type = RoutingType[self.options.routing_type]
        assert routing_type is not None

        for elem in self.svg.selection:
            routing_type.apply_to(elem)
            if self.options.use_depth:
                self.add_depth_info(elem, self.options.depth, self.options.depth_dimension)
 

if __name__ == '__main__':
    ShaperOriginTypeAndDepthExtension().run()
