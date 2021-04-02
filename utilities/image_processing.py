from PIL import Image

basewidth = 60
img = Image.open(r'C:\Users\Sam\Documents\Python Scripts\Chess\images\chess-piece.png')
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), Image.ANTIALIAS)
img.save('somepic.jpg')