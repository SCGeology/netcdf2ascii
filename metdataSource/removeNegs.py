#\\dnrnas\lwcdusr\Common\SWB\ASCII\

#iterate through raster list and do conversion if the min val < 0; put in new folder
import arcpy
from arcpy.sa import *
import os

ws = arcpy.GetParameterAsText(0)
arcpy.env.workspace = ws

convASC = os.path.join(ws,"new")

if not os.path.exists(convASC):
    os.makedirs(convASC)

arcpy.AddMessage("made new folder")

rasters = arcpy.ListRasters()

for r in rasters:
    #it might just be faster to do conditional statement and save on all, and do it in the first script. 
    arcpy.CalculateStatistics_management(ws+"/"+r,"#","#","#","SKIP_EXISTING")
    ras = Raster(r)
    minVal = ras.minimum
    if minVal < 0:
        arcpy.AddMessage(r + " has negative values. Removing negative values now.")
        ras = Con((ras < 0),0,ras)        
        arcpy.AddMessage(r + ": changing min value from " +str(minVal)+ " to 0")
    else:
        arcpy.AddMessage(r + " does not have negative values.")
    #deal with null values
    outIsNull = IsNull(ras)
    outConRas = Con(outIsNull,0,ras,"VALUE = 1")        
        
    arcpy.RasterToASCII_conversion(outConRas,os.path.join(convASC,r))                   
        
#for renaming with caps
curDir = convASC
os.chdir(curDir)
for asc in os.listdir(curDir):
    capsName = asc[:5].upper()+asc[5:]
    os.rename(asc,capsName)
