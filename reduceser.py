from qualitytest import QualityTest
from imagemanager import SerManager
from os import listdir, remove
from os.path import splitext, isfile, isdir, getsize
from threading import Thread
from numpy import empty, append as np_append, flip as np_flip

class ReduceSer:

    def __init__(self, directory, suffix, subdir, tokeep,percentage, delete, callback,log):
        self.directory = directory
        self.subdir = subdir
        self.tokeep = tokeep
        self.suffix = suffix
        self.percentage = percentage
        self.delete = delete
        self.running = False
        self.callback = callback
        self.writelog = log

    def start(self):
        self.running = True
        self.writelog("++++++++ Start",colors='white on green')
        self.thread = Thread(target=self.runner, daemon=True)
        self.thread.start()


    def _reduce_ser(self, path):
        output = splitext(path)[0]+self.suffix+'.ser'

        if isfile(output):
            self.writelog("  -- Reduced file exists, skipping", colors="white on black")
            return
        
        if self.suffix in path:
            self.writelog("  -- File already reduced", colors="white on black")
            return

        size = getsize(path)  / (1024 ** 3)
        try:
            ser = SerManager(path)
        except:
            self.writelog("   error reading SER File", colors='white on red')
            return
        
        result = empty(1)
        for i in range(ser.header.frameCount):
            try:
                laplacien = QualityTest.local_contrast_laplace(ser.get_img(i))
            except:
                self.writelog("   Error reading frames", colors='white on red')
                return
            
            result=np_append(result,laplacien)
            if not self.running:
                return

        index = np_flip(result.argsort())

        if self.percentage:
            tokeep = int(self.tokeep * ser.header.frameCount)
        else:
            tokeep = self.tokeep
        
        if tokeep<100:
            self.writelog("   Error, frame < 100", colors='white on red')
        else:
            try:
                ser.reduce_ser_file(output,index[0:tokeep])
            except:
                self.writelog("   Error writing new ser", colors='white on red')
                return
            
            newsize =getsize(output)/ (1024 ** 3)
            gain = 100-int(newsize/size *100)
            self.writelog("%s reduce to %i frames(initial : %i), gain %i %%" % (path, tokeep,ser.header.frameCount, gain), colors="white on green")
            if self.delete:
                try:
                    remove(path)
                    self.writelog("  - Original file removed")
                except:
                    self.writelog(" Error removing original file", colors = "white on red")

    def runner(self,dir=None):
        if not self.running:
            return
        
        _main = False
        if dir==None:
            _main = True
            dir = self.directory
        self.writelog('** DIRECTORY : %s' % dir,colors='white on blue')
        
        self.writelog('')
        for file in listdir(dir):
            file_path = dir + '/' + file
            if isdir(file_path) and self.subdir:
                self.runner(dir + '/'+ file)
            if isfile(file_path) and splitext(file_path)[1]=='.ser':
                self.writelog("Working on %s" % file_path)
                self._reduce_ser(file_path)

        if _main:
            self.callback("+FINISHED+")
            self.writelog("FINISHED", colors="white on green")
        

    def stop(self):
        self.running = False

