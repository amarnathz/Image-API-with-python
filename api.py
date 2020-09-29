from flask import Flask, render_template, request, json
import urllib.request

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, ImageChops


def make_histogram(cluster):
    """
    Count the number of pixels in each cluster
    :param: KMeans cluster
    :return: numpy histogram
    """
    numLabels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    hist, _ = np.histogram(cluster.labels_, bins=numLabels)
    hist = hist.astype('float32')
    hist /= hist.sum()
    return hist


def make_bar(height, width, color):
    """
    Create an image of a given color
    :param: height of the image
    :param: width of the image
    :param: BGR pixel values of the color
    :return: tuple of bar, rgb values, and hsv values
    """
    bar = np.zeros((height, width, 3), np.uint8)
    bar[:] = color
    red, green, blue = int(color[2]), int(color[1]), int(color[0])
    hsv_bar = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv_bar[0][0]
    return bar, (red, green, blue), (hue, sat, val)


def primary():
    img = cv2.imread("draw.png")
    height, width, _ = np.shape(img)
    # reshape the image to be a simple list of RGB pixels
    image = img.reshape((height * width, 3))
    # we'll pick the 5 most common colors
    num_clusters = 5
    clusters = KMeans(n_clusters=num_clusters)
    clusters.fit(image)
    # count the dominant colors and put them in "buckets"
    histogram = make_histogram(clusters)
    # then sort them, most-common first
    combined = zip(histogram, clusters.cluster_centers_)
    combined = sorted(combined, key=lambda x: x[0], reverse=True)
    # finally, we'll output a graphic showing the colors in order
    bars = []
    hsv_values = []
    rgbs = []
    for index, rows in enumerate(combined):
        bar, rgb, hsv = make_bar(100, 100, rows[1])
        print(f'Bar {index + 1}')
        print(f'  RGB values: {rgb}')
        print(f'  HSV values: {hsv}')
        hsv_values.append(hsv)
        bars.append(bar)
        str = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
        rgbs.append(str)
        return str
        #rgbs.append([rgb[0], rgb[1], rgb[2]])
     

def border(): 
    bor=[]
    img = Image.open("draw.png")
    w, h = img.size
    image_rgb = img.convert("RGB")
    t_l = image_rgb.getpixel((0,0))
    t_l = '#{:02x}{:02x}{:02x}'.format(t_l[0], t_l[1], t_l[2])
    t_r = image_rgb.getpixel((w-1,0))
    t_r = '#{:02x}{:02x}{:02x}'.format(t_r[0], t_r[1], t_r[2])
    b_l = image_rgb.getpixel((0,h-1))
    b_l = '#{:02x}{:02x}{:02x}'.format(b_l[0], b_l[1], b_l[2])   
    b_r = image_rgb.getpixel((w-1,h-1))
    b_r = '#{:02x}{:02x}{:02x}'.format(b_r[0], b_r[1], b_r[2])
    
    return t_l


app = Flask(__name__)


@app.route('/pic',methods=['GET'])
def pic():
    src = request.args.get('src')
    print(type(src))
    print(src)
    src="https://"+urllib.parse.quote(src[8:])
    print(src)
    urllib.request.urlretrieve(src, "draw.png")
    data=[]
    pri_color = primary()
    data.append(pri_color)
    border_color = border()
    data.append(border_color)
  
    print(data)
    data_json={"logo_border": data[1],'dominant_color':data[0]}
    data_json=json.dumps(data_json)
    return data_json

   
        #futher code

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
