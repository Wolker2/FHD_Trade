"""Rebuild adapted Main.dat and Rus/Lang.dat. Python 3, no dependencies."""
from pathlib import Path
from compile_srhd_dat import build_bp

source=Path(__file__).resolve().parent
root=source.parent
build_bp(source/'CFG/Main.txt',root/'CFG/Main.dat')
build_bp(source/'CFG/Lang.txt',root/'CFG/Rus/Lang.dat')
print('Built Main.dat and Rus/Lang.dat; original CacheData.dat retained.')
