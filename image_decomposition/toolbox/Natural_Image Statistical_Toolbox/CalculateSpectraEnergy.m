function [Ef Qhf] = CalculateSpectraEnergy(maskedRgbImage, level, hfci, displayFig)

% Calculate Spectra Energy in a Set of Images
%   Script by Aude Oliva, adapted by Wilma Bainbridge
%
%   Citation: 
%   Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.
%
%   Usage:
%       [Ef Qhf] = CalculateSpectraEnergy(folder... level, hfci, displayFig)
%       Ex: [Ef Qhf] = CalculateSpectraEnergy('imageFolder/',80,10,true);
%           [Ef Qhf] = CalculateSpectraEnergy('imageFolder/');
% 
%   folder = folder containing the set of images.
%   level = level of energy you want to look at (from 1 to 100%). Default
%       is 80.
%	hfci = cycle/image value for calculating the quantity of HSF > hfci.
%       Default is 10.
%	displayFig = true if you want to see the spatial frequency figure,
%       false if not. Default is true.
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CALCULATE IMAGE ENERGY: Ef
% level is a number between 0 and 100: e.g. level of energy 80%
%
% returns 'Ef' which is the frequency that contains the specified amount of
% energy in cycle/image.
% e.g. Ef = 3 c/i is very low spatial frequency. 
%
% CALCULATE QUANTITY OF HSF: Qhf
% hfci is a number between 1 c/i to the maximum frequency (image
% size/2): e.g. 10
% return Qhf, which is the % of HSF above "hfci" image/cycle

% NOTE: IMAGES TO COMPARE MUST ALL HAVE THE SAME SIZE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if nargin < 4; displayFig = true; end
if nargin < 3; hfci = 10; end
if nargin < 2; level = 80; end

m=256;
n=256;

%files = [dir([folder '*.jpg']) ;dir([folder '*.jpeg']) ;dir([folder '*.tif']) ;dir([folder '*.tiff']) ;dir([folder '*.bmp'])]; 
%Nimages = length(files);

%if Nimages == 0
%    disp('Error: No images in folder')
%    return
%end

% Hamming window to reduce boundary artifacts, that will be multiplied with
% the Power spectrum: mesh(g). 
g = hamming(m)*hamming(n)';
[fx, fy] = meshgrid(1:n,1:m); fx = fx - n/2-1; fy = fy-m/2-1;
fr = sqrt(fx.^2+fy.^2); % radial frequency for each pixel of the spectrum
% see imagesc(fr<30) -- e.g. 30 pixels -- to see the role of this line: it
% creates a mask

% for i = 1:Nimages
    img = maskedRgbImage; %imread([folder files(i).name]);
    [m,n,c] = size(img); if c == 1; img = repmat(img,[1 1 3]); end
    img = imresize(img, [m n]); 
    img = double(mean(img,3));
    img=(img-mean(img(:))); 
    
    P=fftshift(abs(fft2(img.*g))); % Amplitude spectrum: imagesc(P)
    P = P.^2; % Power spectrum as we want to calculate the energy E
    P = P / sum(P(:)); % to have the total image energy (sum(sum(P)) = 1. look at imagesc(log(P))

    E = zeros([1 round(max(fr(:)))]); % size(E) is the max frequency of the image "along the diagonal". e.g. number of pixels between the center and a corner following a diagonal line
    % Now calculate the Energy for each circle (radial frequency)
        for j = 1:round(max(fr(:)));
           E(j) = sum(sum(P.*(fr<j))); % Energy = Power spectrum X fr. sum of all values within a circle growing in size
         end
    E = E*100; % here plot(E). E contains the Energy for level of energy 1%, 2%, ... 80%,.. 100%. this is what you want to save for each image
    
    Ef(i)= find(E>level, 1 ); % choose a specific level, like 80%. f is the frequency in cycle/image that contains 80% of energy. if f is small (e.g. 3c/i), the image does not have medium and high SF. high values are ~ 16-25 for 80% E.
    
    Qhf(i) = (sum(sum(P.*(fr>hfci))))*100;
% end

% if displayFig
%     figure
%     subplot(1,3,1)
%     imagesc(img); axis('off'); axis('square')
%     title('example image')
%     subplot(1,3,2)
%     imagesc(log(P)); axis('square')
%     title('power spectrum')
%     subplot(1,3,3)
%     imagesc(fr<level); axis('square')
%     colormap(gray(256))
%     title('chosen level')
end
