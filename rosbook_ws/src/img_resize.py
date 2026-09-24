from PIL import Image

# 이미지 열기
img = Image.open("jdcobot100.png")

# 1) JPG 포맷으로 품질 75% 압축 저장 (용량 60~70% 감소)
rgb_img = img.convert("RGB")
rgb_img.save("jdcobot100_compressed.jpg", "JPEG", quality=75, optimize=True)

# 또는 2) PNG 포맷 그대로 최적화 저장
# img.save("compressed_image.png", "PNG", optimize=True)