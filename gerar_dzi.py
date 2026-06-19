"""
Pipeline das lâminas palinológicas.

Os arquivos em images/perfl*.jpg chegam super-comprimidos (~Q=20,
ratio ~260:1). Os artefatos de luminancia (halos / ringing) ficam
gravados nos pixels e nao podem ser revertidos por re-encoding.

Este pipeline aplica um unsharp mask LEVE (radius=5, sigma=3, x1=2)
para restaurar a nitidez das bordas perdida na quantizacao DCT.
Nenhum pixel eh alterado em regioes planas -- apenas a transicao
dark/light das particulas recupera a nitidez original.

Nenhum resize, nenhuma mask, nenhum crop. Cada pixel que nao esta
em uma borda mantem seu valor; bordas recuperam a agudeza.

Para cada imagem (A-F):
  1. Carrega o JPEG
  2. Aplica sharpen (unsharp mask)
  3. Gera DZI a partir do resultado
  4. Gera thumbnail 320px

Tudo encadeado via pyvips, sem arquivos intermediarios em disco.
"""
import os, time, shutil, pyvips

src_dir    = r'C:\Users\adm_rmejia\Projetos\banner_palino\images'
dzi_dir    = os.path.join(src_dir, 'dzi')
thumbs_dir = os.path.join(src_dir, 'thumbs')
os.makedirs(dzi_dir, exist_ok=True)
os.makedirs(thumbs_dir, exist_ok=True)

SHARP_RADIUS = 5
SHARP_SIGMA  = 3
SHARP_X1     = 2
DZI_QUALITY  = 80
THUMB_SIZE   = 320
THUMB_QUALITY = 82

letters = ['A', 'B', 'C', 'D', 'E', 'F']
total_t0 = time.time()

for L in letters:
    src = os.path.join(src_dir, f'perfl 1j_C_offline_{L}.jpg')
    print(f'\n=== {L} ===')

    img = pyvips.Image.new_from_file(src)
    print(f'  source:    {img.width}x{img.height}')

    sharp = img.sharpen(radius=SHARP_RADIUS, sigma=SHARP_SIGMA, x1=SHARP_X1)

    dzi_file     = os.path.join(dzi_dir, f'{L}.dzi')
    dzi_filesdir = os.path.join(dzi_dir, f'{L}_files')
    for p in (dzi_file, dzi_filesdir):
        if os.path.isfile(p):    os.remove(p)
        elif os.path.isdir(p):   shutil.rmtree(p)

    t0 = time.time()
    sharp.dzsave(
        dzi_file[:-4],
        tile_size=256, overlap=1, suffix=f'.jpg[Q={DZI_QUALITY}]'
    )
    print(f'  DZI (Q={DZI_QUALITY} tiles): {time.time()-t0:.1f}s')

    t0 = time.time()
    sharp.thumbnail_image(THUMB_SIZE, height=THUMB_SIZE).jpegsave(
        os.path.join(thumbs_dir, f'{L}.jpg'), Q=THUMB_QUALITY
    )
    print(f'  thumb (Q={THUMB_QUALITY}):    {time.time()-t0:.1f}s')

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
