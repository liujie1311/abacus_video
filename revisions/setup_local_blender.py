from pathlib import Path
import urllib.request, zipfile, time
root=Path(__file__).resolve().parent.parent/'tools'
root.mkdir(exist_ok=True)
dest=root/'blender-4.5.3-windows-x64'
if (dest/'blender.exe').exists():
    print(dest/'blender.exe',flush=True)
else:
    archive=root/'blender-4.5.3-windows-x64.zip'
    start=time.time();last=0
    with urllib.request.urlopen('https://download.blender.org/release/Blender4.5/blender-4.5.3-windows-x64.zip',timeout=60) as src,archive.open('wb') as out:
        while chunk:=src.read(4*1024*1024):
            out.write(chunk)
            if time.time()-last>10:
                print(f'DOWNLOAD {out.tell()/1e6:.0f} MB, {time.time()-start:.0f}s',flush=True);last=time.time()
    with zipfile.ZipFile(archive) as z:
        # Official archive; additionally constrain extraction to this tools directory.
        for member in z.infolist():
            target=(root/member.filename).resolve()
            if not target.is_relative_to(root.resolve()):raise ValueError(member.filename)
        z.extractall(root)
    assert (dest/'blender.exe').is_file()
    archive.unlink()
    print('READY',dest/'blender.exe',flush=True)
