#!/usr/bin/python3

configBase = 'microsoft_config'
configOverride = 'ubuntu_config'
configDiff = 'ubuntu_config_picked.diff'
configOutput = 'microsoft_config_patched'

def mergeConf(configBase, configOverride, configDiff, configOutput):
    lines = open(configDiff, 'r').read().splitlines()
    config_picked = [line.strip().split(' ')[0] for line in lines]
    print(config_picked)

    ori_config = open(configBase, 'r').read()
    ubuntu_config = open(configOverride, 'r').read()

    ubuntu_lines = filter(lambda x: x.startswith('CONFIG_'), ubuntu_config.splitlines())
    ubuntu_linemap = { c.split('=')[0]: c for c in ubuntu_lines}
    #print(ubuntu_linemap)

    new_config = ori_config
    import re
    for conf in config_picked:
        newconf = ubuntu_linemap["CONFIG_" + conf]
        if newconf.endswith('=m'):
            newconf = newconf[:-2] + '=y'
        # like this # CONFIG_KERNEL_LZMA is not set
        new_config = re.sub(r'^CONFIG_%s=.*?$' % conf, newconf, new_config, flags=re.M)
        new_config = re.sub(r'^# CONFIG_%s is not set$' % conf, newconf, new_config, flags=re.M)

    with open(configOutput, 'w') as f:
        f.write(new_config)

def main(args):
    if len(args) < 4:
        print("Usage: python3 merge_config.py configBase configOverride configDiff configOutput")
    mergeConf(*args[0:4])

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])