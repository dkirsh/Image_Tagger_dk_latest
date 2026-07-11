function [CE, SC, Beta, Gamma] = run_LGNstatistics(maskedRgbImage)

% wrapper function that executes LGNstatistics on each image in the
% directory it is run from

% names = dir('*.jpg');
% names2 = dir('*.jpeg');
% names3 = dir('*.bmp');
% names4 = dir('*.png');
% names5 = dir('*.tif');
    
% names = [names; names2; names3; names4; names5];

CE = nan(1,3); 
SC = nan(1,3);
Beta = nan(1,3);
Gamma = nan(1,3);

%for cNames = 1:length(names)
%     if names(cNames).bytes > 0
im = maskedRgbImage;
[CE,SC,Beta,Gamma] = LGNstatistics(im);
%     end
%     filenames{cNames} = names(cNames).name;
%     disp(cNames);
%end

%matname = 'LGNstatistics';

%try 
%	save(matname,'CE','SC', 'Beta', 'Gamma', 'filenames');
%catch
%    delete(matname);
%	save(matname,'CE','SC', 'Beta', 'Gamma', 'filenames');
end