#!/usr/bin/env python
# coding: utf-8

import re
def getConfig(l):
    configStr = re.findall(r'^CONFIG_(.*?)=.*?$', l)         + re.findall(r'^# CONFIG_(.*?) is not set$', l)
#     print(configStr)
    if len(configStr) == 0:
        return None
    return configStr[0]

def main(args):
    blacklist_syms = args[0]
    config_input = args[1]
    config_output = args[2]
    blacksyms = open(blacklist_syms).read().splitlines()
    print("Got %d blacklisted symbols" % len(blacksyms))
    
    ubuntu_config_lines = open(config_input).read().splitlines()
    print("Got %d config file lines" % len(ubuntu_config_lines))


    def processUbuntuConfig(l):
        # replace =m to =y
        l = l.replace('=m', '=y')
        return l
    
    ubuntu_config_lines = [processUbuntuConfig(c) for c in ubuntu_config_lines if getConfig(c) not in blacksyms]
    print("After filtering, remain %d lines" % len(ubuntu_config_lines))

    with open(config_output, 'w') as f:
        f.write('\n'.join(ubuntu_config_lines))

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])