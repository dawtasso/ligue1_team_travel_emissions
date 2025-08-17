import shutil
import pandas as pd
import subprocess

passengers="50"

#Run train destination before
source_path = '../Train calculation/localisation_stade.csv'
destination_path = 'localisation_stade.csv'
shutil.copy(source_path, destination_path)

API_KEY='AIzaSyDIf4jaKso1v7WmOVfUyZCLBVYmcOJnuH4'


subprocess.run(["python", "Get-airports.py", API_KEY])
subprocess.run(["python", "Get-distance-fuel.py",API_KEY,passengers])
subprocess.run(["python", "Final.py"])

