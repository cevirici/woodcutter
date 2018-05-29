from urllib import request
from PIL import Image

f = open('imageurls.txt', 'r')
urls = []
filenames = []
for line in f:
    t = line.strip()
    urls.append(t)
    filenames.append(t[t.rfind('/')+1:])
f.close()
