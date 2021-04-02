from PIL import Image
import os

basewidth = 50

path = r'C:\Users\Sam\Documents\Python Scripts\Chess\images'

for file in os.listdir(path):
    if 'original' in file:
        tokens = file.split("_")
        f_img = path+"/"+file
        img = Image.open(f_img)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        img.save(tokens[0]+'_'+tokens[1]+'_'+str(basewidth)+'px.png')
