# WSL2 Kernel CI

Github Actions CI config for WSL2 Kernel.

## What's This?

Microsoft's original WSL2 kernel misses many kernel modules, incluing:
- Various FS (like squashfs)
- nftables related modules (iptables-nftables won't work)
- Security features (lxc, AppArmor, etc.)

Also, if you are on Dev Insider channel, WSL kernel would often be updated, causing you having to rebuild the kernel each time.

## The Kernel Building CI

This CI does these things for you:
- **Auto-Merging**: Merges Ubuntu's Kconfig onto Microsoft's Kconfig automatically
    - achieved by blacklisting some config symbols based on menuconfig's section, and then merges only good symbols
    - You can find the parts that are masked in `config_filter/blacklist_sections`, with some notes on what options differs between each other
    - See `config_examples` directory for a complete list of menuconfig section, and example config after merging & `make prepare`
- **Auto-Update**: Automatically Monitor [Microsoft's WSL2-Linux-Kernel](https://github.com/microsoft/WSL2-Linux-Kernel/releases), and build them once there's a new release
- **Deb-Packaging**: You can download the deb to install latest kernel header
- **Preserve-Version**: Built kernel will having the same version as original one, so scripts detecting kernel version would still work

## Download

Please goto Repo's Release ;)

## Hacking & Tweaking

The CI works by following steps:

1. (Before compiling in Github Actions) Configuring this repo by users:
    - Generate config sections tree by parsing Kconfig: `make scriptconfig PYTHONCMD=python3 SCRIPT=~/wsl2-kernel-ci/config_filter/parse_kconfig.py SCRIPT_ARG="gen_configtree" > all_sections`
    - Select config sections that needs to be masked out based on the output in last step
2. Merge kernel configs:
    - Get blacklisted symbols based on `blacklist_sections` files: `cat blacklist_sections | make scriptconfig PYTHONCMD=python3 SCRIPT=~/wsl2-kernel-ci/config_filter/parse_kconfig.py SCRIPT_ARG="get_blacklist_sym" > blacklist_syms`
    - Mask overriding config (usually Ubuntu' one) using `filter_config.py`, symbols that are blacklisted will be deleted
    - Merge config using `merge_config.py`, symbols will be replaced, and `=m` will be replaced to `=y` so that linux-modules packages are not needed
3. Reconfigure the Kernel: executing `yes "" | make prepare` to fix the dependency issue of merged config
4. Compile and Package the Kernel:
    - WSL2's kernel version has capital letters `-WSL`, causing debian packaging tools goes into error
    - Patched several Makefile to lowercase the version in package name, but still uppercase in the kernel (see build.yml)

You can tweak this repo by changing `blacklist_sections` based on `all_sections` to cut down the kernel size from `~30MB` to `~10MB`