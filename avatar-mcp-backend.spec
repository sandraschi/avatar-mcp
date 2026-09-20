import sys, os
site_pkgs = os.path.abspath('.venv/Lib/site-packages')
if site_pkgs not in sys.path:
    sys.path.insert(0, site_pkgs)

# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['run_server.py'], 
    pathex=['src', site_pkgs],
    datas=[('src/avatarmcp', 'avatarmcp')],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        '_strptime',
    ],
    excludes=['tkinter','setuptools','pip','wheel','test','tests','unittest','_distutils_hack'],
    noarchive=True,
)

# Remove massive binary files from bundled packages
SKIP = ['torch','playwright','bitsandbytes','llvmlite','pyarrow','pymupdf','grpc','numba','Cython','google','azure','boto3','botocore','matplotlib','PIL','pandas','scipy','sklearn','onnxruntime']
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]

pyz = PYZ(a.pure)
exe = EXE(
    pyz, 
    a.scripts, 
    a.binaries, 
    a.zipfiles, 
    a.datas, 
    name='avatar-mcp-backend', 
    debug=False, 
    strip=False, 
    upx=False, 
    console=False
)

