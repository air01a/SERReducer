import types

from numpy import uint8, uint16,frombuffer,reshape, float32
from cv2 import cvtColor,COLOR_BAYER_BG2BGR,COLOR_BGR2GRAY,COLOR_BayerBG2BGR, COLOR_BayerGB2BGR,COLOR_BayerGR2BGR,COLOR_BayerRG2BGR, COLOR_RGB2BGR #imshow, waitKey

import struct
class SerManager:
    def __init__(self,fname):
        self.fname=fname
        self.header=types.SimpleNamespace()
        self.f = open(self.fname,"rb")
        self.header.fileID=self.f.read(14).decode()
        self.header.luID=int.from_bytes(self.f.read(4), byteorder='little')
        self.header.colorID=int.from_bytes(self.f.read(4), byteorder='little')
        """
        Content:
            MONO= 0
            BAYER_RGGB= 8
            BAYER_GRBG= 9
            BAYER_GBRG= 10
            BAYER_BGGR= 11
            BAYER_CYYM= 16
            BAYER_YCMY= 17
            BAYER_YMCY= 18
            BAYER_MYYC= 19
            RGB= 100
            BGR= 101
        """
        if self.header.colorID <99:
            self.header.numPlanes = 1
        else:
            self.header.numPlanes = 3
            
        self.header.littleEndian=int.from_bytes(self.f.read(4), byteorder='little')
        self.header.imageWidth=int.from_bytes(self.f.read(4), byteorder='little')
        self.header.imageHeight=int.from_bytes(self.f.read(4), byteorder='little')
        self.header.PixelDepthPerPlane=int.from_bytes(self.f.read(4), byteorder='little')
        self.header.BitUsed = self.header.PixelDepthPerPlane

        if self.header.PixelDepthPerPlane>8:
            self.header.PixelDepthPerPlane=16


        if self.header.PixelDepthPerPlane == 8:
            self.dtype = uint8
        elif self.header.PixelDepthPerPlane == 16:
            self.dtype = uint16
        self.header.frameCount=int.from_bytes(self.f.read(4), byteorder='little')
        self.header.observer=self.f.read(40).decode()
        self.header.instrument=self.f.read(40).decode()
        self.header.telescope=self.f.read(40).decode()
        self.header.dateTime=int.from_bytes(self.f.read(8), byteorder='little')
        self.imgSizeBytes = int(self.header.imageHeight*self.header.imageWidth*self.header.PixelDepthPerPlane*self.header.numPlanes/8)
        self.imgNum=0
        

    def close(self):
        self.f.close()

    def realign(self):
        ptr = int(178+self.imgNum*(self.imgSizeBytes))
        self.f.seek(ptr) 

    def get_cv2_convertor(self, color):
        if color==8:
            return COLOR_BayerBG2BGR#COLOR_BAYER_BG2BGR
        elif color==9:
            return COLOR_BayerGB2BGR
        elif color==10:
            return COLOR_BayerGR2BGR
        elif color==11:
            return COLOR_BayerRG2BGR
        elif color==101:
            return COLOR_RGB2BGR
        return None 
        
    def reset_ptr(self):
        self.imgNum=0
        self.f.seek(178)

    def get_img(self,imgNum=None):
        if imgNum is None:
            pass
        else:
            self.imgNum=imgNum
            self.f.seek(int(178+self.imgNum*(self.imgSizeBytes)))

            
        frame = frombuffer(self.f.read(self.imgSizeBytes),dtype=self.dtype)
            

        self.imgNum+=1
        
        frame = reshape(frame,(self.header.imageHeight,self.header.imageWidth,self.header.numPlanes))
        if self.header.BitUsed != self.header.PixelDepthPerPlane:
            frame = (frame* (2 ** self.header.PixelDepthPerPlane)  / (2** self.header.BitUsed)).astype(self.dtype)
        
        if self.header.colorID>1:
             COLOR_CONVERTER=self.get_cv2_convertor(self.header.colorID)
             frame=cvtColor(frame, COLOR_CONVERTER)
        

        frame = (frame - frame.min())/(frame.max()-frame.min())
        frame = (frame/frame.max()).astype(float32)
        return frame
    
    def int_to_little_indian(self, i):
        return struct.pack('<I', i)
    
    def reduce_ser_file(self, output, frames_to_keep):
        # Read  header
        self.f.seek(0)
        header1 = self.f.read(38)
        self.f.read(4)  #Read framecount that will change according to len(frames_to_keep)
        header2 = self.f.read(136)
        trailer=[]
        frames_to_keep.sort()
        with open(output,'wb') as f_out:
            f_out.write(header1)
            f_out.write(self.int_to_little_indian(len(frames_to_keep)))
            f_out.write(header2)

            for i in frames_to_keep:
                ptr = int(178+i*(self.imgSizeBytes))
                self.f.seek(ptr)
                img = self.f.read(self.imgSizeBytes)
                self.f.seek(self.header.frameCount*self.imgSizeBytes+178+4*i)
                tmp = self.f.read(4)
                trailer.append(tmp)
                f_out.write(img)
            for data in trailer:
                f_out.write(data)
        
        self.realign()

if __name__ == "__main__":
    import time

    import cv2
    ser = SerManager('E:/sharpcap/2024-08-25/Sun/08_49_30.ser')

    print(ser.header)
    for i in range(ser.header.frameCount%100):
        frame = cv2.resize(ser.get_img(i),(800,600))
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)  # Nécessaire pour rafraîchir la fenêtre

        if cv2.getWindowProperty('Frame', cv2.WND_PROP_VISIBLE) < 1:
            break
    frame_keep = [i for i in range(200,800)]
    ser.reduce_ser_file('test.ser',frame_keep)
    cv2.destroyAllWindows()


