#! /usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import division
import os
import sys
import re

# Assumes SolidPython is in site-packages or elsewhwere in sys.path
from solid import *
from solid.utils import *

SEGMENTS = 48

class Cards(object):
    CARD_SIZE = [85.5, 53.8]
    CARD_THICKNESS = 0.8
    CORNER_RADIUS = 2.5
    BORDER_WIDTH = 1

    FONT = 'BigNoodleTitling:style=Oblique'
    FONT_SIZE = 4.5
    FONT_COLS = 8
    FONT_OFFSET = [-39.5, 20.5]
    FONT_SEPARATION = [10.7, 6.5]

    BORDER_THICKNESS = 0.2
    FONT_THICKNESS = 0.2

    def __init__(self, quantity):
        self.quantity = quantity
        self.max_number = int(pow(2,self.quantity)-1)
        
        #construct the map of bits to possible values
        self.magic_map = {}
        for i in range(self.max_number+1):
            n = i
            exp = 0
            while n>0:
                magic_number = self.magic_number_from_exp(exp)
                if(n&1 > 0):
                    if magic_number in self.magic_map:
                        self.magic_map[magic_number].append(i)
                    else:
                        self.magic_map[magic_number] = [i]
                n = n>>1
                exp = exp+1

    def render(self):
        r = part()
        for i in range(self.quantity):
            r = r + back(i*(self.CARD_SIZE[1]+10))(self.render_card(i))
        return r

    def render_card(self, exponent):
        c = self.get_card_base()
        n = self.get_numbers_solid(exponent)
        return c + translate([self.FONT_OFFSET[0], self.FONT_OFFSET[1], self.CARD_THICKNESS])(n)

    def get_card_base(self):
        border_factor = list(map(lambda x: (x-self.BORDER_WIDTH)/x, self.CARD_SIZE))
        border_radius = self.CORNER_RADIUS - self.BORDER_WIDTH

        s = square(self.CARD_SIZE, center=True)
        c = circle(self.CORNER_RADIUS)
        base = minkowski()(s, c)

        base_extrusion = linear_extrude(height=self.CARD_THICKNESS)(base)

        bs = scale(border_factor)(s)
        bc = circle(border_radius)
        border_hole = minkowski()(bs,bc)

        border_extrusion = linear_extrude(height=self.BORDER_THICKNESS)(base - border_hole)

        #return up(self.CARD_THICKNESS)(border_extrusion)
        #return base_extrusion
        return base_extrusion + up(self.CARD_THICKNESS)(border_extrusion)

    def get_number_solid(self, n):
        return linear_extrude(height=self.FONT_THICKNESS)(
            text(
                str(n),
                font=self.FONT,
                size=self.FONT_SIZE
            )
        )

    def magic_number_from_exp(self, exponent):
        return int(pow(2, exponent))

    def get_numbers_solid(self, exponent):
        magic_number = self.magic_number_from_exp(exponent)
        numbers = self.magic_map[magic_number]

        cols = self.FONT_COLS
        ox = self.FONT_SEPARATION[0]
        oy = self.FONT_SEPARATION[1]

        final_object = part()
        for i, n in enumerate(numbers):
            number_solid = self.get_number_solid(n)
            final_object = final_object + back((int(i/cols))*oy)(right((i%cols)*ox)(number_solid))

        return final_object 


if __name__ == '__main__':
    amount_of_cards = 7
    cards = Cards(amount_of_cards)

    for i in range(amount_of_cards):
        scad_render_to_file(
            cards.render_card(i),
            'out{}.scad'.format(i),
            file_header='$fn = %s;' % SEGMENTS,
            include_orig_code = False
        )
