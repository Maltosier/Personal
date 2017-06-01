import arcpy, os, errno


# ------------------------- SCRIPT  INFORMATION START ------------------------ #

# This script was created by Mursheed Drahman on YYYY-MM-DD

# It was created for use in Constraints Analyses for CanACRE Ltd.

# The purpose of this script is to automate a majority of the output process,
# when given the locations of all necessary constraints layers.

# All inquiries for this script can be directed to mdrahman@canacre.com
# where I can assist to the best of my ability 

# ------------------------- SCRIPT  INFORMATION  END ------------------------- #

# ============================================================================ #
# ========================== CUSTOMIZE SCRIPT HERE =========================== #
# ============== LOCATE DATA AND CHANGE OUTPUT LOCATION AND NAME ============= #

# ----------------------------- CONSTANTS START ------------------------------ #
# VARIABLE: layerList                                                          #
# DESCRIPTION:                                                                 #
#   absolute path to a .csv file that is formatted with the following headers: #
#        -  NAME                (Name of Feature, eg. "Property Line")         #
#        -  ZONING CONSTRAINTS  (Buffer Distance, eg. "50ft")                  #
#        -  DATA PATH           (File Path to Feature. eg.                     #
#               "G:\arc_US_IL\DATA\BASEDATA\US_Geological_Survey\20170308_DEM")#
# NOTE:                                                                        #
#           for features requiring multiple data sources that are merged,      #
#           separate file paths with semicolons (;) on the same line           #
#           eg.  "G:\Path\thing.shp;G:\Path\stuff.shp;G:\Path\other.shp"       #

layerList = "G:\Scripts\WIP_Scripts\MD\layerList.csv"

# VARIABLE: studyArea                                                          #
# DESCRIPTION:                                                                 #
#           absolute path to the studyArea featureclass                        #
# NOTE:                                                                        #
#           This feature class is used to clip the constraint analysis features#
#           to the relevant subset                                             #

studyArea = "G:\MAPs\MXD\Map17_MXD\Map17-0111\ConstraintAnalysis_Leland_Mazon.gdb\Study_Area_B5Miles"

# VARIABLE: etToolboxNeeded & etToolboxPath                                    #
# DESCRIPTION:                                                                 #
#           ON/OFF switch and absolute path to the ET_Geowizards toolbox       #
# NOTE:                                                                        #
#           this toolbox is required to convert the polygonal parcel features  #
#           into polyline.  If the feature class linked to Property Line is    #
#           already converted to polyline, set etToolBoxNeeded to False.       #

etToolboxNeeded = True
etToolboxPath = 'C:\Program Files (x86)\ET SpatialTechniques\ET GeoWizards 11.3 for ArcGIS 10.3\ET GeoWizards.tbx'

# ------------------------------ CONSTANTS  END  ----------------------------- #

# ====================== AVOID EDITS BELOW THIS LINE ========================= #
# ======== EDITS BELOW THIS LINE MAY CAUSE THE SCRIPT TO STOP WORKING ======== #
# ==========================EDIT AT YOUR OWN RISK ============================ #
# ============================================================================ #

# ------------------------ METHOD DEFINITIONS START -------------------------- #

# A method to create a directory at path only if it does not already exist.
def ensure(path):
    try:
     os.makedirs(path)
    except OSError as exception:
     if exception.errno != errno.EEXIST:
         raise

# ------------------------- METHOD DEFINITIONS  END  ------------------------- #


# ------------------------------- MAIN START --------------------------------- #

arcpy.env.overwriteOutput = True
if etToolboxNeeded:
    arcpy.ImportToolbox(etToolboxPath)

print "The script is running..."

layerListString = open(layerList, 'r')
layerTuples = []
skip = True


# this for loop deals with organizing the instructions given in an external csv
print "Processing information from:"
print layerList

for i in layerListString:
    
    if skip: # skips the header row
        skip = False
        continue

    # following section obtains name, buffer dist, and file location
    commaIndex = i.index(",")
    name = i[0:commaIndex]
    i = i[commaIndex+1:]
    commaIndex = i.index(",")
    dist = i[0:commaIndex]
    location = i[commaIndex+1:]
    # following section deals with layers that have multiple file sources
    # by adding them into a list for merging later
    listLocation = []
    if ";" in location:
        while ";" in location:
            print "Adding: " + location[0:location.index(";")]
            listLocation.append(location[0:location.index(";")])
            location = location[location.index(";")+1:]
        listLocation.append(location.replace("\n",""))
    else:
        listLocation.append(location.replace("\n",""))
    #this creates a tuple to keep all info easily accessible    
    layerTuples.append((name,dist,listLocation))

print "Information processed."
print "Creating scratch copies..."
print os.getcwd()

scratch = 'scratch.gdb'
curDir = os.getcwd()
gdbDir = curDir+"\\"+scratch
print gdbDir

if arcpy.Exists(gdbDir):
    arcpy.Delete_management(gdbDir)
arcpy.CreateFileGDB_management(curDir, scratch)

scratch = scratch + "/"

for i in layerTuples:
    output = scratch+i[0].replace(" ","")
    print output
    arcpy.Merge_management(i[2], output)
    if i[0] == 'Property Line' and etToolboxNeeded:
        print "ET_Geowizards detected. Property Line conversion started."
        arcpy.ET_GPPolygonToPolyline(output,scratch+"Property_Line_GEN")

# --------------------------------- MAIN  END -------------------------------- #





