% Author: Izabela M Sztuka
% Date: 2019 - 2024
% Description: 
% TBA

classdef ImageDecomposer
    properties
        BasePath
        OutputPath
        ImageFolder
        ImageNames
        NumImages
    end
    
    methods
        % Constructor
        function obj = ImageDecomposer(base_path, output, image_folder)
            obj.BasePath = base_path;
            obj.OutputPath = output;
            obj.ImageFolder = image_folder;
            in_images = fullfile(base_path, image_folder);
            img_dr = dir(in_images);
            obj.ImageNames = {img_dr.name};
            obj.ImageNames = obj.ImageNames(~ismember(obj.ImageNames, {'.', '..', '.DS_Store'}));
            obj.NumImages = length(obj.ImageNames);
        end
        
        % Main method to decompose images
        function decomposeImages(obj)
            for a = 1:obj.NumImages
                obj.decompositionImages(a);
            end
        end
        
        % Decomposition for a single image
        function decompositionImages(obj, a)
            close all
            fprintf('Processing image %d of %d\n', a, obj.NumImages);
            img = imread(fullfile(obj.BasePath, obj.ImageFolder, obj.ImageNames{a}));
            LLF = obj.classifier(img);
            LLF = table({obj.ImageNames{a}}, LLF);
            writetable(LLF, fullfile(obj.OutputPath, 'stimuli.csv'), 'WriteMode', 'append');
        end
        
        % Classifier function
        function frame = classifier(obj, maskedRgbImage)
            [avFeatsNofix, extraData] = WholeIm_Decomposer_cc_ims(maskedRgbImage);
            warning("WholeImDecomposer done");
            [EdgeStr, NSED, ED] = Str_NStr_DecomposerV3ci(maskedRgbImage);
            warning("Edge Density done");
            [color_value] = Count_Colors_variableDupIMS(maskedRgbImage, [60/360 120/360 180/360 240/360 300/360], [1/12 1/12 1/12 1/12 1/12 1/12], 0.05);
            warning("Color decomp done");
            [df, df_std] = obj.fractal(maskedRgbImage);  % Correct reference to obj.fractal
            warning("LGN in progress");
            [CE, SC, Beta, Gamma] = run_LGNstatistics(maskedRgbImage);
            [Ef, Qhf] = obj.calculateSpectraEnergy(maskedRgbImage);
            warning("power spectra calculated");
            frame = [avFeatsNofix extraData EdgeStr NSED ED df df_std color_value CE SC Beta Gamma Ef Qhf];
        end
        
        % Fractal function
        function [df, df_std] = fractal(obj, maskedRgbImage)
            I = rgb2gray(maskedRgbImage);
            [m, r] = boxcount(I);
            dff = (-diff(log(m))./diff(log(r)));
            df = mean(dff(4:end));
            df_std = std(dff(4:end));
        end
        
        % CalculateSpectraEnergy function
        function [Ef, powerSpectrumAverage] = calculateSpectraEnergy(obj, img)
            targetSize = [256, 256];
            if ~isequal(size(img, 1:2), targetSize)
                img = imresize(img, targetSize);
            end
            [m, n, c] = size(img);
            g = hamming(m) * hamming(n)';
            if c == 3
                imgBW = rgb2gray(img);
            else
                imgBW = img;
            end
            imgBW = double(imgBW);
            windowedImg = imgBW .* g;
            fftImg = fftshift(fft2(windowedImg));
            powerSpectrum = abs(fftImg).^2;
            Ef = sum(powerSpectrum(:));
            powerSpectrumAverage = mean(powerSpectrum(:));
        end
    end
end
