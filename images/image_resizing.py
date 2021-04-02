from PIL import Image

basewidth = 50
img = Image.open('chess-piece.png')
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), Image.ANTIALIAS)
img.save('white_pawn.png')
