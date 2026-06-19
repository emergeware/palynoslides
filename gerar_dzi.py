"""
Gera tiles DZI e thumbnails a partir das imagens em images/.

Nenhum processamento de pixel eh aplicado:
  - sem redimensionamento (as imagens ja estao na resolucao definitiva)
  - sem achatamento de fundo (preserva a lamina como ela eh)
  - sem crop, sem blur, sem ajuste de cor

Para cada imagem (A-F) em images/perfl*.jpg:
  1. Abre a imagem original
  2. Gera tiles DZI em images/dzi/<L>.dzi + <L>_files/  (OpenSeadragon)
  3. Gera thumbnail 320px em images/thumbs/<L>.jpg (apenas resize proporcional)
"""
import os, time, shutil, pyvips

src_dir    = r'C:\Users\adm_rmejia\Projetos\banner_palino\images'
dzi_dir    = os.path.join(src_dir, 'dzi')
thumbs_dir = os.path.join(src_dir, 'thumbs')
os.makedirs(dzi_dir, exist_ok=True)
os.makedirs(thumbs_dir, exist_ok=True)

DZI_QUALITY   = 80
THUMB_SIZE    = 320
THUMB_QUALITY = 82

letters = ['A', 'B', 'C', 'D', 'E', 'F']
total_t0 = time.time()

for L in letters:
    src = os.path.join(src_dir, f'perfl 1j_C_offline_{L}.jpg')
    print(f'\n=== {L} ===')

    img = pyvips.Image.new_from_file(src)
    print(f'  source:    {img.width}x{img.height}')

    dzi_file     = os.path.join(dzi_dir, f'{L}.dzi')
    dzi_filesdir = os.path.join(dzi_dir, f'{L}_files')
    for p in (dzi_file, dzi_filesdir):
        if os.path.isfile(p):    os.remove(p)
        elif os.path.isdir(p):   shutil.rmtree(p)

    t0 = time.time()
    img.dzsave(
        dzi_file[:-4],
        tile_size=256, overlap=1, suffix=f'.jpg[Q={DZI_QUALITY}]'
    )
    print(f'  DZI:       {time.time()-t0:.1f}s')

    t0 = time.time()
    img.thumbnail_image(THUMB_SIZE, height=THUMB_SIZE).jpegsave(
        os.path.join(thumbs_dir, f'{L}.jpg'), Q=THUMB_QUALITY
    )
    print(f'  thumb:     {time.time()-t0:.1f}s')

print(f'\n=== TOTAL: {time.time()-total_t0:.1f}s ===\n')

total_dzi = 0.0
for L in letters:
    p = os.path.join(dzi_dir, f'{L}_files')
    if os.path.isdir(p):
        mb = sum(
            os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(p) for f in fs
        ) / 1024 / 1024
        print(f'  DZI {L}: {mb:.1f} MB')
        total_dzi += mb
print(f'  TOTAL DZI: {total_dzi:.1f} MB')
