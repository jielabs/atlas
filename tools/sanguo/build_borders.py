"""Build the Three Kingdoms pack's warlord border maps.

Usage: python3 tools/sanguo/build_borders.py      (needs shapely; writes packs/sanguo/borders/sg-*.geojson)

The spec is tools/sanguo/states.json: one seed per Eastern Han commandery seat and a snapshot per change of
hands, grown into territories by tools/build_states.py exactly as the atlas draws the Warring States or the Five
Dynasties. The pack's eras.json names these files in its periods' `snapshots`.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import build_states

build_states.build("tools/sanguo/states.json")
