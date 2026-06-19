import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

url = "https://emergeware.github.io/palynoslides/"

qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=20,
    border=2,
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    color_mask=SolidFillColorMask(front_color=(4, 8, 16), back_color=(255, 255, 255)),
    embeded_image_path=None,
)
img.save("qr/qr-palynoslides.png")

# Versão SVG (vetorial, melhor para impressão)
from qrcode.image.svg import SvgImage
qr_svg = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=20,
    border=2,
)
qr_svg.add_data(url)
qr_svg.make(fit=True)
qr_svg.make_image(image_factory=SvgImage).save("qr/qr-palynoslides.svg")

print(f"URL: {url}")
print(f"PNG saved: qr/qr-palynoslides.png")
print(f"SVG saved: qr/qr-palynoslides.svg")

import os
print(f"PNG size: {os.path.getsize('qr/qr-palynoslides.png')/1024:.1f} KB")
print(f"SVG size: {os.path.getsize('qr/qr-palynoslides.svg')/1024:.1f} KB")
