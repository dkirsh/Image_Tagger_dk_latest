% Author: Izabela M Sztuka
% Before running this script, make sure to read the README file.


clc;
clear;
%----------Set up the paths and directories----------------
% root directory to this folder
root = pwd;
% name of image folder
image_folder = "stimuli";
% output directory
output = fullfile(root, 'output');

% make the output directory if it doesn't exist
if ~exist(output, 'dir')
    mkdir(output);
end

% base path
set(0, 'DefaultFigureVisible', 'off');
pathtoolbox = fullfile(root, 'toolbox/'); % path to the toolbox

% Add paths for various toolboxes
ber_path = fullfile(pathtoolbox, 'WholeIm_Decomposer_cc_ims.m'); % path to the Berman toolbox
addpath(genpath(fileparts(ber_path))); % add the directory of the Berman toolbox to the path
path_circ = fullfile(pathtoolbox, 'CircStat2012a/');
addpath(genpath(path_circ));
sed_path = fullfile(pathtoolbox, 'Str_Nstr_DecomposerV3/'); %Str_Nstr_DecompserV3ci.m spatial decomposer
addpath(genpath(sed_path));
color_path = fullfile(pathtoolbox, 'Count_Colors_variableDupIMS.m');
addpath(genpath(color_path));
fractal_path = fullfile(pathtoolbox, 'boxcount.m');
addpath(genpath(fractal_path));
lgn_statistics = fullfile(pathtoolbox, 'LGNstatistics-master/');
addpath(genpath(fileparts(lgn_statistics)));
warning('off', 'all');

%---------------Class Integration----------------
% Initialize the ImageDecomposer class
decomposer = ImageDecomposer(root, output, image_folder);
% Process the images
decomposer.decomposeImages();

%---------------Post-Processing----------------
% load feature names from load_featureheaders.csv
feature_header = readtable(fullfile(root, 'load_featureheaders.csv'));
% load the data
data = readtable(fullfile(output, 'stimuli.csv'));
% add the feature names to the data
data.Properties.VariableNames = feature_header.Properties.VariableNames;
% save the data
writetable(data, fullfile(output, 'stimuli.csv'), 'WriteMode', 'overwrite');
