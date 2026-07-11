% Permutation test for non-normal curves
%   Wilma Bainbridge (w/ help from Radoslaw Cichy)
%   October 2 2013
%
%   This runs a permutation statistical test for comparing two non-unimodal
%   distributions
%
%   Please cite:
%   Bainbridge, W. A. & Oliva, A. (in submission). Interaction envelope: Local spatial representations of objects at all scales in scene-selective regions.
%
%   Usage:
%       p = permutationTest(data1,data2,sides,samples)
%       Ex: p = permutationTest(rand([1 20]),rand([1 20]),2,10000);
%           p = p = permutationTest(rand([1 20]),rand([1 20]));
%
%   Inputs:
%   data1 = a vector you want to compare
%   data2 = another vector you want to compare. data1 and data2 must be the
%   same length.
%   sides = either 1 for a one-sided test or 2 for a two-sided test.
%   Default is 2.
%   samples = number of iterations to do (the more the better, but the more
%   computationally intensive). Default is 10,000
%   displaylFig = display figure (true) or not (false). Default is true.
%
%   Outputs:
%   p = the resulting p-value from the permutation test


function p = permutationTest(data1,data2,sides,samples,displayFig)

if nargin < 5; displayFig = true; end
if nargin < 4; samples = 10000; end
if nargin < 3; sides = 2; end

subDat = data1-data2;
meanDat = mean(subDat);
for c = 1:samples
    temp = double(rand(length(subDat),1)>0.5);
    temp(temp==0) = -1;
    permmean(c) = mean(subDat .* temp');
end

if sides == 1
    p = sum(permean>meanDat)/samples; % one sided
else
    p = sum(abs(permmean)>abs(meanDat))/samples; % two sided
end

if displayFig
    fh = figure;
    ah = axes;
    hist(permmean,100);
    hold on
    plot([meanDat,meanDat],get(ah,'YLim'));
    title(['p=' num2str(p)]);
end

end