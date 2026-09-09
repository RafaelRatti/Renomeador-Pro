from PIL import Image

# Pega o seu ícone baixado
img = Image.open("icon.ico")

# Força as proporções exatas e salva em todas as resoluções que o Windows exige
img.save(
    "icon_valido.ico", 
    format="ICO", 
    sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
)
print("Ícone consertado com sucesso! Um arquivo 'icon_valido.ico' foi gerado.")