#!/usr/bin/env python3
# Debug helper: print the parent chain of given node names in the Kconfig tree
import sys
sys.path.insert(0, "/mnt/d/Workspaces/TweakWorkspace/Tweak-PC/wsl2-kernel-ci/config_filter")
from kconfiglib import Kconfig
from collections import OrderedDict
import parse_kconfig

kconf = Kconfig(sys.argv[1], warn_to_stderr=False)
h = OrderedDict({})
parse_kconfig.prepareNode(h, kconf.top_node)

def find(nodes, name, parents):
    for c in nodes:
        n = parse_kconfig.getNodeName(c)
        if n == name:
            return parents + [n]
        r = find(nodes[c], name, parents + [n])
        if r:
            return r
    return None

targets = sys.argv[2].split("::") if len(sys.argv) > 2 else []
for t in targets:
    if t:
        print(t, "->", " > ".join(find(h, t, []) or ["NOT FOUND"]))
