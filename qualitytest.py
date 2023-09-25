
from cv2 import CV_32F, Laplacian, GaussianBlur, cvtColor,  meanStdDev,COLOR_BGR2GRAY, Sobel, CV_64F, magnitude


class QualityTest:
        
    @staticmethod
    def local_contrast_laplace(frame, stride=2, blur = True):
        """
        Measure the amount of structure in a rectangular frame in both coordinate directions and
        return the minimum value. The discrete variance of the Laplacian is computed.

        :param frame: 2D image
        :param stride: Factor for down-sampling
        :return: Measure for amount of local structure in the image (scalar)
        """


        if blur:
            src = GaussianBlur(frame, (3, 3), 0)
        else:
            src= frame

        if len(frame.shape)>2 and frame.shape[2] > 1 : 
            src = cvtColor(src, COLOR_BGR2GRAY)
        return meanStdDev(Laplacian(src[::stride, ::stride], CV_32F))[1][0][0]
    

    @staticmethod
    def local_constrast_sobel(image):
            
            if len(image.shape)>2 and image.shape[2] > 1 : 
                gray = cvtColor(image, COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            # Calculer les dérivées horizontales et verticales avec Sobel
            gradient_x = Sobel(gray, CV_64F, 1, 0, ksize=3)
            gradient_y = Sobel(gray, CV_64F, 0, 1, ksize=3)
            # Calculer la magnitude du gradient
            gradient_magnitude = magnitude(gradient_x, gradient_y)
            # Calculer la netteté comme la moyenne de la magnitude du gradient
            sharpness = gradient_magnitude.mean()
            return sharpness

