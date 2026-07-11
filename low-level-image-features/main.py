import os
from skimage import io
import cv2
import pandas as pd
import cv2 as cv
import numpy as np
from skimage import measure
from skimage.metrics import structural_similarity as ssim
import click



# return the overall brightness of an image and sd of brightness
# it's a value between 0 and 1 where a higher value indicates more brightness in the image
def get_brightness(image):
    flat_image = image.flatten()
    total_brightness = np.sum(flat_image)
    tot_pix = image.shape[0] * image.shape[1] * image.shape[2]
    average_brightness = (total_brightness / tot_pix) / 255
    std_dev_brightness = np.std(flat_image / 255)
    return average_brightness, std_dev_brightness


# returns the amount of pixels which are blue, gree, red or neutral
def classify_image_colors(image):
    img  = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    rows, cols, _ = img.shape

    color_B = 0
    color_G = 0
    color_R = 0
    color_N = 0 # neutral/gray color

    for i in range(rows):
        for j in range(cols):
            k = img[i,j]
            if k[0] > k[1] and k[0] > k[2]:
                color_B = color_B + 1
                continue
            if k[1] > k[0] and k[1] > k[2]:
                color_G = color_G + 1
                continue
            if k[2] > k[0] and k[2] > k[1]:
                color_R = color_R + 1
                continue
            color_N = color_N + 1

    pix_total = rows * cols
    return color_B/pix_total, color_G/pix_total, color_R/pix_total, color_N/pix_total


# returns the average contrast of the image
# higher values indicate a higher contrast
def get_contrast(image):
    img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = img_grey.std()
    return contrast / 100


# returns shannon entropy
def get_entropy(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return measure.shannon_entropy(image)


# returns average edge density
def get_edge_density(image, sigma=0.33):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged_high_sensitiv = cv2.Canny(image, lower*0.8, upper*0.8)
    edged_low_sensitiv = cv2.Canny(image, lower*1.6, upper*1.6)

    edges = np.zeros_like(edged_high_sensitiv)
    edges[edged_low_sensitiv == 255] = 2
    edges[edged_high_sensitiv == 255] = 1

    lines = cv2.HoughLinesP(edged_high_sensitiv, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

    straight_edge_mask = np.zeros_like(image, dtype=np.uint8)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(straight_edge_mask, (x1, y1), (x2, y2), 255, 1)

    total_edges = edges.size
    straight_edges = np.sum((straight_edge_mask > 0) & (edges > 0))
    non_straight_edges = np.sum((straight_edge_mask == 0) & (edges > 0))

    straight_edge_density = straight_edges / total_edges
    non_straight_edge_density = non_straight_edges / total_edges

    return straight_edge_density, non_straight_edge_density, edges.mean()


# Mean Square Error: The smaller the error the more similarity is between the original and the flipped image
def get_mean_square_error(imgA, imgB):
    err = np.sum((imgA.astype("float") - imgB.astype("float")) ** 2)
    err /= float(imgA.shape[0] * imgA.shape[1])
    return err


# SSIM: structural similarity index. Can vary between -1 and 1, where 1 indicates perfect similarity
def get_SSI(imgA, imgB,):
    s = ssim(imgA, imgB, win_size=3, multichannel=True)
    return s


# return hsv components:
# average hue of image, as well as sd of hue
# average saturation of image, as well as sd of saturation
# average value of image, as well as sd of value
def get_hsv_values(img):
    hue = np.mean(img[:, :, 0])
    sd_hue = np.std(img[:, :, 0])

    saturation = np.mean(img[:, :, 1])
    sd_saturation = np.std(img[:, :, 1])

    value = np.mean(img[:, :, 2])
    sd_value = np.std(img[:, :, 2])
    return hue, sd_hue, saturation, sd_saturation, value, sd_value


def get_power_spectrum(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    power_spectrum = np.abs(fshift) ** 2
    mean_power_spectrum = np.mean(power_spectrum)
    return mean_power_spectrum


def write_data(n, b, sd_b, g_p, b_p, r_p, n_p, s_1, s_2, cr_1, en, hue, sd_hue, sat, sd_sat, value, sd_value, s_edge_d, ns_edge_d, edges, power):
    df = pd.DataFrame(
        {'Image': n,'Brightness': b, 'sdBrightness': sd_b, 'Green_pixel': g_p, 'Blue_pixel': b_p, 'Red_pixel': r_p, 'Neutral_pixel': n_p, 'Symmetry_MSE': s_1,
         'Symmetry_SSI': s_2, 'Contrast_RMS': cr_1, 'Shannon_Entropy': en, 'Hue': hue, 'sdHue': sd_hue, 'Saturation': sat, 'sdSaturation': sd_sat, 'Value': value, 'sdValue': sd_value, 'SED': s_edge_d, 'NSED': ns_edge_d, 'ED': edges, 'Power_spectrum': power})
    writer = pd.ExcelWriter('low-level-features.xlsx')
    df.to_excel(writer, index=False)
    writer._save()


VALID_IMAGE_EXTENSIONS = ['jpg', 'png', 'PNG']


@click.command()
@click.option('--path', prompt='path to image', help='The path to the image directory')
@click.option('--ext', type=click.Choice(VALID_IMAGE_EXTENSIONS), prompt='Image extension (jpg/png)', help='Specify the image extension')
@click.option('--brightness', default=True, help='Calculate brightness values')
@click.option('--color', default=True, help='Calculate color values')
@click.option('--contrast', default=True, help='Calculate contrast values')
@click.option('--entropy', default=True, help='Calculate entropy values')
@click.option('--edge_density', default=True, help='Calculate edge density')
@click.option('--mse', default=True, help='Calculate symmetry (MSE) values')
@click.option('--ssi', default=True, help='Calculate symmetry (SSI) values')
@click.option('--hsv_values', default=True, help='Calculate hsv properties')
@click.option('--power_spectrum', default=True, help='Calculate mean power spectrum')
def run(path, ext, brightness, color, contrast, entropy, edge_density, mse, ssi, hsv_values, power_spectrum):
    names = [file for file in os.listdir(path) if file.endswith(f".{ext}")]
    b_all = []
    sd_brightness = []
    green_pixel = []
    blue_pixel = []
    red_pixel = []
    neutral_pixel = []
    s_mse_all = []
    s_ssit_all = []
    con_bgr_rms = []
    entr = []
    hue = []
    sd_hue = []
    sat = []
    sd_sat = []
    value = []
    sd_value = []
    straight_edge_density_all = []
    non_straight_edge_density_all = []
    total_edges = []
    total_power_spectrum = []

    for x in names:
        img = io.imread(path + x)
        print('Processing image ', x)

        if brightness:
            bright, sd_bright = get_brightness(img)
            b_all.append(bright)
            sd_brightness.append(sd_bright)
        else:
            b_all.append('NA')
            sd_brightness.append('NA')

        if color:
            blue, green, red, neutral = classify_image_colors(img)
            green_pixel.append(green)
            blue_pixel.append(blue)
            red_pixel.append(red)
            neutral_pixel.append(neutral)
        else:
            green_pixel.append('NA')
            blue_pixel.append('NA')
            red_pixel.append('NA')
            neutral_pixel.append('NA')

        if entropy:
            entr.append(get_entropy(img))
        else:
            entr.append('NA')

        if mse:
            img = cv2.imread(path + x)
            flipped_img = cv2.flip(img, 1)
            s_mse_all.append(get_mean_square_error(img, flipped_img))
        else:
            s_mse_all.append('NA')

        if ssi:
            if not mse:
                img = cv2.imread(path + x)
                flipped_img = cv2.flip(img, 1)
            s_ssit_all.append(get_SSI(img, flipped_img))
        else:
            s_ssit_all.append('NA')

        if hsv_values:
            if not mse or not ssi:
                img = cv2.imread(path + x)
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, sd_h, s, sd_s, v, sd_v = get_hsv_values(img_hsv)
            hue.append(h)
            sd_hue.append(sd_h)
            sat.append(s)
            sd_sat.append(sd_s)
            value.append(v)
            sd_value.append(sd_v)

        else:
            hue.append('NA')
            sd_hue.append('NA')
            sat.append('NA')
            sd_sat.append('NA')
            value.append('NA')
            sd_value.append('NA')

        if edge_density:
            if not mse or not ssi or not hsv_values:
                img = cv2.imread(path + x)
            straight_edges, non_straight_edges, tot_edges = get_edge_density(img)
            straight_edge_density_all.append(straight_edges)
            non_straight_edge_density_all.append(non_straight_edges)
            total_edges.append(tot_edges)
        else:
            straight_edge_density_all.append('NA')
            non_straight_edge_density_all.append('NA')
            total_edges.append('NA')

        if contrast:
            img = cv2.imread(path + x)
            con_bgr_rms.append(get_contrast(img))
        else:
            con_bgr_rms.append('NA')

        if power_spectrum:
            if not mse or not ssi or not hsv_values or not contrast:
                img = cv2.imread(path + x)
            total_power_spectrum.append(get_power_spectrum(img))
        else:
            total_power_spectrum.append('NA')


    write_data(names, b_all, sd_brightness, green_pixel, blue_pixel, red_pixel, neutral_pixel, s_mse_all, s_ssit_all, con_bgr_rms, entr, hue, sd_hue, sat, sd_sat, value, sd_value, straight_edge_density_all, non_straight_edge_density_all, total_edges, total_power_spectrum)


if __name__ == '__main__':
    run()