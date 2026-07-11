function [ avFeatsNofix ] = WholeIm_Decomposer( Folder_Address )
% Generates a Matrix where coulmns are in order
% Edge-Density, Hue, Saturation, Brightness, std of Hue, std of Saturation,
% std of brightness, and Entropyy of a batch of images that are 
% located in the folder specified in the input argument Folder_Address

% Example: WholeIm_Decomposer('D:\MayanEyetracking\Stimuli')

%   Citations: 
%   [1] Kardan, O., Demiralp, E., Hout, M. C., Hunter, M. R., Karimi, H., Hanayik, T., ... & Berman, M. G. (2015). Is the preference of natural versus man-made scenes driven by bottom–up processing of the visual features of nature?. Frontiers in psychology, 6.
%   [2] Berman, M. G., Hout, M. C., Kardan, O., Hunter, M. R., Yourganov, G., Henderson, J. M., ... & Jonides, J. (2014). The perception of naturalness correlates with low-level visual features of environmental scenes. PloS one, 9(12), e114572.

%     *Note: make sure CircStat2012a folder is added in the MATLAB path:
%     *Circular Statistics Toolbox for Matlab, By Philipp Berens, 2009; berens@tuebingen.mpg.de - www.kyb.mpg.de/~berens/circStat.html
  
%names = dir([Folder_Address, '\*.jpg']);
names = dir([Folder_Address, '\*.jpg']);
Hue=[];
Sat=[];
Lum=[];
ED=[];
Entropyy=[];
sdHue=[];
sdSat=[];
sdBright=[];
num_image = length(names(not([names.isdir]))); % 

for k=1:num_image % 
    imnamee = names(k).name;
    tempp1=imread(imnamee);
    tempp1g=rgb2gray(tempp1);
    [s1 s2 s3]=size(tempp1);
    kgb=s1*s2;
    tempp1c=rgb2hsv(tempp1);
    
    [~, level]=edge(tempp1g,'canny');
    cann2=edge(tempp1g,'canny',0.8*level); 
    cann1=edge(tempp1g,'canny',1.6*level);
    tempp1a=(cann1+cann2)/2;
    
    
    
    edd=sum(sum(tempp1a))/kgb;
    entr = entropy(tempp1g);
    
    sdsatt=std2(tempp1c(:,:,2));
    sdbrightt=std2(tempp1c(:,:,3));
    
    [huee ul ll] = circ_mean(circ_mean(2*pi*tempp1c(:,:,1), ones(size(tempp1c(:,:,1)))),ones(1,size(tempp1c(:,:,1),2)),2);
    AA = reshape(tempp1c(:,:,1),[s1*s2,1]);
    [s sdhuee] = circ_std(2*pi*AA);
    
    satt=sum(sum(tempp1c(:,:,2)))/kgb;
    brightt=sum(sum(tempp1c(:,:,3)))/kgb;
    
    
    Hue=[Hue;huee];
    Sat=[Sat;satt];
    Lum=[Lum;brightt];
    ED=[ED;edd];
    Entropyy=[Entropyy;entr];
    sdHue=[sdHue;sdhuee];
    sdSat=[sdSat;sdsatt];
    sdBright=[sdBright;sdbrightt];
%     imname = [imname;imnamee];
    disp(k);
end
avFeatsNofix =[ED Hue Sat Lum sdHue sdSat sdBright Entropyy];
% avFeatsNofixH =['Name' 'ED' 'Hue' 'Sat' 'Lum' 'sdHue' 'sdSat' 'sdBright' 'Entropyy'];
% avFeatsNofix = [avFeatsNofixH; avFeatsNofix1];

end

