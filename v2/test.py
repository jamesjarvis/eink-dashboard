#!/usr/bin/env python3
from storage import Storage
import graphics

storage = Storage()

graphics.draw_overlay(
  image=storage.get_latest_image(),
)
