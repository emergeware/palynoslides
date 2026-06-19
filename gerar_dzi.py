import os, time, pyvips

src_dir = r'C:\Users\adm_rmejia\Projetos\banner_palino\images'
dzi_dir = os.path.join(src_dir, 'dzi')
thumbs_dir = os.path.join(src_dir, 'thumbs')
os.makedirs(dzi_dir, exist_ok=True)
os.makedirs(thumbs_dir, exist_ok=True)

letters = ['A', 'B', 'C', 'D', 'E', 'F']
total_t0 = time.time()

for L in letters:
    src = os.path.join(src_dir, f'perfl 1j_C_offline_{L}.jpg')
    print(f'\n=== {L} ===')

    t0 = time.time()
    img = pyvips.Image.new_from_file(src, access='sequential')
    print(f'  loaded: {img.width}x{img.height} ({time.time()-t0:.1f}s)')

    t0 = time.time()
    img.dzsave(os.path.join(dzi_dir, L), tile_size=256, overlap=1, suffix='.jpg[Q=82]')
    print(f'  DZI: {time.time()-t0:.1f}s')

    t0 = time.time()
    thumb = pyvips.Image.new_from_file(src, access='sequential')
    thumb = thumb.thumbnail_image(320, height=320)
    thumb.jpegsave(os.path.join(thumbs_dir, f'{L}.jpg'), Q=82)
    print(f'  thumb: {time.time()-t0:.1f}s')

print(f'\n=== TOTAL: {time.time()-total_t0:.1f}s ===')

# Resumo de tamanhos
import subprocess
for L in letters:
    dzi_size = subprocess.check_output(
        ['powershell', '-Command',
         f'(Get-ChildItem -Recurse -File \"{dzi_dir}\\{L}_files\" | Measure-Object Length -Sum).Sum / 1MB'],
        shell=True
    ).decode().strip()
    thumb_size = os.path.getsize(os.path.join(thumbs_dir, f'{L}.jpg')) / 1024
    print(f'  {L}: DZI={dzi_size} MB, thumb={thumb_size:.0f} KB')
