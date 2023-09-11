
from cv2 import CV_32F, Laplacian, GaussianBlur, cvtColor,  meanStdDev,COLOR_BGR2GRAY


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


        if len(frame.shape)>2 and frame.shape[2] > 1 : 
            src = cvtColor(src, COLOR_BGR2GRAY)
        return meanStdDev(Laplacian(src[::stride, ::stride], CV_32F))[1][0][0]
    


