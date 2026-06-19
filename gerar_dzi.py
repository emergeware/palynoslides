"""
Pipeline de processamento das lâminas palinológicas.

Para cada imagem (A-F) em images/perfl*.jpg:
  1. Carrega original (resolução típica: 22434x18907)
  2. Reduz para no máximo MAX_DIM px no lado maior
  3. Achata o fundo: substitui pixels de fundo pela versão borrada
     (uniforme) e preserva os espécimes (manchas significativas)
  4. Gera tiles DZI em images/dzi/<L>/  (OpenSeadragon)
  5. Gera thumbnail 320px em images/thumbs/<L>.jpg (catálogo)

Resultado típico: ~1-2 MB por imagem processada, fundo uniforme
que comprime muito bem em JPEG, espécimes preservados.
"""
import os, time, pyvips

src_dir = r'C:\Users\adm_rmejia\Projetos\banner_palino\images'
dzi_dir  = os.path.join(src_dir, 'dzi')
thumbs_dir = os.path.join(src_dir, 'thumbs')
os.makedirs(dzi_dir, exist_ok=True)
os.makedirs(thumbs_dir, exist_ok=True)

MAX_DIM       = 8000
BG_BLUR_SIGMA = 150
MASK_PERCENT  = 98
DZI_QUALITY   = 80
THUMB_SIZE    = 320
THUMB_QUALITY = 82

letters = ['A', 'B', 'C', 'D', 'E', 'F']
total_t0 = time.time()

for L in letters:
    src = os.path.join(src_dir, f'perfl 1j_C_offline_{L}.jpg')
    print(f'\n=== {L} ===')

    img = pyvips.Image.new_from_file(src)
    print(f'  original:  {img.width}x{img.height}')

    if max(img.width, img.height) > MAX_DIM:
        scale = MAX_DIM / max(img.width, img.height)
        img = img.resize(scale)
        print(f'  resized:   {img.width}x{img.height}  (scale={scale:.3f})')

    bg    = img.gaussblur(BG_BLUR_SIGMA)
    diff  = (img - bg).abs()
    thr   = diff.percent(MASK_PERCENT)
    mask  = (diff > thr).ifthenelse(255, 0).gaussblur(3)
    proc  = mask.ifthenelse(img, bg)

    proc_path = os.path.join(src_dir, f'_proc_{L}.jpg')
    proc.jpegsave(proc_path, Q=85)
    proc_size = os.path.getsize(proc_path) / 1024 / 1024
    print(f'  processed: {proc_size:.2f} MB')

    t0 = time.time()
    pyvips.Image.new_from_file(proc_path).dzsave(
        os.path.join(dzi_dir, L),
        tile_size=256, overlap=1, suffix=f'.jpg[Q={DZI_QUALITY}]'
    )
    print(f'  DZI:       {time.time()-t0:.1f}s')

    t0 = time.time()
    proc.thumbnail_image(THUMB_SIZE, height=THUMB_SIZE).jpegsave(
        os.path.join(thumbs_dir, f'{L}.jpg'), Q=THUMB_QUALITY
    )
    print(f'  thumb:     {time.time()-t0:.1f}s')

    os.remove(proc_path)

print(f'\n=== TOTAL: {time.time()-total_t0:.1f}s ===')
print()

total_dzi = 0
for L in letters:
    dzi_path = os.path.join(dzi_dir, f'{L}_files')
    if os.path.isdir(dzi_path):
        for root, _, files in os.walk(dzi_path):
            for f in files:
                total_dzi += os.path.getsize(os.path.join(root, f))
        dzi_mb = sum(os.path.getsize(os.path.join(r, f))
                     for r, _, fs in os.walk(dzi_path) for f in fs) / 1024 / 1024
        print(f'  DZI {L}: {dzi_mb:.1f} MB')
print(f'  TOTAL DZI: {total_dzi/1024/1024:.1f} MB')
