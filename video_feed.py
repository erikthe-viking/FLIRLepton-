import wx
from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps
import numpy
import cv2
from pylepton import Lepton
from skimage.util.shape import view_as_blocks

# Created by Erik Kirkegaard 
# For use with the FLIR Lepton Module on Raspberry Pi
# Requires pylepton library

SIZE = (640, 480)

class Analyzer():

    def __init__(self):
      self.im = Image.new('RGB', (80,60))
      self.matrix =  numpy.zeros(shape=(80,60))
      self.threshold = 9.5978
      self.sum_list = []
      self.thresh_list = []
      self.average_list = []
      self.average = 0.0
      self.counter = 0
    def get_image(self):
 
         with Lepton() as l:
           test,_ = l.capture()
         self.im = Image.frombytes('L', (test.shape[1],test.shape[0]), test.astype('b').tostring())
         self.matrix = test # assigns the class numpy matrix the current frame
         self.im = self.im.resize((560,420))
         self.analyze(test)
         self.smoothed = self.im.filter(ImageFilter.SMOOTH)
         self.blurred = self.smoothed.filter(ImageFilter.BLUR)
         
         if (self.threshold-self.average) >  1 and (self.threshold-self.average) < 2.5: # Human Detection
               self.color = self.blurred.filter(ImageFilter.FIND_EDGES) 
            #   self.color = ImageOps.colorize(self.edge,'#800000',(248,248,255))
        
         elif self.threshold >=  2.5:  # Super hot detection
               self.color = ImageOps.colorize(self.blurred,'#800000',(248,248,255))  
         else:
               self.color = self.blurred
	 
	 self.counter = self.counter + 1
         
         return self.color
      

    def analyze(self,input_val):        
         x = image = numpy.array(input_val)
         y  = view_as_blocks(x, block_shape=(3,4,1)).squeeze()
 
         del self.sum_list[:]
         del self.thresh_list [:]
         
         for i in range(0,19):
            sum_val = numpy.sum(y[i][0])
            self.sum_list.append(sum_val)

         for i in range(0,19):
            test = float(self.sum_list[i]) / 10000
            self.thresh_list.append(test)
         self.threshold = 0
         for i in range(0,19):
            if self.thresh_list[i] > self.threshold:
              self.threshold = self.thresh_list[i]

	 if self.counter < 200:
		x = self.threshold
		self.average_list.append(x)
	 if self.counter == 200:
		self.average = sum(self.averae_list) / len(self.average_list)
         
         print self.threshold

def pil_to_wx(image):
    width, height = image.size
    buffer = image.convert('RGB').tostring()
    bitmap = wx.BitmapFromBuffer(width, height, buffer)
    return bitmap

class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent, -1)
        self.SetSize(SIZE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.update()
        self.XYZ = Analyzer()
    def update(self):
        self.Refresh()
        self.Update()
        wx.CallLater(15, self.update)
    def create_bitmap(self):
        image = self.XYZ.get_image()
        bitmap = pil_to_wx(image)
        return bitmap
    def on_paint(self, event):
        bitmap = self.create_bitmap()
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(bitmap, 0, 0)

class Frame(wx.Frame):
    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX
        super(Frame, self).__init__(None, -1, 'Camera Viewer', style=style)
        panel = Panel(self)
        self.Fit()

def main():
    app = wx.PySimpleApp()
    image = Frame()
    image.Center()
    image.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
