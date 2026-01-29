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
It allows to create cut paths for dovetail joints.
"""

import inkex
import sys
from math import radians, tan
from shaper_origin_base import *
from shaper_origin_anchor_utils import *


# All cuts will continue through the board by the width of the router
# bit multiplied by this constant. This applies to both sides of the board.
# E.g. for 8mm straight bit a buffer of 8mm * 0.55 = 4.4mm 
__OVERCUTTING_BUFFER_FACTOR__ = .55

# An exception are the cuts using the dovetail bit. To make retraction
# safer, a buffer of the full diameter is added below the board.
__LOWER_OVERCUTTING_BUFFER_DOVETAIL_BIT_FACTOR__ = 1.0

# For cuts that reach the horizontal edge of the board, a fixed size
# buffer is used. This constants specifies the width of this buffer in mm.
__HORIZONTAL_BUFFER__ = 2

__FONT_SIZE__ = 4
__LINE_HEIGHT__ = __FONT_SIZE__ * 1.6

# This is the vertical separation of the two cutting graphics (one for the
# pin board, one for the tail board).
__VERTICAL_OFFSET_BOARDS__ = 50


class ShaperOriginDovetailsExtension(ShaperEffectExtension):
    def __init__(self):
        super().__init__()
        # The tangens of the cut angle which is used in a lot of calculation, 
        # thus computed only once.
        self.tan_cut_angle = None

        self.is_odd_number_of_tails = None

        # This is the (calculated) diameter of the dovetail bit at the top of 
        # the tails board shown in blue in the plugins dialog.
        self.upper_tail_diameter = None

        # This is the width of the dovetails at their bottom.
        self.smaller_width_tails = None

        # This is the width of the rectangles that you cut in between the 
        # dovetails - i.e. this is the width of the board minus all widths of 
        # the dovetails divided by the number of cuts between the dovetails.
        self.individual_width_of_tail_cut = None


    def add_arguments(self, pars):
        pars.add_argument("--cut_angle", type=float, default=15.0)
        pars.add_argument("--tail_bit_diameter", type=float, default=13.8)
        pars.add_argument("--pin_bit_diameter", type=float, default=8.0)
        pars.add_argument("--tail_thickness", type=float, default=15.0)
        pars.add_argument("--pin_thickness", type=float, default=15.0)
        pars.add_argument("--width", type=float, default=150.0)
        pars.add_argument("--width_tails", type=float, default=20.0)
        pars.add_argument("--num_tails", type=int, default=2)        


    def calculate_upper_tail_diameter(self):
        """Calculates how wide a cut the dovetail bit makes plunged down to 
        the thickness of the pin at the top of the board in a single pass."""
        # Example: the dovetail bit sold by Shaper has a cut angle of 15° and 
        # a diameter of 13.8mm at the bottom (i.e. the widest diameter). 
        # If you use it to cut through a board plunged down to 10mm the bottom 
        # of the cut will be 13.8mm wide (obviously) and the top of the cut at
        # the edge of the board will be 8.44mm wide. This can be calculated as
        # follows:
        # 13.8mm - 2 * tan(15°) * 10mm =
        # 13.8mm - 2 * 0.268 * 10mm =
        # 13.8mm - 5.36mm = 8.44mm        
        return self.options.tail_bit_diameter - \
            2 * self.tan_cut_angle * self.options.pin_thickness


    def num_tail_cuts(self):
        return self.options.num_tails + 1 if self.is_odd_number_of_tails else self.options.num_tails


    def add_box(self, x0, y0, x1, y1, routing_type=RoutingType.INTERIOR, depth=None):
        current_layer = self.svg.get_current_layer()
        x = str(self.du2uu(min(x0, x1)))
        y = str(self.du2uu(min(y0, y1)))
        width = str(self.du2uu(abs(x1-x0)))
        height = str(self.du2uu(abs(y1-y0)))

        box = current_layer.add(inkex.Rectangle(x=x, y=y, width=width, height=height))
        routing_type.apply_to(box)
        if depth is not None: 
            self.add_depth_info(box, depth, "mm")
        return box


    def add_polygon(self, *args):
        polygon = inkex.Polygon()
        points_in_user_units = self.du2uu_points(args)
        polygon.set_points(*points_in_user_units)
        RoutingType.INTERIOR.apply_to(polygon)
        self.add_depth_info(polygon, self.options.tail_thickness, "mm")
        return self.svg.get_current_layer().add(polygon.to_path_element())
        

    def add_tail_cuts(self, y_origin_tail_board):
        cutting_buffer_above_board = \
                self.options.tail_bit_diameter * __OVERCUTTING_BUFFER_FACTOR__
        start_y = y_origin_tail_board - cutting_buffer_above_board
        cutting_buffer_below_board = self.options.tail_bit_diameter * \
                __LOWER_OVERCUTTING_BUFFER_DOVETAIL_BIT_FACTOR__
        end_y = (y_origin_tail_board + 
                 self.options.tail_thickness + 
                 cutting_buffer_below_board)

        # Design decision: The cutting rectangles will _not_ be wider than the
        # actual cut, even though this would enable the user to specify the
        # actual/lower diameter of the dovetail bit while using the Shaper 
        # Origin. So why accept this drawback?
        # The reason is as follows: __Not__ adding extra horizontal space 
        # enables the user to make first rough cuts using a normal or even a
        # roughening straight bit without any offsets and thus minimize usage 
        # of the the dovetail bit.

        if self.is_odd_number_of_tails:
            x = self.options.width_tails/2
            while x < self.options.width:
                self.add_box(x, start_y, 
                             x + self.individual_width_of_tail_cut, end_y, 
                             RoutingType.INTERIOR, self.options.pin_thickness)
                x = x + self.individual_width_of_tail_cut + self.options.width_tails
        else:
            self.add_box(-__HORIZONTAL_BUFFER__, start_y, 
                         self.individual_width_of_tail_cut / 2, end_y,
                         RoutingType.INTERIOR, self.options.pin_thickness)        
            self.add_box(self.options.width - self.individual_width_of_tail_cut/2,
                         start_y, 
                         self.options.width + __HORIZONTAL_BUFFER__, 
                         end_y,
                         RoutingType.INTERIOR, self.options.pin_thickness)        
            x = self.individual_width_of_tail_cut/2 + self.options.width_tails
            for i in range(self.options.num_tails - 1):
                self.add_box(x, start_y, 
                             x + self.individual_width_of_tail_cut, end_y,
                             RoutingType.INTERIOR, self.options.pin_thickness)
                x = x + self.individual_width_of_tail_cut + self.options.width_tails
        return end_y
        
   
    def add_pin_cuts(self):
        """This adds trapezoid shapes for cutting pockets into the pin board."""
        # This method generates cut paths that are pockets (plus inside cuts).
        # Inside cuts alway have rounded corners, as a round bit cannot cut 
        # sharp inside corners.

        # Therefore the cuts need to be longer than the board width by more 
        # than half the straight bit cutter diameter (on both sides). This 
        # will cut into the spoil board and leaves straight edges all through 
        # the board.
        cutting_buffer_outside_of_board = \
            self.options.pin_bit_diameter * __OVERCUTTING_BUFFER_FACTOR__

        # The trapezoids will all be specified starting with the top left 
        # coordinate. All consecutive points are specified in clockwise order. 

        # As the SVG coordinate system has the y axis pointing downwards and 
        # the top left corner of the pin board is placed on the origin of the
        # coordinate system, the upper y-coordinate is:
        start_y = -cutting_buffer_outside_of_board

        # The lower ordinate is the pin board thickness plus the buffer size.
        end_y = self.options.pin_thickness + cutting_buffer_outside_of_board
        
        # To accomodate the buffering cuts on the x-Axis (as we want to 
        # continue cutting through the board at the same angle, which is equal 
        # to the cutting angle of the dovetail bit), we have to calculate the 
        # necessary delta x for the buffer. This has to be added or subtracted 
        # to/from the x-coordinates.
        delta_x = cutting_buffer_outside_of_board * self.tan_cut_angle
        
        if self.is_odd_number_of_tails:
            # Using an odd number of dovetails results in two "half-tails" 
            # (see the dialog of the plugin for an explanatory graphic).
            # First we add routing paths for both "half-tails" on the left and 
            # right hand side of the pin board. After that we will iterate the 
            # full dovetails and add a cutting path for each of them. All 
            # trapezoids will have their smaller edges on top to minimize 
            # cutting into spoil boards.
            # A side effect of this decision
            top_left = (-__HORIZONTAL_BUFFER__, start_y)
            # For the half-tails the width has (obviously) to be divided by two.
            top_right = (self.smaller_width_tails/2-delta_x, start_y)
            bottom_right = (self.options.width_tails/2+delta_x, end_y)
            bottom_left = (-__HORIZONTAL_BUFFER__, end_y)
            self.add_polygon(top_left, top_right, bottom_right, bottom_left)

            # right hand half-tail
            top_left = (self.options.width-self.smaller_width_tails/2+delta_x, 
                start_y)
            top_right = (self.options.width + __HORIZONTAL_BUFFER__, start_y)
            bottom_right = (self.options.width + __HORIZONTAL_BUFFER__, 
                end_y)
            bottom_left = (self.options.width-self.options.width_tails/2-delta_x, 
                end_y)
            self.add_polygon(top_left, top_right, bottom_right, bottom_left)
            
            # With an odd number of tails the x-coordinate for the center 
            # of the next trapezoid is the width of a half-tail plus the width 
            # of the cuts made with the dovetail bit plus the half of the 
            # dovetail width. From there we calculate the relevant
            # x-coordinates using the smaller and wider widths of the tails.
            x = self.options.width_tails + self.individual_width_of_tail_cut
        else:
            # With an even number of tails there are no half-tails. The first 
            # dovetail starts after half of an "individual_width_of_tail_cut"
            # and the center of the tail is its width divided by two - so:
            x = (self.options.width_tails + self.individual_width_of_tail_cut)/2            
        
        for i in range(self.options.num_tails):
            top_left = (x - self.smaller_width_tails/2 + delta_x, start_y)
            top_right = (x + self.smaller_width_tails/2 - delta_x,  start_y)
            bottom_right = (x + self.options.width_tails/2 + delta_x, end_y)
            bottom_left = (x - self.options.width_tails/2 - delta_x, end_y)
            self.add_polygon(top_left, top_right, bottom_right, bottom_left)
            # the (horizontal) center of the next trapezoid is the with of a 
            # cut between the dovetails plus the width of the dovetail.
            x = x + self.individual_width_of_tail_cut + self.options.width_tails

        return end_y
    
    
    def __calc_and_check_parameters(self):
        """Checks the parameters specified by the user and returns an error
        message, if they do not work out."""
        self.tan_cut_angle = tan(radians(self.options.cut_angle))
        self.is_odd_number_of_tails = self.options.num_tails % 2 == 1
        self.upper_tail_diameter = self.calculate_upper_tail_diameter()
        if self.upper_tail_diameter <= 0:
            return ("The calculated upper cutting diameter for dovetail bit "
                    "is zero or less!\n\nThis means, that the parameters "
                    "specified for\n  1) cutting angle "
                    f"({self.options.cut_angle}°),\n"
                    f"  2) dovetail bit diameter ({self.options.tail_bit_diameter}"
                    "mm) and\n  3) the thickness of the pins board ("
                    f"{self.options.pin_thickness}mm, determines the plunge "
                    "depth) lead to a geometry that is impossible to cut.\n\n"
                    "Please re-check these parameters.")
        
        # The width of the dovetails specified by the user is the widest width
        # of the tails. It is cut by the upper part of the dovetail bit - with 
        # the diameter calculated above.
        # The width of the dovetails at their bottom is smaller, as it is cut 
        # by the widest diameter of the dovetail bit. The difference between 
        # these two widths is equal to the difference between the widest 
        # cutting diameter of the dovetail bit and the diameter calculated 
        # before.
        self.smaller_width_tails = self.options.width_tails - \
            (self.options.tail_bit_diameter - self.upper_tail_diameter)

        # You cut the spaces for the dovetails using the straight bit. So the 
        # diameter of the straight bit cannot be wider than the smaller width 
        # of the dovetails.
        if self.smaller_width_tails  < self.options.pin_bit_diameter:
            return ("The specified width of the tails (red line) is "
                    f"{self.options.width_tails}mm, which results in a "
                    f"(lower/smaller) width of {self.smaller_width_tails:.2f}"
                    "mm.\n\nThis is smaller than the diameter of your straight"
                    f" router bit ({self.options.pin_bit_diameter}mm).\n\n"
                    "As this bit cannot cut a gap this small, this cannot "
                    "work.\n\nYou'll either have to use a thinner straight "
                    "bit or increase the width of the dovetails.")
    
        # Check, whether the added widths of the dovetails are wider than the
        # tail board.
        cumulative_tail_width = self.num_tail_cuts() * self.options.width_tails
        if cumulative_tail_width >= self.options.width:
            msg = ("The cumulative width of the tails ("
                f"{cumulative_tail_width}mm) is too wide for the "
                f"specified board width ({self.options.width}mm).\nPlease "
                "reduce the number of tails or the tail width accordingly.")
            if self.is_odd_number_of_tails:
                msg = msg + ("\nPlease take into consideration that with "
                    "an odd number of tails additional padding is added "
                    "(see yellow lines in illustration).")
            return msg
        
        # Calculate the cumulative width of the distances between the dovetails
        # in order to calculate the cut width in between the dovetails.
        cumulative_width_of_cuts_between_tails = \
                self.options.width - cumulative_tail_width
        assert cumulative_width_of_cuts_between_tails > 0
        self.individual_width_of_tail_cut = \
                cumulative_width_of_cuts_between_tails / self.num_tail_cuts()

        # the next check is, whether the width of each of the cuts with the 
        # dovetail bit is at least as wide as the upper diameter calculated above
        self.individual_width_of_tail_cut = \
            cumulative_width_of_cuts_between_tails / self.num_tail_cuts()
        if self.individual_width_of_tail_cut < self.upper_tail_diameter:
            return ("The calculated width of the cuts made between the "
                    f"dovetails is {self.individual_width_of_tail_cut:.2f}"
                    "mm.\n\nYou will not be able to make these cuts, as the "
                    "diameter of your dovetail bit is "
                    f"{self.upper_tail_diameter:.2f}mm when plunged "
                    f"down to {self.options.pin_thickness}mm depth (i.e. the "
                    "thickness of the pins board).\n\n"
                    "Please reduce the number of tails or the tail width "
                    "accordingly.")
        return None
        
    
    def add_pin_board(self):
        """Adds a guide for the pin board, pockets for routing the pins,
        a custom anchor and instructions to the current layer.
        It returns the lower end of the graphics (not the text) in mm."""
        self.add_box(0, 0, self.options.width, self.options.pin_thickness, 
                     RoutingType.GUIDE)        
        lower_end = self.add_pin_cuts()
        pin_anchor_element = create_anchor_polygon(
                AxisOrientation.RT, x=0, 
                y=self.du2uu(self.options.pin_thickness), 
                x_size=self.du2uu(self.options.pin_thickness/2)
                )
        current_layer = self.svg.get_current_layer()
        current_layer.add(pin_anchor_element)
        self.add_text(0, lower_end + __LINE_HEIGHT__, 
            "Cutting pattern for straight router bit in the pin board.") 
        self.add_text(0, lower_end + 2 * __LINE_HEIGHT__, 
            f"Set cutting depth to {self.options.tail_thickness}mm.")
        return lower_end


    def add_tail_board(self, y_origin_tail_board):
        self.add_box(0, y_origin_tail_board, self.options.width, 
                     y_origin_tail_board + self.options.tail_thickness, 
                     RoutingType.GUIDE)        
        lower_end = self.add_tail_cuts(y_origin_tail_board)
        dovetail_anchor_element = create_anchor_polygon(
                AxisOrientation.RT, x=0, 
                y=self.du2uu(y_origin_tail_board+self.options.tail_thickness), 
                x_size=self.du2uu(self.options.tail_thickness/2)
                )
        current_layer = self.svg.get_current_layer()
        current_layer.add(dovetail_anchor_element)
        self.add_text(0, lower_end + __LINE_HEIGHT__, 
                      ("Cutting pattern for dovetail router bit in the tail "
                      "board."))
        self.add_text(0, lower_end + 2 * __LINE_HEIGHT__, 
                      f"Set cutting depth to {self.options.pin_thickness}mm.")
        self.add_text(0, lower_end + 3 * __LINE_HEIGHT__, 
                      ("You can use any straight cutter in the given paths to "
                       "go easy on your dovetail bit."))
        self.add_text(0, lower_end + 4.5 * __LINE_HEIGHT__, 
                      ("**IMPORTANT**: Set cutting diameter to "
                       f"{self.upper_tail_diameter:.2f}mm when using the "
                       "dovetail bit!"),
                      bold=True)
        self.add_text(0, lower_end + 5.5 * __LINE_HEIGHT__, 
                      ("Please remember to not use incremental depths with "
                       "the dovetail bit and plunge/retract as far away from "
                       "the board as possible."))
        self.add_text(0, lower_end + 6.5 * __LINE_HEIGHT__, 
                      ("The cutting buffers leave more than enough space for "
                       "safe plunging and retracting."))
        self.add_text(0, lower_end + 9 * __LINE_HEIGHT__,
                      ("You should skip the text when loading the cut paths to "
                       "your Origin."))
        self.add_text(0, lower_end + 10 * __LINE_HEIGHT__,
                      ("The amount of paths seems to be a "
                       "challenge (at least to my Gen 1)."))


    def shaper_effect(self):
        errormsg = self.__calc_and_check_parameters()
        if errormsg is not None:
            inkex.utils.errormsg(errormsg)
            return
        
        lower_end = self.add_pin_board()
        self.add_tail_board(lower_end + __VERTICAL_OFFSET_BOARDS__)


if __name__ == '__main__':
    ShaperOriginDovetailsExtension().run()
