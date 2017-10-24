#!/usr/bin/python

import xml.etree.ElementTree as ET
import os.path

configPath ="/Library/Application Support/Kaspersky Lab/KAV/Binaries/config.xml"

if os.path.isfile(configPath):
    tree = ET.parse(configPath)
    root = tree.getroot()

    patches = root.findtext(".//key[@name='Data']/tSTRING[@name='ProductHotfix']").split('.')
    patches = ', '.join(sorted(patches))

    print ''.join(["<result>", patches, "</result>"])
else:
    print "<result>Config File Missing</result>"
