function [R,G,B]=Lab2RGB(L,a,b)
% Lab to RGB color space converter
%
% Please cite: Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.
%
% This function converts pixels from Lab space to RGB space (specifically,
% sRGB) via XYZ.  The inputs can be the L, a, and b values from a single
% pixel or an entire image.

[n,m]=size(L);

% matrix for sRGB -> XYZ conversion
kernelXYZn = [ 	0.412453 	0.35758 	0.180423;
	        0.212671	0.71516 	0.072169;	
	        0.019334 	0.119193 	0.950227];	

% CIE Standard Illuminant D65 (reference white point)
Xn=243.31;
Yn=256;
Zn=278.72;

% Convert Lab to XYZ
fy=(L+16)/116;
fx=(fy+a/500);
fz=(fy-b/200);

X=Xn.*invf(fx);
Y=Yn.*invf(fy);
Z=Zn.*invf(fz);       

%X=Xn.*(fx);
%Y=Yn.*(fy);
%Z=Zn.*(fz);       

% Convert XYZ to RGB
RGB=inv(kernelXYZn)*[X(:) Y(:) Z(:)]';

R=reshape(RGB(1,:),n,m);                    
G=reshape(RGB(2,:),n,m);                    
B=reshape(RGB(3,:),n,m);     

% Subfunction if:
function t=invf(y);
   t=(y.^3).*(y>=0.2069)+((y-16/116)/7.787).*(y<0.2069);

