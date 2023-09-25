import types

from numpy import uint8, uint16,frombuffer,reshape

import struct

class SerManager:
    def __init__(self,fname):
        self.fname=fname
        self.header=types.SimpleNamespace()
        with open(self.fname,"rb") as f:
            self.header.fileID=f.read(14).decode()
            self.header.luID=int.from_bytes(f.read(4), byteorder='little')
            self.header.colorID=int.from_bytes(f.read(4), byteorder='little')
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
                
            self.header.littleEndian=int.from_bytes(f.read(4), byteorder='little')
            self.header.imageWidth=int.from_bytes(f.read(4), byteorder='little')
            self.header.imageHeight=int.from_bytes(f.read(4), byteorder='little')
            self.header.PixelDepthPerPlane=int.from_bytes(f.read(4), byteorder='little')
            self.header.BitUsed = self.header.PixelDepthPerPlane

            if self.header.PixelDepthPerPlane>8:
                self.header.PixelDepthPerPlane=16


            if self.header.PixelDepthPerPlane == 8:
                self.dtype = uint8
            elif self.header.PixelDepthPerPlane == 16:
                self.dtype = uint16
            self.header.frameCount=int.from_bytes(f.read(4), byteorder='little')
            self.header.observer=f.read(40).decode()
            self.header.instrument=f.read(40).decode()
            self.header.telescope=f.read(40).decode()
            self.header.dateTime=int.from_bytes(f.read(8), byteorder='little')
            self.imgSizeBytes = int(self.header.imageHeight*self.header.imageWidth*self.header.PixelDepthPerPlane*self.header.numPlanes/8)
            self.imgNum=0
        
    def get_img(self,imgNum=None):
        if imgNum is None:
            pass
        else:
            self.imgNum=imgNum
            
        with open(self.fname,"rb") as f:
            f.seek(int(178+self.imgNum*(self.imgSizeBytes)))
            frame = frombuffer(f.read(self.imgSizeBytes),dtype=self.dtype)
            
        self.imgNum+=1
        
        frame = reshape(frame,(self.header.imageHeight,self.header.imageWidth,self.header.numPlanes))
        if self.header.BitUsed != self.header.PixelDepthPerPlane:
            frame = (frame* (2 ** self.header.PixelDepthPerPlane)  / (2** self.header.BitUsed)).astype(self.dtype)
        
        return frame
    
    def int_to_little_indian(self, i):
        return struct.pack('<I', i)
    
    def reduce_ser_file(self, output, frames_to_keep):
        with open(self.fname,"rb") as f:
            # Read  header
            header1 = f.read(38)
            f.read(4)  #Read framecount that will change according to len(frames_to_keep)
            header2 = f.read(136)

            with open(output,'wb') as f_out:
                f_out.write(header1)
                f_out.write(self.int_to_little_indian(len(frames_to_keep)))
                f_out.write(header2)

                for i in frames_to_keep:
                    f.seek(int(178+i*(self.imgSizeBytes)))
                    img = f.read(self.imgSizeBytes)
                    f_out.write(img)


 