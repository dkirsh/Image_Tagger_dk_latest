function [L,a,b]=RGB2Lab(R,G,B)
% RGB to Lab color space converter
%
% Please cite: Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.
%
% This function converts pixels from RGB space (specifically, sRGB) to Lab
% space via XYZ.  The inputs can be the R, G, and B values from a single
% pixel or an entire image.

[n,m]=size(R);

% matrix for sRGB -> XYZ conversion
kernelXYZn = [0.412453 	0.35758   0.180423;
	         0.212671	0.71516   0.072169;	
	         0.019334 	0.119193  0.950227];	

% CIE Standard Illuminant D65 (reference white point)
Xn=243.31;
Yn=256;
Zn=278.72;

% Convert RGB to XYZ
XYZn = kernelXYZn * [R(:) G(:) B(:)]';	
		
X=reshape(XYZn(1,:),n,m);                    
Y=reshape(XYZn(2,:),n,m);                    
Z=reshape(XYZn(3,:),n,m);     

% Convert XYZ to Lab
L = 116*f(Y/Yn)-16; 
a = 500*(f(X/Xn)-f(Y/Yn));
b = 200*(f(Y/Yn)-f(Z/Zn));

% Subfunction f:
function y=f(t);
   y=(t.^(1/3)).*(t>=0.008856)+(7.787*t+16/116).*(t<0.008856);
