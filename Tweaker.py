# Python 2.7 and 3.5
# Author: Christoph Schranz, Salzburg Research

## You can preset the default model in line 42

import sys, argparse
import os
import time
from MeshTweaker import Tweak
import FileHandler


def getargs():
    parser = argparse.ArgumentParser(description=
            "Orientation tool for better 3D prints")
    parser.add_argument('-vb', '--verbose', action="store_true",dest="verbose", 
                        help="increase output verbosity", default=False)
    parser.add_argument('-i', action="store",  
                        dest="inputfile", help="select input file")
    parser.add_argument('-o', action="store", dest="outputfile",
                        help="select output file. '_tweaked' is postfix by default")
    parser.add_argument('-c', '--convert', action="store_true",dest="convert", 
                        help="convert 3mf to stl without tweaking", default=False)
    parser.add_argument('-a', '--angle', action="store", dest="angle", type=int,
                        default=45,
                        help="specify critical angle for overhang demarcation in degrees")
    parser.add_argument('-b', '--bi', action="store_true", dest="bi_algorithmic", default=False,
                        help="using two algorithms for calculation")
    parser.add_argument('-v', '--version', action="store_true", dest="version",
                        help="print version number and exit", default=False)
    parser.add_argument('-r', '--result', action="store_true", dest="result",
                        help="show result of calculation and exit without creating output file",
                        default=False)                            
    args = parser.parse_args()

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
        print("""No additional arguments. Testing calculation with 
demo object in verbose and bi-algorithmic mode. Use argument -h for help.
""")
        args.convert = False
        args.verbose = True
        args.bi_algorithmic = False            
    return args


if __name__ == "__main__":
    ## Get the command line arguments. Run in IDE for demo tweaking.
    stime=time.time()
    try:
        args = getargs()
        if args is None:
            sys.exit()
    except:
        raise
        
    try:
        #print(args.inputfile)
        FileHandler = FileHandler.FileHandler()
        objs = FileHandler.loadMesh(args.inputfile)
        
        if objs is None:
            sys.exit()
    except(KeyboardInterrupt, SystemExit):
        print("\nError, loading mesh from file failed!")
        raise
        
    ## Start of tweaking.
    if args.verbose:
        print("Calculating the optimal orientation:\n  {}\n"
                        .format(args.inputfile.split("\\")[-1]))
    c = 0
    for obj in objs:
        mesh = obj["Mesh"]
        if args.convert:
            R=[[1,0,0],[0,1,0],[0,0,1]]
        else:
            try:
                cstime = time.time()
                x=Tweak(mesh, args.bi_algorithmic, args.verbose, args.angle)
                R=x.R
            except (KeyboardInterrupt, SystemExit):
                print("\nError, tweaking process failed!")
                raise
                
            ## List tweaking results
            if args.result or args.verbose:
                print("\nResult-stats:")
                print(" Tweaked Z-axis: \t{}".format((x.Zn)))
                print(" Axis, angle:   \t{v}, {phi}".format(v=x.v, phi=x.phi))
                print(""" Rotation matrix: 
            {:2f}\t{:2f}\t{:2f}
            {:2f}\t{:2f}\t{:2f}
            {:2f}\t{:2f}\t{:2f}""".format(x.R[0][0], x.R[0][1], x.R[0][2],
                                          x.R[1][0], x.R[1][1], x.R[1][2], 
                                          x.R[2][0], x.R[2][1], x.R[2][2]))
                print(" Unprintability: \t{}".format(x.Unprintability))
                
                print("\nFound result:    \t{:2f} s".format(time.time()-cstime))
                if args.result: 
                    sys.exit()   
          
        ## Creating tweaked output file
        if os.path.splitext(args.outputfile)[1].lower() in ["stl", ".stl"]:
            # If you want to write in binary, use the function rotatebinSTL(...)"
            tweakedcontent=FileHandler.rotateSTL(R, mesh, args.inputfile)       
            # Support structure suggestion can be used for further applications        
            #if x.Unprintability > 7:
            #    tweakedcontent+=" {supportstructure: yes}"
            if len(objs)<=1:
                outfile = args.outputfile
            else:
                outfile = os.path.splitext(args.outputfile)[0]+" ({})".format(c)+os.path.splitext(args.outputfile)[1]
            with open(outfile,'w') as outfile: # If you want to write in binary, open with "wb"
                outfile.write(tweakedcontent)

        else:
            transformation = "{} {} {} {} {} {} {} {} {} 0 0 1".format(x.R[0][0], x.R[0][1], x.R[0][2],
                                x.R[1][0], x.R[1][1], x.R[1][2], x.R[2][0], x.R[2][1], x.R[2][2])
            obj["transform"] = transformation
            FileHandler.rotate3MF(args.inputfile, args.outputfile, objs)

    

    ## Success message
    if args.verbose:
        print("Tweaking took:  \t{:2f} s".format(time.time()-stime))
        print("\nSuccessfully Rotated!")
