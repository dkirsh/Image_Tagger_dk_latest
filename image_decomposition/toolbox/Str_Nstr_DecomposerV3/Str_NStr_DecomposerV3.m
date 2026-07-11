function [ EdgeStr, NSED, ED, edgeDensities] = Str_NStr_DecomposerV3( Folder_Address )

% Version 3.0 by Omid Kardan okardan@uchicago.edu

%     Example: [straightnonstraight, imagenames] = Str_NStr_DecomposerV3('D:\MyDirectory\Stimuli')
%     *Note: make sure the folder 'gaussgradient' is added in the MATLAB path:
%      Contributed by Guanglei Xiong (xgl99@mails.tsinghua.edu.cn) at Tsinghua University, Beijing, China.

%   Relevant citations: 
%   Previous versions of this code has been developed and used for the following:
%   [1] Kardan, O., Demiralp, E., Hout, M. C., Hunter, M. R., Karimi, H., Hanayik, T., ... & Berman, M. G. (2015). Is the preference of natural versus man-made scenes driven by bottom�up processing of the visual features of nature?. Frontiers in psychology, 6.
%   [2] Berman, M. G., Hout, M. C., Kardan, O., Hunter, M. R., Yourganov, G., Henderson, J. M., ... & Jonides, J. (2014). The perception of naturalness correlates with low-level visual features of environmental scenes. PloS one, 9(12), e114572.
%Folder_Address = 'D:\str_nstr_script';
addpath(Folder_Address);
names = dir([Folder_Address, '/*.tif']);
num_image = length(names(not([names.isdir])));

%im_files = names.name;
EdgeStr = [];
NSED = [];
ED = [];

for k=1:num_image
    imnamee = names(k).name;
   
    temppp=imread(char(names(k).name));
    temppp=im2double(temppp);
    %temppp=imresize(temppp,[600,800]);
    temppps=rgb2hsv(temppp);
    temppp=rgb2gray(temppp);
    tempppsat=temppps(:,:,2);  % Saturation-based edge detection on
    %temppphue=temppps(:,:,1);  % Hue-based edge detection off
    temppp1=(edge(tempppsat,'canny',[0.08 0.12])-edge(temppp,'canny',[0.08 0.12])).^2 + edge(temppp,'canny',[0.08 0.12]);

[a1,b1]=size(temppp);
   
    ttt=bwareaopen(medfilt2(temppp1.*edge(temppp,'sobel',0.05,'vertical'),[4 1]),15)+bwareaopen(medfilt2(temppp1.*edge(tempppsat,'sobel',0.05,'vertical'),[4 1]),15);
    ttt2=bwareaopen(medfilt2(temppp1.*edge(temppp,'sobel',0.05,'horizontal'),[1 4]),15)+bwareaopen(medfilt2(temppp1.*edge(tempppsat,'sobel',0.05,'horizontal'),[1 4]),15);
     teta0=zeros(size(temppp));
     par90=0;par45=0;par3=0;par4=0;par5=0;
     edges=edge(temppp,'canny',[0.01 0.05]);
     [gx,gy]=gaussgradient(temppp,1);
for i=1:size(gy,1)
    for j=1:size(gy,2)
        if  ((gy(i,j)<20 && gx(i,j)<1) || ((gy(i,j)<1 && gx(i,j)<20)))
            teta0(i,j)=pi; 
        end
    end
end
gx1=im2double(gx);
gy1=im2double(gy);
teta=atan2(gy1,gx1);
teta1=zeros(size(teta));



for i=1:size(teta,1)
    for j=1:size(teta,2)
        if teta(i,j)+teta0(i,j)<pi/8 && teta(i,j)+teta0(i,j)>=0
            teta1(i,j)=1;
       
        end
    end
end

par90=edges.*(bwareaopen(teta1,5)+bwareaopen(imdilate(edge(temppp,'sobel','vertical'),[1;1;1;1]),20));
teta2=zeros(size(teta));
for i=1:size(teta,1)
    for j=1:size(teta,2)
        if teta(i,j)+teta0(i,j)>=pi/8 && teta(i,j)+teta0(i,j)<pi/4
            teta2(i,j)=1;
       
        end
    end
end

par45=edges.*bwareaopen(imdilate(medfilt2(teta2,[6,4]),strel('line',5,68),'same'),20);
teta3=zeros(size(teta));
for i=1:size(teta,1)
    for j=1:size(teta,2)
        if teta(i,j)+teta0(i,j)>=pi/4 && teta(i,j)+teta0(i,j)<3*pi/8
            teta3(i,j)=1;
       
        end
    end
end

par3=edges.*bwareaopen(imdilate(medfilt2(teta3,[5,5]),strel('line',5,45),'same'),20);
teta4=zeros(size(teta));
for i=1:size(teta,1)
    for j=1:size(teta,2)
        if teta(i,j)+teta0(i,j)>=3*pi/8 && teta(i,j)+teta0(i,j)<pi/2
            teta4(i,j)=1;
       
        end
    end
end

par4=edges.*bwareaopen(imdilate(medfilt2(teta4,[3,5]),strel('line',5,23),'same'),20);
teta5=zeros(size(teta));
for i=1:size(teta,1)
    for j=1:size(teta,2)
        if teta(i,j)+teta0(i,j)>=pi/2 && teta(i,j)+teta0(i,j)<5*pi/8
            teta5(i,j)=1;
       
        end
    end
end

par5=edges.*(imdilate(medfilt2(teta5,[3,20]),strel('line',4,0),'same'));

liness=bwareaopen(bwareaopen(par90,5)+par45+par3+par4+par5+bwareaopen(imdilate(edge(tempppsat,'sobel',0.1,'vertical'),[0 1 0]),5)+bwareaopen(imdilate(edge(tempppsat,'sobel',0.1,'horizontal'),[0;1;0]),5),15,8);

for i=2:3:a1-1
    for j=2:3:b1-1
        ssdd=[liness(i-1,j-1),liness(i-1,j),liness(i-1,j+1);liness(i,j-1),liness(i,j),liness(i,j+1);liness(i+1,j-1),liness(i+1,j),liness(i+1,j+1)];
        if (sum(sum(ssdd))>3)
            liness(i,j)=0;liness(i-1,j-1)=0;liness(i+1,j+1)=0;liness(i-1,j+1)=0;liness(i+1,j-1)=0;liness(i,j-1)=0;liness(i,j+1)=0;liness(i,j-1)=0;
        end
        
    end
    
end

for j=1:a1
    for h=b1-2:b1
        liness(j,h)=0;
    end
end

liness=bwareaopen(bwareaopen(liness,5),10);
liness=(liness-ttt).^2+liness+(liness-ttt2).^2+liness;
[~,thresh]=edge(temppp,'canny');
tempedge1=edge(temppp,'canny',0.8*thresh);
tempedge2=edge(temppp,'canny',1.6*thresh);
tempedge=(tempedge1+tempedge2)/2;

nse=sum(sum(tempedge-(tempedge.*liness)));
if nse <0
    disp('Warning this image is too complex or sparse in terms of straight edges');
    nse = 0;
end
        
ppp=sum(sum(liness));   
pix1 = a1*b1;
ppp = ppp/pix1;
nse = nse/pix1;    
edd = sum(sum(tempedge))/pix1;
EdgeStr = [EdgeStr; ppp];    
NSED = [NSED; nse];
ED = [ED; edd];

disp(names(k).name);
imname{k} = imnamee;

end

straightnonstraight=[EdgeStr NSED];
edgeDensities = table(imname', EdgeStr, NSED, ED, 'VariableNames',{'ImgName','SED','NSED','fullED'});

%warning('on',id);
end

