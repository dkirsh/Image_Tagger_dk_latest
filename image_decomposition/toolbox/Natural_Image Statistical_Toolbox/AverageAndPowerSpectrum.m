function [averageImage, averageFFT] = AverageAndPowerSpectrum(maskedRgbImage)

% Compute averages of the image set and the global power spectrum of the
% images in the set as well as slopes
%
%   By: Aude Oliva
%   Email: oliva@mit.edu, torralba@ai.mit.edu
%   Citation: Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.
%
%   Usage:
%       [averageImage, averageFFT] = AverageAndPowerSpectrum('images/');
%
%   averageImage = an overlaid average of all the images in the folder
%   averageFFT = the power spectrum average of all the images in the folder

%files = [dir([folder '*.jpg']); dir([folder '*.tif']); dir([folder '*.png']); dir([folder '*.bmp'])];
%Nimages = length(files);
%files = folder;
%Nimages = 1;

% Window to remove boundary artifatcs
g=hammingfn(256)*hammingfn(256)';

averageImage = 0;
averageFFT = 0;

% Loop: read images and compute averages
%for i = 1:Nimages
    % real image
    img = maskedRgbImage; %imread([folder files(i).name]);
    [m,n,c] = size(img); if c == 1; img = repmat(img,[1 1 3]); end
    
    %img = makesquare(img);
    img = imresize(img, [150 150]); % normalize images here
    % image(img); drawnow
    
    % Compute FFT and power spectrum
    img = double(img);
    imgBW = mean(img, 3); % put image in gray levels
    imgBW = imgBW-mean(imgBW(:)); % remove mean
    fftImg=abs(fft2(imgBW.*g)).^2; % compute power spectrum
    fftImg=fftImg/sum(fftImg(:)); % normalize to unit power
    
    %   averageImage = averageImage + imgBW; % B&W image average
    averageImage = averageImage+img; % image average
    averageFFT=averageFFT+fftImg;    % power spectrum average    
%end

%averageImage = averageImage/Nimages;
%averageFFT = averageFFT/Nimages;
averageFFT = fftshift(averageFFT); % put frequency (0,0) in the center
end

% % PLOTS:
% figure
% averageImage = averageImage-min(averageImage(:)); averageImage = averageImage/max(averageImage(:));
% image(averageImage); title([folder ': image average'])
% 
% figure
% surf(log(averageFFT)); shading interp; colormap(gray(256)); axis('tight')
% xlabel('f_x'); ylabel('f_y'); zlabel('log'); %view(0,90)
% title([folder ': power spectrum average'])
% 
% % Plot sections:
% [thresholds, ndx] = sort(-averageFFT(:)); thresholds= -thresholds;
% energySections = cumsum(thresholds);
% [foo, ndx90] = min(abs(energySections - .9)); th90 = thresholds(ndx90);
% [foo, ndx80] = min(abs(energySections - .8)); th80 = thresholds(ndx80);
% [foo, ndx60] = min(abs(energySections - .6)); th60 = thresholds(ndx60);
% 
% figure
% [c,h] = contour(-128:127, -128:127, averageFFT,[th90 th80 th60]); % Here I assume that images are 256x256
% xlabel('f_x (cycles per image)');ylabel('f_y (cycles per image)');
% title([folder ': Sections that account for 60, 80 and 90 % of the image energy'])
% grid on
% axis('square');
% drawnow

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % Slopes:
% % Parameters:
% fb=[0.01 0.45]; % interval of frequencies (in cycles per pixel => max value = .5)
% Nangles = 4;    % Number of angles
% 
% th=linspace(0, pi, Nangles+1); th = th(1:end-1);
% n=256;  % Here I assume that images are 256x256
% 
% [fx,fy] = meshgrid(0:n-1,0:n-1);fx=fx-n/2;fy=fy-n/2;
% 
% f=logspace(log10(fb(1)), log10(fb(2)), 20); % select 20 points along a radial axis
% lf=log10(f);
% theta=pi/2-th;
% 
% theta = th;
% figure
% subplot(121)
% col='rgbcmkyrgbcmkyrgbcmkyrgbcmky';
% clear h slope prefactor
% % Loop on angles:
% for kk=1:length(theta)
%     % extract a radial section of the power spectrum
%     t=theta(kk); fxi=-f*sin(t)*n; fyi=f*cos(t)*n;
%     p=interp2(fx,fy,averageFFT,fxi,fyi,'linear');
%     
%     % Fit the model spectrum = prefactor * f^slope
%     lp=log10(p);
%     pol=polyfit(lf,lp,1); % FITTING WITH A LINE
%     slope(kk)=pol(1); % this is the slope
%     prefactor(kk)=exp(pol(2)); % this is the prefactor
%     
%     % Plot
%     plot(lf, lp, col(kk), 'linewidth', 3)
%     axis('tight')
%     hold on
%     h(kk) = plot(lf, lf*pol(1)+pol(2), [col(kk) '-o']);
%     grid on
% end
% xlabel('frequency (cycles per pixel in log units)')
% ylabel('power spectrum (radial section)')
% legend(h, num2str(theta'/pi*180));
% title([folder ': The angles read as: f_y = 0, f_x = 90'])
% 
% subplot(122)
% plot(theta/pi*180, slope, 's-')
% text (theta/pi*180, slope, num2str(-slope'))
% xlabel('Angle (The angles read as: f_y = 0, f_x = 90)')
% ylabel('slope')
% title([folder ': spectrum = prefactor * f^{ slope}'])


