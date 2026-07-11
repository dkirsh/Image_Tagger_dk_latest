------------------------------
Natural Image Statistical Toolbox
------------------------------
Wilma A. Bainbridge & Aude Oliva
Created July 6, 2015

This is a collection of MATLAB scripts useful for controlling stimulus sets for psychophysics and neuroimaging studies, to ensure there are no low-level visual differences - specifically differences in spatial frequency, color and contrast, and retinal space taken by the stimulus. This is a growing work in progress. Also, keep in mind, we do not provide any troubleshooting or tutorials for these scripts, so use them at your own risk!

 
**Cite these two papers when using anything from this toolbox:**

Bainbridge, W. A. & Oliva, A. (in submission). Interaction envelope: Local spatial representations of objects at all scales in scene-selective regions.

Torralba A., & Oliva A. (2003). Statistics of natural image categories. Network 14, 391-412.

------------------------------
Contents:

Spatial Frequency Scripts

AverageAndPowerSpectrum.m
	A script that computes averages and the global power spectrum of an image set.
	
hammingfn.m
	A script that calculates the coefficients of a hamming window.
	
CalculateSpectraEnergy.m
	A script that calculates spatial frequency information in an image set.
	
CompareSpectraEnergy.m
	A script that compares spatial frequency between two image sets.
	
	
Color Scripts

CompareColorHistograms.m
	A script that compares and visualizes color distributions between two image sets.

Lab2RGB.m
	A script that converts Lab pixels to RGB pixels.

RGB2Lab.m
	A script that converts RGB pixels to Lab pixels.

	
Retinal Space Scripts

ProportionNonWhiteSpace.m
	A script that gets the proportion of foreground pixels from a white-background isolated object image set.

CompareNonWhiteSpace.m
	A script that compares the proportion of foreground pixels in two image sets.

	
Miscellaneous Useful Scripts

makesquare.m
	A script that makes a white-background image square, to be inputted into other scripts.

permutationtest.m
	A bootstrapping permutation statistical test to compare two vectors with the same number of samples, without prerequisites of a unimodal or normal distribution.