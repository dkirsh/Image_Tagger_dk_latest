function [ avFeatsNofix, extraData ] = WholeIm_Decomposer_cc( Folder_Address )
% Generates a Matrix where columns are in order
% Edge-Density, Hue, Saturation, Brightness, std of Hue, std of Saturation,
% std of brightness, and Entropy of a batch of images that are
% located in the folder specified in the input argument Folder_Address

% Example: WholeIm_Decomposer('D:\MayanEyetracking\Stimuli')

%   Citations:
%   [1] Kardan, O., Demiralp, E., Hout, M. C., Hunter, M. R., Karimi, H., Hanayik, T., ... & Berman, M. G. (2015). Is the preference of natural versus man-made scenes driven by bottom�up processing of the visual features of nature?. Frontiers in psychology, 6.
%   [2] Berman, M. G., Hout, M. C., Kardan, O., Hunter, M. R., Yourganov, G., Henderson, J. M., ... & Jonides, J. (2014). The perception of naturalness correlates with low-level visual features of environmental scenes. PloS one, 9(12), e114572.

%     *Note: make sure CircStat2012a folder is added in the MATLAB path:
%     *Circular Statistics Toolbox for Matlab, By Philipp Berens, 2009; berens@tuebingen.mpg.de - www.kyb.mpg.de/~berens/circStat.html

addpath('CircStat2012a/');
%addpath('/Users/cassanello/Documents/interiorDesign+fractalDimension/ImageDecomposer/CircStat2012a');

addpath(Folder_Address);
names = dir([Folder_Address,'*.jpg']); %dir(Folder_Address);
Hue=[];
Sat=[];
Lum=[];
ED=[];
ED0=[];
EDlev = [];
EDLog = [];
EDLoglev = [];
EDLogFT = [];
Entropyy=[];
sdHue=[];
sdSat=[];
sdBright=[];
labL = []; labA = []; labB = []; sdlabL =[]; sdlabA = []; sdlabB = [];
EtrH = []; EtrS = []; EtrV = []; EtrL = []; EtrA = []; EtrB = [];
EDH0 = []; EDS0 = []; EDV0 = []; EDL0 = []; EDA0 = []; EDB0 = [];
% imname={};
num_image = length(names); %

for k=1:num_image %
    imnamee = names(k).name;
    %disp(imnamee);
    tempp1=imread(imnamee); % loads image imnamee
    [s1, s2, s3]=size(tempp1); % gets size of the image in pixels
    kgb=s1*s2; % total number of pixels
    if s3 == 3
        tempp1g = rgb2gray(tempp1); % converts the image to gray levels from rgb
        tempp1c = rgb2hsv(tempp1); % converts the image from rgb to hsv
        tempp1L = rgb2lab(tempp1);
    elseif s3 == 1
        tempp1g = tempp1;
        tempp1c = tempp1;
        tempp1L = tempp1;
    end
    [cann0, level]=edge(tempp1g,'canny'); % bare canny edge map with level asign by matlab anr reported in level
    cann2=edge(tempp1g,'canny',0.8*level); % low threshold edge map
    cann1=edge(tempp1g,'canny',1.6*level); % high threshold edge map
    tempp1a=(cann1+cann2)/2; % average map between low and high thresholds
    [tempplg, loglev] = edge(tempp1g,'log'); % my edge map extraction using LOG method also from the gray level map; for our set the mean level across images was 0.037
    tempplgft = edge(tempp1g,'log',0.001); % my edge map extraction with a lower threshold forced by hand; same for all images though which is probably not right

    % compute edges over the components of hsv and lab
    [canH0, levH] = edge(tempp1c(:,:,1),'canny');
    [canS0, levS] = edge(tempp1c(:,:,2),'canny');
    [canV0, levV] = edge(tempp1c(:,:,3),'canny');

    [canL0, levL] = edge(tempp1L(:,:,1),'canny');
    [canA0, levA] = edge(tempp1L(:,:,2),'canny');
    [canB0, levB] = edge(tempp1L(:,:,3),'canny');



    edd=sum(sum(tempp1a))/kgb; % normalization: each edge map is a matrix of 0s and 1s with a 1 in each pixel where an edge was detected; this steps sums over all 1s and divides by the picture size in pixels
    edd0=sum(sum(cann0))/kgb; % normalization for the bare canny map
    eddH0 = mean2(canH0);
    eddS0 = mean2(canS0);
    eddV0 = mean2(canV0);
    eddL0 = mean2(canL0);
    eddA0 = mean2(canA0);
    eddB0 = mean2(canB0);

    entr = entropy(tempp1g); % entropy extraction
    entrH = entropy(tempp1c(:,:,1));
    entrS = entropy(tempp1c(:,:,2));
    entrV = entropy(tempp1c(:,:,3));
    entrL = entropy(tempp1L(:,:,1)/100);
    entrA = entropy(tempp1L(:,:,2));
    entrB = entropy(tempp1L(:,:,3));

    eddlg = sum(sum(tempplg))/kgb; % normalization for my edge density using log
    eddlgft = sum(sum(tempplgft))/kgb; % normalization for my edge density using fix threshold in log method
    if s3 == 3
        sdsatt = std2(tempp1c(:,:,2)); % std for saturation; uses hsv converted map of the image
        sdbrightt=std2(tempp1c(:,:,3)); % std fro brightness; uses hsv converted map of the image

        [huee, ul, ll] = circ_mean(circ_mean(2*pi*tempp1c(:,:,1), ones(size(tempp1c(:,:,1)))),ones(1,size(tempp1c(:,:,1),2)),2); % hue conversion from matlab value in the hsv map to a circular variable
        AA = reshape(tempp1c(:,:,1),[s1*s2,1]);
        [s, sdhuee] = circ_std(2*pi*AA);

        satt=sum(sum(tempp1c(:,:,2)))/kgb; % saturation normalized to size from Matlab's hsv map
        brightt=sum(sum(tempp1c(:,:,3)))/kgb; % same for brightness

        Hue = [Hue; huee]; % here column variables are collected across images to report in the table at the end
        Sat = [Sat; satt];
        Lum = [Lum; brightt];
        sdHue = [sdHue; sdhuee];
        sdSat = [sdSat; sdsatt];
        sdBright = [sdBright; sdbrightt];

        labL = [labL; mean2(tempp1L(:,:,1))];
        labA = [labA; mean2(tempp1L(:,:,2))];
        labB = [labB; mean2(tempp1L(:,:,3))];

        sdlabL = [sdlabL; std2(tempp1L(:,:,1))];
        sdlabA = [sdlabA; std2(tempp1L(:,:,2))];
        sdlabB = [sdlabB; std2(tempp1L(:,:,3))];

    elseif s3 == 1
        Hue = [Hue; 0]; % here column variables are collected across images to report in the table at the end
        Sat = [Sat; 0];
        sdHue = [sdHue; 0];
        sdSat = [sdSat; 0];
        brightt=sum(sum(tempp1c))/kgb; % same for brightness
        sdbrightt=std2(tempp1c); % std fro brightness; uses hsv converted map of the image
        Lum = [Lum; brightt];
        sdBright = [sdBright; sdbrightt];
    end


    ED = [ED; edd]; % this is the edge density that Berman, Kardan, et al report (left plot in the 3-subplot comparison I sent)
    ED0 = [ED0; edd0]; % I added this to have an idea of the bare canny result without the double thresholding
    EDlev = [EDlev; level]; % this reports the levels that Matlab automatically assign at the 'bare' canny level before and on which the double thresholding is then based
    EDLog = [EDLog; eddlg]; % these are the edge densities using the LOG method and letting Matlab assign the threshold (middle plot in the figure I sent)
    EDLogFT = [EDLogFT; eddlgft]; % edge density using LOG with external forced threshold at 0.001 (right plot in the figure I sent)
    EDLoglev = [EDLoglev; loglev]; % reports the levels that Matlab assigns with the LOG method when no threshold is provided
    Entropyy = [Entropyy; entr]; % rest of Berman's features
    imname{k} = imnamee;
    EDH0 = [EDH0; eddH0];
    EDS0 = [EDS0; eddS0];
    EDV0 = [EDV0; eddV0];
    EDL0 = [EDL0; eddL0];
    EDA0 = [EDA0; eddA0];
    EDB0 = [EDB0; eddB0];

    EtrH = [EtrH; entrH];
    EtrS = [EtrS; entrS];
    EtrV = [EtrV; entrV];
    EtrL = [EtrL; entrL];
    EtrA = [EtrA; entrA];
    EtrB = [EtrB; entrB];

end
if s3 == 3
    extraData = table(imname', labL, labA, labB, sdlabL, sdlabA, sdlabB, EDH0, EDS0, EDV0, EDL0, EDA0, EDB0, EtrH, EtrS, EtrV, EtrL, EtrA, EtrB, 'VariableNames',{'ImgName','labL','labA','labB','sdlabL','sdlabA','sdlabB','EDHue','EDSat','EDVal','EDL','EDA','EDB','ETH','ETS','ETV','ETL','ETA','ETB'});
    avFeatsNofix = table(imname', ED, ED0, EDLog, EDLogFT, Hue, Sat, Lum, sdHue, sdSat, sdBright, Entropyy, EDlev, EDLoglev,'VariableNames',{'ImgName','EdgeDensity','EdgeBareCanny','EdgeLog','EdgeLogFT','Hue','Saturation','Brightness','sdHue','sdSat','sdBright','Entropy','EDlev','EDLoglev'});
elseif s3 == 1
    avFeatsNofix = table(imname', ED, ED0, EDLog, EDLogFT, Lum, sdBright, Entropyy, EDlev, EDLoglev,'VariableNames',{'ImgName','EdgeDensity','EdgeBareCanny','EdgeLog','EdgeLogFT','Brightness','sdBright','Entropy','EDlev','EDLoglev'});
end
    save avFeatsNofix avFeatsNofix % this saves a matlab file with the table but can be commented out
%end
