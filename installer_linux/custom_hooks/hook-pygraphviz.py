import glob
import os
import shutil

from PyInstaller.depend.bindepend import findLibrary

binaries = []
datas = []

# List of binaries agraph.py may invoke.
progs = [
    "neato",
    "dot",
    "twopi",
    "circo",
    "fdp",
    "nop",
    "acyclic",
    "gvpr",
    "gvcolor",
    "ccomps",
    "sccmap",
    "tred",
    "sfdp",
    "unflatten",
]

# Locate the graphviz binaries directory
graphviz_bindir = os.path.dirname(shutil.which("dot"))
if graphviz_bindir:
    for binary in progs:
        binary_path = os.path.join(graphviz_bindir, binary)
        if os.path.exists(binary_path):
            binaries.append((binary_path, "."))

# Locate the graphviz libraries directory
gvc_lib = findLibrary('gvc')
if gvc_lib:
    graphviz_libdir = os.path.dirname(gvc_lib)
    if graphviz_libdir:
        for binary in glob.glob(os.path.join(graphviz_libdir, "*.so")):
            binaries.append((binary, "graphviz"))
        for data in glob.glob(os.path.join(graphviz_libdir, "config*")):
            datas.append((data, "graphviz"))
else:
    graphviz_libdir = None

# Fallback for typical Ubuntu locations if above methods fail
if not graphviz_bindir:
    common_bindirs = ["/usr/bin", "/usr/local/bin", "/usr/lib/graphviz"]
    for common_bindir in common_bindirs:
        if os.path.isdir(common_bindir):
            for binary in progs:
                binary_path = os.path.join(common_bindir, binary)
                if os.path.exists(binary_path):
                    binaries.append((binary_path, "."))

if not graphviz_libdir:
    common_libdirs = ["/usr/lib", "/usr/lib64", "/usr/local/lib"]
    for common_libdir in common_libdirs:
        libdir_path = os.path.join(common_libdir, "graphviz")
        if os.path.isdir(libdir_path):
            for binary in glob.glob(os.path.join(libdir_path, "*.so")):
                binaries.append((binary, "graphviz"))
            for data in glob.glob(os.path.join(libdir_path, "config*")):
                datas.append((data, "graphviz"))
