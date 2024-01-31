from ctypes import *
import numpy as np

mylib = CDLL("./libLepton.so")
mylib.Lepton_new.restype = POINTER(c_int)
lepton = mylib.Lepton_new()
width = mylib.Lepton_get_width(lepton)
height = mylib.Lepton_get_height(lepton)

image_ctype = mylib.Lepton_get_image(lepton)
image_np = np.ctypeslib.as_array(image_ctype, shape=(height, width, 3))
