import urllib.request
from PIL import Image

f = open('imageurls.txt', 'r')
fsplit = [x.strip().split(':') for x in f]
urls = [url.split('/')[-1] for card, url in fsplit]

f.close()
for url in urls:
    try:
        im = Image.open(url)
        size = im.size
        size = [coord // 5 for coord in size]
        im.thumbnail(size, Image.ANTIALIAS)
        bits = url.split('.')
        im.save(bits[0] + '-tiny.' + bits[1])
    except:
        continue
    # im.save(url.split('/')[-1])
