import arcpy
import os

#select the folder that holds the daymet files
daymetDir = arcpy.GetParameterAsText(0)

#Set the parent directory - this is the 'root' folder
parentDir = arcpy.GetParameterAsText(1)

#get the variables you want in dropdown list
variableInputs = arcpy.GetParameterAsText(2)

#Clip polygon
clipper = arcpy.GetParameterAsText(3)

#can specify the band range
bands = arcpy.GetParameterAsText(4)

#want to use snap env?
snapEnv = arcpy.GetParameterAsText(5)

#choose snap raster and cell size environments
snapRas = arcpy.GetParameterAsText(6)

#kill script function
def die():  
    from sys import exit
    exit()

if bands != 'ALL':
    begBand = int(bands.split('-')[0].strip())-1
    endBand = int(bands.split('-')[1].strip())
    if endBand < begBand or endBand > 366 or begBand < 0:
        arcpy.AddError("Range of raster bands is incorrect.")
        die()
    arcpy.AddMessage("Band Index %s to %s" %(begBand+1, endBand))
else:
    arcpy.AddMessage("All Bands")
       
        
if snapEnv == "true":
         
    #Get cell size, set environments 
    cellx = arcpy.GetRasterProperties_management(snapRas,"CELLSIZEX")
    celly = arcpy.GetRasterProperties_management(snapRas,"CELLSIZEY")
    arcpy.AddMessage("Resample cell size X,Y: %s, %s" %(cellx,celly))
    
else:
    
    #set to default values
    cellx = "#"
    celly = "#"
    arcpy.AddMessage("Not using snap/cell size environments. Cell size will remain the same as input")   
        
        
#split the variables, add to variables list
variables = []
for v in variableInputs.split(';'):
    variables.append(v)

leapYears = [1980,1984,1988,1992,1996,2000,2004,2008,2012,2016]    
    
#iterate variables, run netCDF tool, save to rasters
for v in variables:
    for i in os.listdir(daymetDir):
        if i.startswith(v):
            daymetFile = os.path.join(daymetDir,i)
    
            if daymetFile[-3:] == 'nc4':
                year = daymetFile[-8:-4]
            else:
                year = daymetFile[-7:-3]

            #create directory for the year (if it doesn't exist)
            yearPath = os.path.join(parentDir,year)
            if not os.path.exists(yearPath):
                os.makedirs(yearPath)
                yearDir = yearPath
            else:
                yearDir = yearPath

            #make a directory for variable and ascii files (if it doesn't exist)
            varPath = os.path.join(yearDir,v)
            if not os.path.exists(varPath):
                os.makedirs(varPath)
                varDir = varPath
            else:
                varDir = varPath
                
            if v == 'pr':
                vt = 'precipitation_amount'
            else:
                vt = 'air_temperature'

            #make net CDF Layer
            netCDF = arcpy.MakeNetCDFRasterLayer_md(daymetFile, vt, "lon","lat", v+"Layer","day")

            #extract all the bands of netCDF to raster layers, copy those layers to raster datasets
            if bands == 'ALL':
                begBand = 0
                if int(year) in leapYears:
                    endBand = 366
                    arcpy.AddMessage(year + " is leap year.")
                else:
                    endBand = 365 
            
            for band in range (begBand,endBand):
                
                if v == 'tmmx':
                    var = 'tx'
                elif v == 'tmmn':
                    var = 'tn'
                else:
                    var = v
                
                julianDay = str(band+1)

                if snapEnv == "true":
                    varRasPath = varDir + "/" + var + "_" + year + "_" + julianDay + "c"
                else:
                    varRasPath = varDir + "/" + var + "_" + year + "_" + julianDay
                    
                rasLayer = arcpy.MakeRasterLayer_management(netCDF, str(netCDF)+julianDay,"#","#",julianDay)
                    
                arcpy.env.outputCoordinateSystem = clipper
                
                newRas = arcpy.Clip_management(rasLayer,"#",varRasPath,clipper,"#","NONE")
                
                if int(julianDay) % 10 == 0:
                    arcpy.AddMessage("Day: " + julianDay + " of year: " + year + " for variable: " + v + ".")
                
                #if the snapEnv setting is true, then resample the rasters and save final raster
                if snapEnv == "true":
                    arcpy.env.snapRaster = snapRas    
                    resRas = varDir + "/" + var + "_" + year + "_" + julianDay + "r"
                    arcpy.Resample_management(newRas,resRas,cellx,"NEAREST")
                    finRas = arcpy.sa.ExtractByMask(resRas,snapRas)
                    finalRas = varDir + "/" + var + "_" + year + "_" + julianDay
                    finRas.save(finalRas)
                    #delete the rasters that are not resampled. 
                    arcpy.Delete_management(newRas)
                    arcpy.Delete_management(resRas)
                #if false, just save the final raster based on the split and clip    

                
