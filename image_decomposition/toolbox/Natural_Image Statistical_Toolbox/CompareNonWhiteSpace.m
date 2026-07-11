function [h,p,ci,stats] = CompareNonWhiteSpace(folder1,folder2,displayFig)

% Compare Proportion of Non-Empty Image Space Between Image Sets
%
%   Wilma Bainbridge
%   July 6, 2015
%
%   Citation:
%   Bainbridge, W. A. & Oliva, A. (in submission). Interaction envelope: Local spatial representations of objects at all scales in scene-selective regions.
%
%   For isolated object images sets against white backgrounds, compare the
%   proportions of non-white between the two. This is to ensure one image
%   set isn't retinotopically larger than the other.
%
%   Usage:
%       [h,p,ci,stats] = CompareNonWhiteSpace(folder1,folder2,displayFig);
%       Ex: [h,p,ci,stats] =
%       CompareNonWhiteSpace('images1/','images2/',true);
%           [h,p,ci,stats] = CompareNonWhiteSpace('images1/','images2/');
%
%   Inputs:
%   folder1 = first folder containing images
%   folder2 = second folder containing images for comparison
%   displayFig = true to display a histogram of the two sets, false to not.
%           Default is true.
%
%   Outputs:
%   [h,p,ci,stats] = the statistics from the t-test run between the two
%   folders.

if nargin < 3; displayFig = true; end

nonwhite1 = ProportionNonWhiteSpace(folder1);
nonwhite2 = ProportionNonWhiteSpace(folder2);

[h,p,ci,stats] = ttest2(nonwhite1,nonwhite2);

if displayFig
    % Plot the histogram
    figure
    bar1 = hist(nonwhite1,40);
    bar2 = hist(nonwhite2,40);
    
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
    
    title('Histogram for non-white space in images');
    legend(folder1,folder2)
    legend('boxoff')
end

end