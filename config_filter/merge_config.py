#!/usr/bin/python3
import re

configBase = 'microsoft_config'
configOverride = 'ubuntu_config_picked'
configOutput = 'microsoft_config_patched'

def getConfig(l):
    configStr = re.findall(r'^CONFIG_(.*?)=.*?$', l)         + re.findall(r'^# CONFIG_(.*?) is not set$', l)
    #     print(configStr)
    if len(configStr) == 0:
        return None
    return configStr[0]

from collections import OrderedDict

def mergeConf(configBase, configOverride, configOutput):
    ori_config = open(configBase, 'r').read()
    ubuntu_config = open(configOverride, 'r').read()

    ubuntu_lines = ubuntu_config.splitlines()
    # ubuntu_lines = filter(lambda x: x.startswith('CONFIG_'), ubuntu_lines)

    ubuntu_linemap = OrderedDict()
    for c in ubuntu_lines:
        ubuntu_linemap[getConfig(c)] = c
    del ubuntu_linemap[None]
    #print(ubuntu_linemap)

    ori_config_lines = ori_config.splitlines()
    new_config_lines = []
    for confLine in ori_config_lines:
        conf = getConfig(confLine)
        if not conf:
            new_config_lines.append(confLine)
            continue
        newconf = ubuntu_linemap.pop(conf, None)
        if not newconf:
            new_config_lines.append(confLine)
            continue
        if newconf.endswith('=m'):
            newconf = newconf[:-2] + '=y'
        new_config_lines.append(newconf)
        continue

    new_config_lines += ['######### Beginning of merged additional config']
    new_config_lines += list(ubuntu_linemap.values())

    with open(configOutput, 'w') as f:
        f.write('\n'.join(new_config_lines))

def main(args):
    if len(args) < 3:
        print("Usage: python3 merge_config.py configBase configOverride configOutput")
    mergeConf(*args[0:3])

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])