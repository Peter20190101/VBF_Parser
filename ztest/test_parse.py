import sys
import os
from time import sleep, time
from math import ceil
from io import BytesIO
import can

from ford.vbf import Vbf

vbf_path = 'E:\Github\MyGit\VBF_Parser\ztest/vbf\g.vbf'
print(vbf_path)
data = Vbf(vbf_path)
print("end")
