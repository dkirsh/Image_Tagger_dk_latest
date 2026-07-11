# Low-Level Feature Analysis


### Getting started
This script was tested under Python 3.11. 


### Running the Script

Run the script:

E.g., `python main.py --path 'img/' --ext 'jpg'`

- `--path` specifies the folder that contains your images. The folder should be within the same directory as this script.
- `--ext` specifies the image extension. This is either 'jpg' or 'png'.
- `--brightness` by default `True`, will calculate a brightness value for each image.
- `--color` by default `True`, will calculate color percentages. This includes the percentage of green, blue, red and neutral (white, black, and grey) pixels in the image.
- `--contrast` by default `True`, will calculate the average contrast of each image.
- `--entropy` by default `True`, will calculate the average entropy of each image.
- `--edge_density` by default `True`, will calculate the average straight and non-straight edge density of each image.
- `--mse` by default `True`, will calculate a symmetry score based on the mean square error between the original and flipped image.
- `--ssi` by default `True`, will calculate a symmetry score based on the structural similarity index between the original and flipped image.
- `--hsv_values` by default `True`, will calculate the hsv properties: average hue, sd hue, average saturation, sd saturation, average value, and sd value.
- `--power-spectrum` by default `True`, will calculate the mean of the power spectrum of the image.


### Output
The script will output an excel file 'low-level-features.xlsx'


### Interpretation of Low-level feature values
- Brightness: Is a value between 0 and 1 where a higher value indicates more brightness in the image.
- Color: All color values represent percentages. Therefore, the color values of green, blue, red, and neutral pixel sum up to 1. A value of 0.4 hence indicates that the image consists of 40% of green pixel.
- Contrast: Is a value between 0 and 1 where a higher value indicates a higher overall contrast in the image.
- Symmetry: MSE symmetry has a minimum value of 0, which would indicate perfect symmetry, but not maximum value. Therefore, smaller number indicate a higher symmetry. For SSI symmetry, the values range between -1 and 1, where 1 indicates perfect symmetry.
- Entropy: There are no strict limits for this measure, but usually the entropy values range between 6-7 (although they can be lower or higher). Higher values indicate a higher entropy of the image.
- Hue: Is the average hue of the image.
- Sd hue: Is the standard deviation of the hue values and represents the degree of diversity in the images hue.
- Saturation: Higher values indicates a higher saturation of the image.
- Sd saturation: Standard deviation of the saturation. Higher values indicate a greater diversity in the saturation of the image.
- Value: Another way to measure the brightness in an image.
- Sd value: Standard deviation of value. Represents the diversity in value across the image.
- SED: A higher value indicates a higher straight edge density.
- NSED: a higher value indicates a higher non-straight edge density
- Power spectrum: Provides insides into the frequency characteristics of the image (this includes also textures). Higher values indicate a higher mean power spectrum (images with a lot of textures/noise), while a low mean power spectrum relates to an image that is rather smooth in terms of its textures.
