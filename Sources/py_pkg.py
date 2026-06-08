import sys
import pkgutil
import subprocess

def install_pkg(pkg_name):
    loader = pkgutil.find_loader(pkg_name)
    if loader is None:
        subprocess.run(f'python -m pip install {pkg_name}')

if __name__ == '__main__':
    pkg_name = sys.argv[1]
    install_pkg(pkg_name)