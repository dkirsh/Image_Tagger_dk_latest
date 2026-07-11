function [Ef_t, Ef_p, Qhf_t, Qhf_p] = CompareSpectraEnergy(folder1, folder2, hfci, levels, displayFig)

% Compare Spectra Energy (Spatial Frequencies) of Two Image Sets
%   Script by Wilma A. Bainbridge
%
%   This script goes through different energy levels (every 20th level from
%   10% to 100%) and compares the Ef and Hf for two different image sets at
%   each level, to see if they significantly differ in spatial frequency.
%   If any value of Ef_p or if Qhf_p goes below your selected significance
%   threshold (often p < 0.05), then your image sets are significantly
%   different in spatial frequency.
%   Note that this takes a handful of seconds to run.
%
%   Please cite both of these:
%   Bainbridge, W. A. & Oliva, A. (in submission). Interaction envelope: Local spatial representations of objects at all scales in scene-selective regions.
%   Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.
%
%   Usage:
%       [Ef_t, Ef_p, Qhf_t, Qhf_p] = compareSpectraEnergy(folder1, folder2... hfci, levels, displayFig)
%       Ex: [Ef_t, Ef_p, Qhf_t, Qhf_p] = compareSpectraEnergy('condition1/','condition2/',10,10:20:100,true)
%           [Ef_t, Ef_p, Qhf_t, Qhf_p] = compareSpectraEnergy('condition1/','condition2/')
% 
%   Inputs:
%   folder1 = folder containing one set of images
%   folder2 = folder containing another set of images
%	hfci = cycle/image value for calculating the quantity of HSF > hfci.
%       Default is 10.
%   levels = the levels to test at. Default is 10:20:100
%   displayFig = true if you want to see average image and power spectrum
%   information for the two folders. false if you do not. Default is true.
%
%   Outputs:
%   Ef_t and Ef_p : the t statistic and p-value from independent t-tests
%       between the Efs of the two image sets, at each level.
%   Qhf_t and Qhf_p: the t statistic and p-value from independent t-tests
%       between the Qhfs of the two image sets. It is always the same at
%       every level.

if nargin < 5; displayFig = true; end
if nargin < 4; levels = 10:20:100; end
if nargin < 3; hfci = 10; end

for c = 1:length(levels)
    level = levels(c);
    
    [Ef1, Qhf1] = CalculateSpectraEnergy(folder1,level,hfci,false);
    [Ef2, Qhf2] = CalculateSpectraEnergy(folder2,level,hfci,false);
   
    [h, Ef_p(c), ci, stats] = ttest2(Ef1, Ef2);
    Ef_t(c) = stats.tstat;
    if c == 1 % Because Qhf is the same at every level
        [h, Qhf_p, ci, stats] = ttest2(Qhf1, Qhf2);
        Qhf_t = stats.tstat;
    end
    
    disp(['Done with ' num2str(level) '% level']);
end

if displayFig
    [img fft] = AverageAndPowerSpectrum(folder1);
    [img fft] = AverageAndPowerSpectrum(folder2);
end