function [propnonwhite] = ProportionNonWhiteSpace(maskedRgbImage)

% Calculate Proportion of Non-Empty Image Space
%
%   Wilma Bainbridge
%   July 2, 2013
%
%   Citation: 
%   Bainbridge, W. A. & Oliva, A. (in submission). Interaction envelope: Local spatial representations of objects at all scales in scene-selective regions.
%
%   For isolated object images, calculate how much of the image isn't the
%   white background. This is useful for comparison of image sets to ensure
%   one doesn't just have objects of larger retinal size than the other.
%
%   Note: also counts white objects as background, not very sophisticated!
%   Though this would not be a trivial issue to fix. This should be good
%   enough for comparing image sets, since one image isn't going to throw
%   off the statistics.
%
%   Usage:
%       [propnonwhite] = ProportionNonWhiteSpace(folder);
%       Ex: propnonwhite = ProportionNonWhiteSpace('images/');
%
%   Inputs:
%   folder = folder containing the set of images.
%
%   Outputs:
%   propnonwhite = a vector with the proportion of non-white space for each
%   of the images in the directory.

% diry = [dir([folder '*.jpg']) ;dir([folder '*.jpeg']) ;dir([folder '*.tif']) ;dir([folder '*.tiff']) ;dir([folder '*.bmp'])]; 

% Nimages = length(diry);

% for i = 1:Nimages
    %imname{i} = diry(i).name;
    img = maskedRgbImage;
    imgsize = size(img,1)*size(img,2);
    white = length(img((img(:,:,1)==255) & (img(:,:,2)==255) & (img(:,:,3)==255)));
    propnonwhite = 1- white / imgsize;
end
  