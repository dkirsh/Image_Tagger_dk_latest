function [c] = hammingfn(n)
% Coefficients of a hamming window
% Script by Barabara Hidalgo-Sotelo
% see: http://octave.sourceforge.net/index/signal.html#Windowfunctions
% ref: A. V. Oppenheim & R. W. Schafer, "Discrete-Time Signal Processing".

if n==1
    c=1;
else
    n = n-1;
    c = 0.54 - 0.46 * cos (2 * pi * ([0:n])' / n);
end
