#!/usr/bin/env python3
#
# Copyright (c) 2025, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
#
# All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
#import bpy
import mujoco
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import PyKDL
import sys

from ament_index_python.packages import get_package_prefix
from xml.dom import minidom, Node


def main(filepath):
    # Load your XML document
    dom = minidom.parse(filepath)

    # Get all elements with the tag name you're interested in
    body_elements = dom.getElementsByTagName("body")

    include_element = dom.createElement("include")
    include_element.setAttribute("file", "wheels.xml")

    # Filter by attribute value containing a substring
    for elem in body_elements:
        if "wheel_link" in elem.getAttribute("name"):
            for node in elem.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    if (
                        node.tagName == "geom"
                        and node.getAttribute("type") == "cylinder"
                        and node.getAttribute("class") == "collision"
                    ):
                        print(f"adding to {elem.getAttribute('name')}")
                        node.setAttribute("name", elem.getAttribute("name"))

    with open(filepath, "w") as file:
        # Remove extra newlines that minidom adds after each tag
        xml_data = "\n".join(
            [line for line in dom.toprettyxml(indent="  ").splitlines() if line.strip()]
        )
        file.write(xml_data)


if __name__ == "__main__":
    filepath = "mjcf_data/mujoco_description_formatted.xml"
    main(filepath)
