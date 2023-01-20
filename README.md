# Nakshatra-23

# Team name : pied_piper

## Team members : 

vedant agrawal(cse210001074@iiti.ac.in)               

devansh gupta(me210003028@iiti.ac.in)               

Renu(me210003063@iiti.ac.in)
               
               
## Brief write up about our solution:
 
### The code that we have uploaded is a Flask web application that takes two FITS files as input, processes them, and renders the result in a browser. The processing steps include:

Open the FITS files using the **astropy.io** library, get the data and shape of the images.

Scale the data of both images to the same scale using **MinMaxScaler** from the sklearn library.

Crop both images to the same size if their shapes are different.

Create a green channel by averaging the red and blue channels.

Create a RGB image from the red, green and blue channels.

Display the RGB image using matplotlib's imshow function.

Mirror the data of both images.

Subtract the background of both images using **'sep'** library

Extract sources from the background subtracted images.

Find the target flux of the sources in both images.

Calculate the temperature of the sources using the flux values.

formulae that we used was _ballesteros formula_. 

Create a scatter plot of the sources using matplotlib.

Plot the temperature of the sources on the scatter plot using the matplotlib's annotate function.

Show the scatter plot using matplotlib's show function.

Return the image to the browser using the flask's render_template function


### Problems Faced :

There multiple hurdles to overcome, in the implementation side it was difficult to come up with a method to identify stars in the image and then calculate tempereature of the star. we finally used the ballesteros formula to get the temperature of the star from the color index of the star.
On the web tool part of the solution it was a bit complicated to render temperatures when hovered upon a star so we finally instead rendered multiple plots with identified stars and their temperatures.

## Requirements/ Instructions to run this locally : 

To run this on local machine:
1. Download the zip file of the code
2. Install the necessary dependencies:
    `pip install flask`
    `pip install sep`
    `pip install astropy.io`
    `pip install sklearn`
3. Finally run the project by the running the command `python app.py`

