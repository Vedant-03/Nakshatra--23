# from flask import Flask, request, render_template, jsonify
# from astropy.io import fits
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import numpy as np
# import json

# app = Flask(__name__, template_folder='templates')

# data = None

# @app.route('/upload-fits-file', methods=['POST'])
# def upload_fits_file():
#     file = request.files['fits-file']
#     hdul = fits.open(file, mode='update')
#     data = hdul[0].data
#     plt.imshow(data)
#     plt.savefig('static/image.png')
#     hdul.close()
#     return render_template('index.html')

# @app.route('/')
# def index():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, url_for, send_from_directory
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib import rcParams
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import os
import sep
import math

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render():
    print(os.getcwd())
    if request.method == 'POST':
        rcParams['figure.figsize'] = [8., 8.]
        file1 = request.files['file1']
        file2 = request.files['file2']
        hdu1 = fits.open(file1, mode='update')
        hdu2 = fits.open(file2, mode='update')
        data1 = hdu1[0].data
        data2 = hdu2[0].data
        red_shape = data1.shape
        blue_shape = data2.shape

        scaler = MinMaxScaler()
        scaler.fit(data1)
        data1 = scaler.transform(data1)
        scaler.fit(data2)
        data2 = scaler.transform(data2)

        height_diff = abs(red_shape[0] - blue_shape[0])
        width_diff = abs(red_shape[1] - blue_shape[1])

        if red_shape[0] > blue_shape[0]:
            data1 = data1[height_diff//2:-height_diff//2,:]
        elif red_shape[0] < blue_shape[0]:
            data2 = data2[height_diff//2:-height_diff//2,:]

        if red_shape[1] > blue_shape[1]:
            data1 = data1[:,width_diff//2:-width_diff//2]
        elif red_shape[1] < blue_shape[1]:
            data2 = data2[:,width_diff//2:-width_diff//2]
        greendata = (data1 + data2) / 2

        image_data = np.dstack((data1, greendata, data2))
        plt.imshow(image_data)
        plt.axis('off')
        plt.savefig(os.path.join('static', 'image.png'))

        data1 = mirror_data(data1)
        data2 = mirror_data(data2)
        data1 = data1.astype(np.float)
        data2 = data2.astype(np.float)
        data1_sub, data1_bkg = subtract_background(data1)
        data2_sub, data2_bkg = subtract_background(data2)
        objects = extract_sources(data1_sub, data1_bkg, 0, 0, data1.shape[0], data1.shape[1])
        target_flux_red, target_flux_blue = get_target_flux(objects, data1_sub, data1_bkg, data2_sub, data2_bkg)
        temperatures = []
        for i in range(len(objects)):
            color_index = 2.5*math.log(abs(target_flux_red[i]/target_flux_blue[i]))
            color_index = abs(color_index)
            temp = 4600*(1/(0.92*color_index + 1.7) + 1/(0.92*color_index) + 0.62)
            temperatures.append(temp)

        plt.clf()
    return render_template('index.html', image_url=url_for('static', filename='image.png'))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

###         TEMPERATURE CALCULATION         ###
def mirror_data(data):
    dataout = np.array(data)
    rows = len(data)
    cols = len(data[0])
    for r in range(rows):
        for c in range(cols):
            dataout[rows-1-r][c] = data[r][c]
    return dataout

def get_image_data(filename, mirror=False):
    # process filename as FITS file
    

    data = fits.getdata(filename)
    
    if mirror==True:
        data = mirror_data(data)

    data = data.byteswap().newbyteorder()
    
    return data

def subtract_background(data):
      # measure a spatially varying background on the image
    data = data.astype(np.float)
    bkg = sep.Background(data)
    
    # evaluate background as 2-d array, same size as original image
    bkg_image = bkg.back()
    # bkg_image = np.array(bkg) # equivalent to above
    
    # evaluate the background noise as 2-d array, same size as original image
    bkg_rms = bkg.rms()
    data_sub = data - bkg
    
    return data_sub, bkg

def extract_sources(data_sub, bkg, x1, y1, x2, y2):
    # perform the extraction
    objects = sep.extract(data_sub, 20, err=bkg.globalrms,minarea = 100)
    
    # display the image
    from matplotlib.patches import Ellipse

    # plot background-subtracted image
    fig, ax = plt.subplots()
    m, s = np.mean(data_sub), np.std(data_sub)
    im = ax.imshow(data_sub, interpolation='nearest', cmap='gray',
               vmin=m-s, vmax=m+s, origin='lower')
    plt.xlim(x1,x2)
    plt.ylim(y1,y2)

    # plot an ellipse for each object
    for i in range(len(objects)):
        e = Ellipse(xy=(objects['x'][i], objects['y'][i]),
                width=6*objects['a'][i],
                height=6*objects['b'][i],
                angle=objects['theta'][i] * 180. / np.pi)
        e.set_facecolor('none')
        e.set_edgecolor('red')
        ax.add_artist(e)
    plt.show()
    
    return objects

def get_target_flux(objects, red_data_sub, red_bkg, blue_data_sub, blue_bkg):
    target_flux_red = []
    target_flux_blue = []
    lst = [-3,-2,-1,0,1,2,3]

    for i in range(len(objects)):
      curr_x = objects[i]['x']
      curr_y = objects[i]['y']
      red_flux = float(0)
      blue_flux = float(0)
      for x in lst:
        for y in lst:
            red_flux += red_data_sub[int(curr_y + y)][int(curr_x + x)]
            blue_flux += blue_data_sub[int(curr_y + y)][int(curr_x + x)]
      target_flux_red.append(red_flux)
      target_flux_blue.append(blue_flux)

    return target_flux_red, target_flux_blue



if __name__ == '__main__':
    file_path = 'static/image.png'
    if(os.path.isfile(file_path)):
        os.remove(file_path)
    app.run(debug=True)