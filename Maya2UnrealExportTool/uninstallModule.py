#!/usr/bin/env python
import os
import pathlib
import platform
import sys
from pathlib import Path
import argparse

from numpy import delete

maya_locations = {
    "Linux": "/maya",
    "Darwin": "/Library/Preferences/Autodesk/maya",
    "Windows": "\\Documents\\maya",
}

def uninstall_module(location):
    print(f"uninstalling from {location}")
    if Path(location + "modules/M2UExportTool.mod").is_file():
        os.remove(location + "modules/M2UExportTool.mod")

    folders = os.listdir(location)
    for folder in folders:
        if folder.startswith("20") and int(folder) < 2022:
            with open(f"{location}/{folder}/Maya.env", "w+") as env_file:
                if "M2U_EXPORT_PLUGIN_ROOT" in env_file.read():
                    lines = env_file.readlines()
                    for line in lines:
                        if 'M2U_EXPORT_PLUGIN_ROOT' in line:
                            lines.remove(line)
                    env_file.writelines(lines)


def check_maya_installed(dir_path):
    if dir_path:
        mloc = dir_path
    else:
        op_sys = platform.system()
        mloc = f"{Path.home()}{maya_locations.get(op_sys)}/"
    
    if not os.path.isdir(mloc):
        raise
    return mloc

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='Modify the parameters of the module uninstallation.')
    parse.add_argument('--dirpath', '-d', nargs='?', type=Path, help='specific directory path of Maya')
    args = parse.parse_args()

    try:
        m_loc = check_maya_installed(args.dirpath)
    except:
        print("Error can't find maya install")
        sys.exit(0)

    uninstall_module(m_loc)
