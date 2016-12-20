import arcpy
import os
import datetime
import shutil
from arcpy.sa import *

#select the folder that holds the daymet files
gridDir = arcpy.GetParameterAsText(0)
asciiDir = arcpy.GetParameterAsText(1)
deleteGrids = arcpy.GetParameterAsText(2)

#iterate folders to get to rasters
for year in os.listdir(gridDir):
    yearPath = os.path.join(gridDir,year)    
    for variable in os.listdir(yearPath):
        arcpy.AddMessage('Converting rasters variable: %s, year: %s' %(variable, year))
        
        #make folders for ascii files if they don't exist
        asciiSub = os.path.join(asciiDir,variable)
        if not os.path.isdir(asciiSub):
            os.makedirs(asciiSub)
        
        varPath = os.path.join(yearPath, variable)
        arcpy.env.workspace = varPath
        
        rasters = arcpy.ListRasters("*")
#List and begin processing the rasters in the folder 
        for ras in rasters:
            rasSplit = ras.split("_")
            v = rasSplit[0]
            dtyear = int(rasSplit[1])
            dtday = int(rasSplit[2])
            dtdate = datetime.datetime(dtyear,1,1)+datetime.timedelta(dtday-1)
            if v == 'pr':
                asciiName = 'prcp_%s.asc'%dtdate.strftime('%Y_%m_%d').upper()
                convertRas = Raster(ras) * 0.0393701
                asciiRas = arcpy.RasterToASCII_conversion(convertRas,os.path.join(asciiSub,asciiName))
            elif v == 'tx':
                asciiName = 'tmax_%s.asc'%dtdate.strftime('%Y_%m_%d')
                convertRas = Raster(ras)*9/5+32
                asciiRas = arcpy.RasterToASCII_conversion(convertRas,os.path.join(asciiSub,asciiName))
            elif v == 'tn':
                asciiName = 'tmin_%s.asc'%dtdate.strftime('%Y_%m_%d')
                convertRas = Raster(ras)*9/5+32
                asciiRas = arcpy.RasterToASCII_conversion(convertRas,os.path.join(asciiSub,asciiName))
            else: 
                arcpy.AddMessage("must be a bad name er sumthin...")
                
#rename prcp files with with CAPS 
curDir = os.path.join(asciiDir,'pr')
os.chdir(curDir)
for asc in os.listdir(curDir):
    capsName = asc[:5].upper()+asc[5:]
    os.rename(asc,capsName)
    
#if deleteGrids is checked, delete all of the rasters used to create the ascii
if deleteGrids == 'true':
    arcpy.AddMessage("Deleting Raster Files")
    for year in os.listdir(gridDir):
        shutil.rmtree(os.path.join(gridDir,year),ignore_errors=True)