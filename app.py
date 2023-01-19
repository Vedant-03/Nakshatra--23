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


from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from sklearn.preprocessing import MinMaxScaler
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

class FitsForm(FlaskForm):
    file1 = FileField('file1', validators=[FileAllowed(['fits'])])
    file2 = FileField('file2', validators=[FileAllowed(['fits'])])

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/render-image', method=['GET', 'POST'])
def render_image(form):
    form = FitsForm()

    data1 = fits.getdata(form.file1.data)
    data2 = fits.getdata(form.file2.data)

    scaler = MinMaxScaler()
    shape1 = data1.shape
    shape2 = data2.shape

    scaler.fit(data1)
    data1 = scaler.transform(data1)
    scaler.fit(data2)
    data2 = scaler.transform(data2)

    height_diff = abs(shape1[0] - shape2[0])
    width_diff = abs(shape1[1] - shape2[1])

    if shape1[0] > shape2[0]:
        data1 = data1[height_diff//2:-height_diff//2,:]
    elif shape1[0] < shape2[0]:
        data2 = data2[height_diff//2:-height_diff//2,:]

    if shape1[1] > shape2[1]:
        data1 = data1[:,width_diff//2:-width_diff//2]
    elif shape1[1] < shape2[1]:
        data2 = data2[:,width_diff//2:-width_diff//2]

    data3 = (data1 + data2) / 2

    image_data = np.dstack((data1, data3, data2))
    print(image_data)
    plt.savefig('static/image.png')
    plt.imshow(image_data)
    plt.savefig('static/image.png')
    plt.close()

    return render_template('index.html')

@app.route('/image')
def image():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
