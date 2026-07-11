function [ pixV ] = Count_Colors_variableDupIMS(maskedRgbImage, ctrs ,thRGB, thS) 

I = maskedRgbImage;
    [s1, s2, s3] = size(I);
    %thR = 0.15; 
    %thG = 0.15;
    %thB = 0.15;
    
    if s3 == 3
        J = rgb2hsv(I);
        maskW = zeros(size(J));
        maskY = zeros(size(J));
        maskC = zeros(size(J));
        maskM = zeros(size(J));
        maskR = zeros(size(J));
        maskG = zeros(size(J));
        maskB = zeros(size(J));
        for j = 1:size(J,1)
            for k = 1:size(J,2)
                if abs(J(j,k,1)) < thRGB(1) || abs(J(j,k,1) - 1) < thRGB(1)
                    maskR(j,k,1:3) = 1;
                end
                if abs(J(j,k,1) - ctrs(1)) < thRGB(2)
                    maskY(j,k,1:3) = 1;
                end
                if abs(J(j,k,1) - ctrs(2)) < thRGB(3)
                    maskG(j,k,1:3) = 1;
                end
                if abs(J(j,k,1) - ctrs(3)) < thRGB(4)
                    maskC(j,k,1:3) = 1;
                end
                if abs(J(j,k,1) - ctrs(4)) < thRGB(5)
                    maskB(j,k,1:3) = 1;
                end
                if abs(J(j,k,1) - ctrs(5)) < thRGB(6)
                    maskM(j,k,1:3) = 1;
                end
                if J(j,k,2) < thS
                    maskR(j,k,1:3) = 0;
                    maskG(j,k,1:3) = 0;
                    maskB(j,k,1:3) = 0;
                    maskY(j,k,1:3) = 0;
                    maskC(j,k,1:3) = 0;
                    maskM(j,k,1:3) = 0;
                    maskW(j,k,1:3) = 1;
                end
            end
        end
        pixR = length(find(maskR(:,:,1)))/(s1*s2);
        pixG = length(find(maskG(:,:,1)))/(s1*s2);
        pixB = length(find(maskB(:,:,1)))/(s1*s2);
        pixY = length(find(maskY(:,:,1)))/(s1*s2);
        pixC = length(find(maskC(:,:,1)))/(s1*s2);
        pixM = length(find(maskM(:,:,1)))/(s1*s2);
        pixW = length(find(maskW(:,:,1)))/(s1*s2);
        IR = uint8(maskR).*I;
        IG = uint8(maskG).*I;
        IB = uint8(maskB).*I;
        IY = uint8(maskY).*I;
        IC = uint8(maskC).*I;
        IM = uint8(maskM).*I;
        IW = uint8(maskW).*I;
%         subplot('position',[0.01 0.5 0.25 0.45])
%         hold on
%         imshow(I)
%         set(gca,'Visible','off')
%         subplot('position',[0.26 0.5 0.25 0.45])
%         hold on
%         imshow(IR)
%         set(gca,'Visible','off')
%         subplot('position',[0.51 0.5 0.25 0.45])
%         hold on
%         imshow(IG)
%         set(gca,'Visible','off')
%         subplot('position',[0.76 0.5 0.25 0.45])
%         hold on
%         imshow(IB)
%         set(gca,'Visible','off')
%         subplot('position',[0.01 0.02 0.25 0.45])
%         hold on
%         imshow(IW)
%         set(gca,'Visible','off')
%         subplot('position',[0.26 0.02 0.25 0.45])
%         hold on
%         imshow(IM)
%         set(gca,'Visible','off')
%         subplot('position',[0.51 0.02 0.25 0.45])
%         hold on
%         imshow(IY)
%         set(gca,'Visible','off')
%         subplot('position',[0.76 0.02 0.25 0.45])
%         hold on
%         imshow(IC)
%         set(gca,'Visible','off')
        
        pixV = [pixR pixY pixG pixC pixB pixM pixW];
        pause(2)
        clf
    end

%pixT = table(imname', pixV(:,1), pixV(:,2), pixV(:,3), pixV(:,4), pixV(:,5), pixV(:,6), pixV(:,7), 'VariableNames',{'ImgName','Rpix','Ypix','Gpix','Cpix','Bpix','Mpix','Wpix'});
