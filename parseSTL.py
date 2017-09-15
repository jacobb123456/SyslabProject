#imports
#import numpy
import math
from stl import mesh
#from matplotlib import pyplot
#from mpl_toolkits import mplot3d
import TweakerMod
#import pickle
import time
import os

#finds the optimal print angle, overhang, and printability
def parseSTL(fileName,printMod):
	output=TweakerMod.readSTL(os.path.join(filePathToSTLs,fileName),printMod)
	orientation=output.Zn
	overhang=output.overhang
	unprintability=output.Unprintability 
	bottomArea=output.bottomArea
	bestLine=output.line
	return orientation,overhang,unprintability,bottomArea,bestLine

def printSTL(fileName):
	figure = pyplot.figure()
	axes = mplot3d.Axes3D(figure)
	your_mesh = mesh.Mesh.from_file(fileName)
	axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))
	scale = your_mesh.points.flatten(-1)
	axes.auto_scale_xyz(scale, scale, scale)
	pyplot.show()

def volumeParse(fileName):
	your_mesh = mesh.Mesh.from_file(os.path.join(filePathToSTLs,fileName))
	volume, cog, inertia = your_mesh.get_mass_properties()
	return volume,cog,inertia

def loadFromFile():
	for file in os.listdir(filePathToSTLs):
		if file.endswith(".stl"):
			parse(file)

def loadPickle(pickleFile):
	listofURL=favorite_color=pickle.load(open(pickleFile,"rb"))
	for URL in listofURL:
		findSTLbyURL(URL)
	print(listofURL)

def findSTLbyURL(url):
	return None
	
def parseByUserInput():
	
	inputSTL=input("STL file name:")
	try:
		parse(inputSTL)
	except (FileNotFoundError):
		print("File Not Found")
	
def parse(fileName,printModifications=False,printSTLFile=False,printBasicInfo=True):
	if (printBasicInfo):
		st=time.time()
		print("------Currently parsing %s -----------" %fileName)
		volume,cog,inertia=volumeParse(fileName)
		#print(time.time()-st)
		orientation,overhang,unprintability,bottomArea,bestLine=parseSTL(fileName,printModifications)
		#print(time.time()-st)
		print("volume:",volume)
		print("cog:",cog)
		print("inertia:",inertia)
		print("orientation:",orientation)
		print("overhang:",overhang)
		print("unprintability:",unprintability)
		print("Bottom Area:",bottomArea)
		print("Best Line:",bestLine)
	if(printSTLFile):
		printSTL(fileName)

#parse("test1.stl")
#parseByUserInput()


filePathToSTLs="/afs/csl.tjhsst.edu/students/2018/2018jblinden/3dprint/STLs/"
loadFromFile()

#loadPickle("populars.p")

		
		
	
	

