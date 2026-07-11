function out = CompareColorHistograms(folder1,folder2,comparisonSet,test,displayFig)

% Compare Color Histograms of Two Image Sets
%   Script by Wilma A. Bainbridge
%   October 2, 2013
%
%   A script that compares the RGB (and Lab color space) information for
%   two image sets. You can elect which specific colors you want to test.
%   Both average intensity and standard deviation (contrast) are tested. To
%   ensure your two image sets have the same color distributions, run it as
%   the default and ensure none of the p-values that are outputted go below
%   your chosen threshold (often p < 0.05). You can also look at the
%   histograms for a sanity check to make sure the distributions look mostly overlapping.
%
%   Please cite both of these:
%   Bainbridge, W. A. & Oliva, A. (in submission). Interaction envelope: Local spatial representations of objects at all scales in scene-selective regions.
%   Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.
%
%   Usage:
%       out = CompareColorHistograms(folder1,folder2,comparisonSet,test,displayFig)
%       Ex: out =
%       CompareColorHistograms('images1/','images2/',{'R','G','B','L','a','b'},'permutation',true);
%           out = CompareColorHistograms('images1/','images2/');
%
%   Inputs:
%   folder1 = folder containing one set of images
%   folder2 = folder containing another set of images
%   comparisonSet = a matrix containing the color values you want compared.
%           Options are 'R','G','B','L','a','b'. Default is all of them.
%	test = 'ttest' to do an independent t-test between the image sets. This assumes a
%               unimodal, normal distribution of the colors
%           'permutation' to do a permutation test between the image sets.
%               This has no distribution assumptions.
%           The default is ttest.
%   displayFig = true displays the histogram figures, false does not.
%           Default is true.
%
%
%   Outputs:
%   out = This is a structure that contains the statistics for the color
%   values you enter in comparisonSet. For each color value, you will get:
%       1. avg1 & avg2 : The average intensities of that color value for
%       each image set.
%       2. std1 & std2 : The standard deviations of the intensities of that
%       color value for each image set. This can be thought of as contrast.
%       3. avgt & avgp : The statistical values comparing the average
%       intensities between the image sets. If you do a permutation test,
%       you will only get a p-value.
%       4. stdt & stdp : The statistical values comparing the contrasts of
%       the image sets. If you do a permutation test, you will only get a
%       p-value.

if nargin < 5; displayFig = true; end
if nargin < 4; test = 'ttest'; end
if nargin < 3; comparisonSet = {'R','G','B','L','a','b'}; end

histSize = 256;
histab = zeros(histSize,histSize);

% loop through the images in the first directory
ims1 = dir([folder1 '*jpg']);
for thisIm = 1:length(ims1)
    
    % take in the image
    names1{thisIm} = ims1(thisIm).name;
    ima = imread([folder1 names1{thisIm}]);
    ima = double(ima);
    ima = makesquare(ima);
    ima = imresize(ima, [histSize histSize]);
    
    % compare the RGB values (color differences)
    R=ima(:,:,1); G=ima(:,:,2); B=ima(:,:,3); % decompose the image in color plane
    avgR1(thisIm) = mean(mean(R)); avgG1(thisIm) = mean(mean(G)); avgB1(thisIm) = mean(mean(B));
    % this collapses the colors per pixel too
    avgI1(thisIm) = mean(mean((R+G+B)./3));
    
    % this gets the standard deviations (contrast)
    stdR1(thisIm) = std(reshape(R,1,[])); stdG1(thisIm) = std(reshape(G,1,[])); stdB1(thisIm) = std(reshape(B,1,[]));
    stdI1(thisIm) = std(reshape((R+G+B)./3,1,[])); % collapsed in pixels
    
    % try it in Lab space
    [L,a,b]=RGB2Lab(R,G,B);
    % compare the Lab (brightness & luminance)
    avgL1(thisIm) = mean(mean(L)); avga1(thisIm) = mean(mean(a)); avgb1(thisIm) = mean(mean(b));
    % the contrast
    stdL1(thisIm) = std(reshape(L,1,[])); stda1(thisIm) = std(reshape(a,1,[])); stdb1(thisIm) = std(reshape(b,1,[]));
end;

% loop through the images in the second directory
ims2 = dir([folder2 '*jpg']);
for thisIm = 1:length(ims2)
    
    % take in the image
    names2{thisIm} = ims2(thisIm).name;
    ima = imread([folder2 names2{thisIm}]);
    ima = double(ima);
    ima = makesquare(ima);
    ima = imresize(ima, [histSize histSize]);
    
    % compare the RGB values (color differences)
    R=ima(:,:,1); G=ima(:,:,2); B=ima(:,:,3); % decompose the image in color plane
    avgR2(thisIm) = mean(mean(R)); avgG2(thisIm) = mean(mean(G)); avgB2(thisIm) = mean(mean(B));
    % this collapses the colors per pixel too
    avgI2(thisIm) = mean(mean((R+G+B)./3));
    
    % this gets the standard deviations (contrast)
    stdR2(thisIm) = std(reshape(R,1,[])); stdG2(thisIm) = std(reshape(G,1,[])); stdB2(thisIm) = std(reshape(B,1,[]));
    stdI2(thisIm) = std(reshape((R+G+B)./3,1,[]));
    
    % try it in Lab space
    [L,a,b]=RGB2Lab(R,G,B);
    % compare the Lab (brightness & luminance)
    avgL2(thisIm) = mean(mean(L)); avga2(thisIm) = mean(mean(a)); avgb2(thisIm) = mean(mean(b));
    % the contrast
    stdL2(thisIm) = std(reshape(L,1,[])); stda2(thisIm) = std(reshape(a,1,[])); stdb2(thisIm) = std(reshape(b,1,[]));
end;

% now do all the statistics and make the output
for c = 1:length(comparisonSet)
    val = comparisonSet{c};
    out.(val).avg1 = eval(['avg' val '1']);
    out.(val).avg2 = eval(['avg' val '2']);
    out.(val).std1 = eval(['std' val '1']);
    out.(val).std2 = eval(['std' val '2']);
    
    % do hypothesis testing
    if strcmp(test,'permutation')
        out.(val).avgp = permutationTest(out.(val).avg1,out.(val).avg2,2,10000,false);
        out.(val).stdp = permutationTest(out.(val).std1,out.(val).std2,2,10000,false);
    else
        [h,p,ci,stats] = ttest2(out.(val).avg1,out.(val).avg2);
        out.(val).avgt = stats.tstat; out.(val).avgp = p;
        [h,p,ci,stats] = ttest2(out.(val).std1,out.(val).std2);
        out.(val).stdt = stats.tstat; out.(val).stdp = p;
    end
    
    if displayFig
        % For plotting various outputs
        % Do the average figure
        figure
        bar1 = hist(out.(val).avg1,40);
        bar2 = hist(out.(val).avg2,40);
        
        bar(bar1.','r');
        d = findobj(gca,'type','patch');
        set(d,'facealpha',0.75)
        hold on;
        bar(bar2.');
        h = findobj(gca,'type','patch');
        set(h,'edgecolor','w','facealpha',0.75)
        
        % Get axis limits so it's not right up to the edge
        ymax = max([bar1 bar2]);
        ylim([0 ymax+2]);

        title(['Histogram for average of ' val]);
        legend(folder1,folder2)
        legend('boxoff')
        
        % Do the standard deviation figure
        figure
        bar1 = hist(out.(val).std1,40);
        bar2 = hist(out.(val).std2,40);
        
        bar(bar1.','m');
        j = findobj(gca,'type','patch');
        set(j,'facealpha',0.75)
        hold on;
        bar(bar2.','c');
        k = findobj(gca,'type','patch');
        set(k,'edgecolor','w','facealpha',0.75)
        
        % Get axis limits so it's not right up to the edge
        ymax = max([bar1 bar2]);
        ylim([0 ymax+2]);

        title(['Histogram for standard deviation of ' val]);
        legend(folder1,folder2)
        legend('boxoff')
    end
end

