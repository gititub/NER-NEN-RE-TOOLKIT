import os
import shutil

dir1 = "./Auto-CORPus/output/"
dir2 = "./input/"


files = os.listdir(dir1)

for file in files:
    if file.endswith("_bioc.json"): #and os.path.getsize(os.path.join(dir1, file)) > 1024:
        shutil.copy(os.path.join(dir1, file), dir2)
        

