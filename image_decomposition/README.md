##### READ ME
# Project Title: Image Decomposer

## Author

- Name: Izabela Maria Sztuka
- Affiliation: Center for Environmental Neuroscience, Max Planck Institute for Human Development
- Contact: imsztuka@protonmail.com/sztuka@mpib-berlin.mpg.de

- Version: 4.0
- Data of last update: 07/24

## Publication

- Sztuka, I. M., & Kühn, S. Blue Skies: Does Visual Composition of Sky Guide Subjective Judgments of Naturalness in the Environment?. Available at SSRN: https://ssrn.com/abstract=4741220 or http://dx.doi.org/10.2139/ssrn.4741220
- Sztuka, I. M., Becker, M. & Kühn, S. Neural representations underlying psychological responses to natural and artificial features in indoor architecture. (in review, Journal for Environmental Psychology)

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repositorystructure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Notes](#notes)
- [Acknowledgments](#acknowledgments)

# ImageDecomposer

## Overview
The `ImageDecomposer` is a MATLAB class that decomposes images into various features using multiple toolboxes. This project is designed to handle large batches of images, extract their features, and save the results in a CSV file. It uses a combination of several toolboxes, including Berman, CircStat, Str_Nstr_DecomposerV3, Count_Colors_variableDupIMS, boxcount, and LGNstatistics.

## Repository Structure

├──ImageDecomposer.m # MATLAB class for image decomposition
├── mainScript.m # Main script to run the decomposition
├── toolbox/ # Directory containing various toolboxes
├── stimuli/ # Directory containing input images
├── output/ # Directory to store output CSV file
├── load_featureheaders.csv # CSV file with feature headers
└── README.md # Notes and instructions

## Prerequisites
- MATLAB installed on your system (tested with 2019 up)
- Required toolboxes placed in the `toolbox` directory:
  - WholeIm_Decomposer_cc_ims.m (Berman toolbox)
  - CircStat2012a (CircStat toolbox)
  - Str_Nstr_DecomposerV3ci (Str_Nstr_DecomposerV3 toolbox)
  - Count_Colors_variableDupIMS.m
  - boxcount.m
  - LGNstatistics-master
- Note these toolboxes have been modified first by Carlos then by me to work with this script.

## Setup
1. Clone this repository to your local machine.
2. Ensure that all required toolboxes are available in the `toolbox` directory.
3. Place your input images in the `stimuli` directory.

## Usage
1. Open MATLAB and navigate to the repository directory.
2. Open `mainScript.m` and modify parameters of the analysis.
2. Run the `mainScript.m` to start the image decomposition process.

### Process
- The script performs the following steps:
1. Sets up the paths and directories.
2. Initializes the ImageDecomposer class.
3. Processes each image in the stimuli directory.
4. Loads feature names from load_featureheaders.csv.
5. Reads the decomposed data from output/stimuli.csv and updates the feature names.
6. Saves the updated data back to output/stimuli.csv.

### Example

```Matlab
% Set up paths and parameters
root = pwd;
image_folder = "stimuli";
output = fullfile(root, 'output');

% Initialize the ImageDecomposer class
decomposer = ImageDecomposer(root, output, image_folder);

% Process the images
decomposer.decomposeImages();
```

## Notes

### Contents

* WholeIm_Decomposer - toolbox to extraxt hue, saturation, brightness, entropy, edge density. Modified in LMG by CC & IMS. Method used in Nature_gradient & ARCH studies.
Published: [1] Kardan, O., Demiralp, E., Hout, M. C., Hunter, M. R., Karimi, H., Hanayik, T., ... & Berman, M. G. (2015). Is the preference of natural versus man-made scenes driven by bottom�up processing of the visual features of nature?. Frontiers in psychology, 6. [2] Berman, M. G., Hout, M. C., Kardan, O., Hunter, M. R., Yourganov, G., Henderson, J. M., ... & Jonides, J. (2014). The perception of naturalness correlates with low-level visual features of environmental scenes. PloS one, 9(12), e114572.

* CircStat2012a - auxiliary toolbox for circular statistics. Used by WholeIm_Decomposer. Published: [3] Berens, P., CircStat: A Matlab Toolbox for Circular Statistics, Journal of Statistical Software, Volume 31, Issue 10, 2009

* SHINEtoolbox - toolbox to control for low-level image properties by normalising contrast and luminance. Published: [4] Willenbockel, V., Sadr, J., Fiset, D., Horne, G. O., Gosselin, F., & Tanaka, J. W. (2010). Controlling low-level image properties: the SHINE toolbox. Behavior research methods, 42(3), 671-684.

* Str_Nstr_DecomposerV3 - 3 versions of function to extract straight & non-straight edge density. Used in publications [1] & [2]. Modified by CC (Str_NStr_DecomposerV3c.m) and IMS (Str_NStr_DecomposerV3ci.m). Method used in Nature_gradient & ARCH studies.

* Count_Colors_variableDup - function to qualtify colours on the images. Created by Carlos Cassanello.

* fractal_analysis - function conducting fractal analysis of the image using boxcounting with either binary or differential method. Created by IMS. Method as used in: [5] Nature_gradient (https://doi.org/10.3389/fpsyg.2022.932507) & ARCH studies (in preparation)

## Acknowledgments

