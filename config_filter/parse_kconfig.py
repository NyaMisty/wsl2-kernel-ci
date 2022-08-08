#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function


from kconfiglib import *
from collections import OrderedDict

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def prepareNode(nodedict, node):
    # convert node linklist to node dict
    subnode = node.list
    while subnode:
        nodedict[subnode] = OrderedDict({})
        prepareNode(nodedict[subnode], subnode)
        subnode = subnode.next

def getNodeName(node):
    # node name as an identifier for debugging & blacklisting
    if node.is_menuconfig:
        return "Menu: " + node.prompt[0]
    else:
        if isinstance(node.item, int):
            return repr(node)
        else:
            return node.item.name

def printNodeDict(index, nodedict):
    # for debug
    leafnodes = []
    for c in nodedict:
        s = None
        if c.is_menuconfig:
            s = "Menu: " + c.prompt[0]
            
        else:
            if isinstance(c.item, int):
                s = repr(c)
            else:
                leafnodes.append(c.item.name)
        
        if leafnodes and nodedict[c]:
            print("  " * index + "[%s]" % ' '.join(leafnodes))
            
        if s:
            print("  " * index + s)
        
        if nodedict[c]:
            printNodeDict(index + 1, nodedict[c])
            leafnodes = []
    if leafnodes:
        print("  " * index + "[%s]" % ' '.join(leafnodes))


def parseBlacklist(blacklist):
    # parse manual-selected blacklist symbol, having same structure as `nodedict`
    # blacklist_sections is using indent to indicate different level
    blacklist_lines = blacklist.splitlines()
    blacklist_lines = list(filter(lambda l: l.strip() and not l.strip().startswith('#'), blacklist_lines))
    blacklist_dict = {}
    cur_indent_level = 0
    # parents = [blacklist_dict]

    # traverse all lines using a stack
    parents = { 0 : blacklist_dict }
    last_line_group = None
    for _line in blacklist_lines:
        line = _line.strip()
        indent_part = _line[:len(_line) - len(line)]
        indent_level = len(indent_part)
        if indent_level > cur_indent_level:
            # parents.append(last_line_group)
            parents[indent_level] = last_line_group
        elif indent_level < cur_indent_level:
            # parent = parents.pop()
            pass
        # parents[-1][line] = {}
        last_line_group = parents[indent_level][line] = {}
        cur_indent_level = indent_level

    return blacklist_dict

def printDict(i, d, p):
    for k in d:
        p("  " * i + k)
        if d[k]:
            printDict(i + 1, d[k], p)

def getNodeSym(node):
    try:
        return (node.item.name)
    except:
        return None
def getAllChildSymbol(_node):
    node = _node.list
    symList = []
    while node:
        nodeName = getNodeSym(node)
        if nodeName:
            symList.append(nodeName)
        symList += getAllChildSymbol(node)
        node = node.next
    return symList

def getBlacklistSymbols(nodes, blackDict):
    # nodes & blackDict should have same structure,
    # we traverse them side-by-side to filter some config
    ret = []
    nodeNamesMap = {}
    for c in nodes:
        nodeNamesMap[getNodeName(c)] = c
    for k in blackDict:
        curnodes = []
        if k.startswith('Menu: '):
            curnodes = [nodeNamesMap[k]]
        elif k.startswith('['):
            nodenames = k[1:-1].split(' ')
            for c in nodenames:
                curnodes.append(nodeNamesMap[c])
        
        if not blackDict[k]:
            ret += list(filter(lambda x: x, map(getNodeSym, curnodes)))
            if len(curnodes) == 1:
                ret += getAllChildSymbol(curnodes[0])
        else:
            assert len(curnodes) == 1
            ret += getBlacklistSymbols(nodes[curnodes[0]], blackDict[k])
    return ret


def main(args):
    if len(args) < 2:
        eprint("Usage:")
        eprint("  python3 preprocess_config.py Kconfig gen_configtree")
        eprint("  python3 preprocess_config.py Kconfig get_blacklist_sym")
    
    kconf = Kconfig(args[0], warn_to_stderr=False)
    args = args[1:]
    
    node_hierarchy = OrderedDict({})
    prepareNode(node_hierarchy, kconf.top_node)
    
    if args[0] == 'gen_configtree':
        printNodeDict(0, node_hierarchy)
    elif args[0] == 'get_blacklist_sym':
        blacklist = sys.stdin.read()
        blacklist_dict = parseBlacklist(blacklist)
        eprint("Successfully parsed blacklist:")
        printDict(0, blacklist_dict, eprint)
        blackSymbols = getBlacklistSymbols(node_hierarchy, blacklist_dict)
        eprint("Got %d Blacklisted config symbol" % len(blackSymbols))
        print('\n'.join(blackSymbols))
    else:
        eprint("Unknown command: %s" % args[0])


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])