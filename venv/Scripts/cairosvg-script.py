#!C:\repos\taiga_back\taiga-back\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'CairoSVG==2.0.3','console_scripts','cairosvg'
__requires__ = 'CairoSVG==2.0.3'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('CairoSVG==2.0.3', 'console_scripts', 'cairosvg')()
    )
