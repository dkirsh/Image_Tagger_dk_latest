function img = makesquare(img)
% Wilma Bainbridge
% April 26, 2012
%
% Adds white space to an image to make it square. Only works for
% images with a white background (like isolated objects against a white
% background).

x = length(img(:,1,1));
y = length(img(1,:,1));

if x < y
    if (y-x)/2 == round((y-x)/2)
        adder = 0;
    else
        adder = 1;
    end
    padder1 = repmat(max(max(img)), (y-x)/2, y);
    padder2 = repmat(max(max(img)), (y-x)/2+adder, y);
    img = cat(1, padder1, img, padder2);
elseif y < x
    if (x-y)/2 == round((x-y)/2)
        adder = 0;
    else
        adder = 1;
    end
    padder1 = repmat(max(max(img)), x, floor((x-y)/2));
    padder2 = repmat(max(max(img)), x, floor((x-y)/2)+adder);
    img = cat(2, padder1, img, padder2);
end

end