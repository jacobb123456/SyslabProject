# Python 2.7 and 3.5
# Author: Christoph Schranz, Salzburg Research

## You can preset the default model in line 42

import sys, argparse
import os
import time
from MeshTweaker import Tweak
import FileHandler as FH


def getargs(fileName):
    parser = argparse.ArgumentParser()                           
    args = parser.parse_args()
    args.version=False
    args.inputfile=fileName
    args.outputfile=None
    args.angle=45
    args.result=False
    args.verbose=False
    if args.version:
        print("Tweaker 0.2.11, (22 Oktober 2016)")
        return None        
    if not args.inputfile:
        try:
            curpath = os.path.dirname(os.path.realpath(__file__))
            args.inputfile=curpath + os.sep + "demo_object.stl"
            args.inputfile=curpath + os.sep + "death_star.stl"
            #args.inputfile=curpath + os.sep + "cylinder.3mf"
            
        except:
            return None          
    if not args.outputfile:
        args.outputfile = os.path.splitext(args.inputfile)[0] + "_tweaked"
        args.outputfile += ".stl" #Because 3mf is not supported for output #TODO

    argv = sys.argv[1:]
    if len(argv)==0:
        args.convert = False
        args.verbose = True
        args.bi_algorithmic = False            
    return args


def readSTL(fileName,printInfo=False):
    ## Get the command line arguments. Run in IDE for demo tweaking.
    stime=time.time()
    try:
        args = getargs(fileName)
        args.verbose=True
        if args is None:
            sys.exit()
    except:
        raise
        
    try:
        #print(args.inputfile)
        FileHandler = FH.FileHandler()
        objs = FileHandler.loadMesh(args.inputfile)
        
        if objs is None:
            sys.exit()
    except(KeyboardInterrupt, SystemExit):
        print("\nError, loading mesh from file failed!")
        raise
        
    ## Start of tweaking.
    c = 0
    for obj in objs:
        mesh = obj["Mesh"]
        if args.convert:
            R=[[1,0,0],[0,1,0],[0,0,1]]
        else:
            try:
                cstime = time.time()
                x=Tweak(mesh, args.bi_algorithmic, printInfo, args.angle)
                R=x.R
            except (KeyboardInterrupt, SystemExit):
                print("\nError, tweaking process failed!")
                raise
                
            ## List tweaking results
            if args.result or args.verbose:
                return x
                if args.result: 
                    sys.exit()
