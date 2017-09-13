# Python 2.7 and 3.5
# Author: Christoph Schranz, Salzburg Research

import sys
import math
import random
import time
import itertools
from collections import Counter

class Tweak:
    """ The Tweaker is an auto rotate class for 3D objects.
    It requires following mesh format as input:
     [[v1x,v1y,v1z],
      [v2x,v2y,v2z],
      .....
      [vnx,vny,vnz]]
    You can adjust this format in arrange_mesh(). For some applications,
     it is necessary to replace "face[0], face[1]" by "-face[0], -face[1]".

    The critical angle CA is a variable that can be set by the operator as
    it may depend on multiple factors such as material used, printing
     temperature, printing speed, etc.

    Following attributes of the class are supported:
    The tweaked z-axis' vector .z.
    Euler coords .v and .phi, where v is orthogonal to both z and z' and phi
     the angle between z and z' in rad.
    The rotational matrix .R, the new mesh is created, by multiplying each
     vector with R.
    The vector of the new
    And the relative unprintability of the tweaked object. If this value is
     greater than 15, a support structure is suggested.
        """
    def __init__(self, mesh, bi_algorithmic, verbose, CA=45, n=[0,0,-1]):
        
        self.bi_algorithmic = bi_algorithmic
        
        content = self.arrange_mesh(mesh)
        #print("Object has {} facets".format(len(content)))
        arcum_time = dialg_time = lit_time=0
                
        ## Calculating initial printability
        amin = self.approachfirstvertex(content)
        bottomA, overhangA, lineL = self.lithograph(content,[0.0,0.0,1.0],amin,CA)
        liste = [[[0.0,0.0,1.0], bottomA, overhangA, lineL]]


        ## Searching promising orientations: 
        ## Format: [[vector1, gesamtA1],...[vector5, gesamtA5]]: %s", o)
        arcum_time = time.time()
        orientations = self.area_cumulation(content, n)

        arcum_time = time.time() - arcum_time
        if bi_algorithmic:
            dialg_time = time.time()
            orientations += self.egde_plus_vertex(mesh, 12)
            dialg_time = time.time() - dialg_time
            
            orientations = self.remove_duplicates(orientations)
            
        if verbose:
            print("Examine {} orientations:".format(len(orientations)))
            print("  %-32s %-18s%-18s%-18s%-18s " %("Area Vector:", 
            "Touching Area:", "Overhang:", "Line length:", "Unprintability:"))
        
        
        # Calculate the printability of each orientation
        lit_time = time.time()
        for side in orientations:
            orientation = [float("{:6f}".format(-i)) for i in side[0]]
            ## vector: sn, cum_A: side[1]
            amin=self.approachvertex(content, orientation)
            bottomA, overhangA, lineL = self.lithograph(content, orientation, amin, CA)
            liste.append([orientation, bottomA, overhangA, lineL])   #[Vector, touching area, Overhang, Touching_Line]
        
        
        # target function
        Unprintability = sys.maxsize
        for orientation, bottomA, overhangA, lineL in liste:
            F = self.target_function(bottomA, overhangA, lineL) # touching area: i[1], overhang: i[2], touching line i[3]
            if F<Unprintability - 0.05:
                Unprintability=F
                bestside = [orientation, bottomA, overhangA, lineL]
            if verbose:
                print("  %-32s %-18s%-18s%-18s%-18s " %(str(orientation), round(bottomA,3), 
                      round(overhangA,3),round(lineL,3), round(F,3)))
            time.sleep(0)  # Yield, so other threads get a bit of breathing space.
            
           
           
        lit_time = time.time() - lit_time
        if verbose:
            print("""
Time-stats of algorithm:
  Area Cumulation:  \t{ac:2f} s
  Edge plus Vertex:  \t{da:2f} s
  Lithography Time:  \t{lt:2f} s  
  Total Time:        \t{tot:2f} s
""".format(ac=arcum_time, da=dialg_time, lt=lit_time, 
           tot=arcum_time + dialg_time + lit_time))  
           
           
        if bestside:
            [v,phi,R] = self.euler(bestside)
            
        self.v=v
        self.phi=phi
        self.R=R
        self.Unprintability = Unprintability
        self.Zn=bestside[0]
        self.bottomArea=bestside[1]
        self.overhang=bestside[2]
        self.line=bestside[3]


    def target_function(self, touching, overhang, line):
        '''This function returns the printability with the touching area and overhang given.'''
        ABSLIMIT=100             # Some values for scaling the printability
        RELLIMIT=1
        LINE_FAKTOR = 0.5
        touching_line = line * LINE_FAKTOR
        F = (overhang/ABSLIMIT) + (overhang / (touching+touching_line) /RELLIMIT)
        ret = float("{:f}".format(F))
        return ret
        
        
    def arrange_mesh(self, mesh):
        '''The Tweaker needs the mesh format of the object with the normals of the facetts.'''
        face=[]
        content=[]
        i=0
        for li in mesh:      
            face.append(li)
            i+=1
            if i%3==0:
                v=[face[1][0]-face[0][0],face[1][1]-face[0][1],face[1][2]-face[0][2]]
                w=[face[2][0]-face[0][0],face[2][1]-face[0][1],face[2][2]-face[0][2]]
                a=[round(v[1]*w[2]-v[2]*w[1],6), round(v[2]*w[0]-v[0]*w[2],6), round(v[0]*w[1]-v[1]*w[0],6)]
                content.append([a,face[0],face[1],face[2]])
                face=[]
            time.sleep(0)  # Yield, so other threads get a bit of breathing space.
        return content

    
    def approachfirstvertex(self,content):
        '''Returning the lowest z value'''
        amin=sys.maxsize
        for li in content:
            z=min([li[1][2],li[2][2],li[3][2]])
            if z<amin:
                amin=z
            time.sleep(0)  # Yield, so other threads get a bit of breathing space.
        return amin


    def approachvertex(self, content, n):
        '''Returning the lowest value regarding vector n'''
        amin=sys.maxsize
        for li in content:
            a1 = li[1][0]*n[0] +li[1][1]*n[1] +li[1][2]*n[2]
            a2 = li[2][0]*n[0] +li[2][1]*n[1] +li[2][2]*n[2]
            a3 = li[3][0]*n[0] +li[3][1]*n[1] +li[3][2]*n[2]          
            an=min([a1,a2,a3])
            if an<amin:
                amin=an
            time.sleep(0)  # Yield, so other threads get a bit of breathing space.
        return amin

        
    def lithograph(self, content, n, amin, CA):
        '''Calculating touching areas and overhangs regarding the vector n'''
        Overhang=1
        alpha=-math.cos((90-CA)*math.pi/180)
        bottomA=1
        LineL = 1
        touching_height = amin+0.15
        
        anti_n = [float(-i) for i in n]

        for li in content:
            time.sleep(0)  # Yield, so other threads get a bit of breathing space.
            a=li[0]
            norma=math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])
            if norma < 2:
                continue
            if alpha > (a[0]*n[0] +a[1]*n[1] +a[2]*n[2])/norma:
                a1 = li[1][0]*n[0] +li[1][1]*n[1] +li[1][2]*n[2]
                a2 = li[2][0]*n[0] +li[2][1]*n[1] +li[2][2]*n[2]
                a3 = li[3][0]*n[0] +li[3][1]*n[1] +li[3][2]*n[2]
                an = min([a1,a2,a3])
                
                ali = float("{:1.4f}".format(abs(li[0][0]*n[0] +li[0][1]*n[1] +li[0][2]*n[2])/2))
                if touching_height < an:
                    if 0.00001 < math.fabs(a[0]-anti_n[0]) + math.fabs(a[1]-anti_n[1]) + math.fabs(a[2]-anti_n[2]):
                        ali = 0.8 * ali
                    Overhang += ali
                else:
                    bottomA += ali
                    LineL += self.get_touching_line([a1,a2,a3], li, touching_height)
                time.sleep(0)  # Yield, so other threads get a bit of breathing space.
        return bottomA, Overhang, LineL
    
    def get_touching_line(self, a, li, touching_height):
        touch_lst = list()
        for i in range(3):
            if a[i] < touching_height:
                touch_lst.append(li[1+i])
        combs = list(itertools.combinations(touch_lst, 2))
        if len(combs) <= 1:
            return 0
        length = 0
        for p1, p2 in combs:
            time.sleep(0)  # Yield, so other threads get a bit of breathing space.
            length += math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 
                                        + (p2[2]-p1[2])**2)
        return length

    def area_cumulation(self, content, n):
        '''Searching best options out of the objects area vector field'''
        if self.bi_algorithmic: best_n = 7
        else: best_n = 5
        orient = Counter()
        for li in content:       # Cumulate areavectors
            an = li[0]
            A = math.sqrt(an[0]*an[0] + an[1]*an[1] + an[2]*an[2])
            
            if A > 0:
                an = [float("{:1.6f}".format(i/A, 6)) for i in an]
                orient[tuple(an)] += A

        time.sleep(0)  # Yield, so other threads get a bit of breathing space.
        top_n = orient.most_common(best_n)
        return [[[0.0,0.0,1.0], 0.0]] + [[list(el[0]), float("{:2f}".format(el[1]))] for el in top_n]
       

    def egde_plus_vertex(self, mesh, best_n):
        '''Searching normals or random edges with one vertice'''
        vcount = len(mesh)
        # Small files need more calculations
        if vcount < 10000: it = 5
        elif vcount < 25000: it = 2
        else: it = 1           
        self.mesh = mesh
        lst = map(self.calc_random_normal, list(range(vcount))*it)
        lst = filter(lambda x: x is not None, lst)
        
        time.sleep(0)  # Yield, so other threads get a bit of breathing space.
        orient = Counter(lst)
        
        top_n = orient.most_common(best_n)
        top_n = filter(lambda x: x[1]>2, top_n)

        return [[list(el[0]), el[1]] for el in top_n]

    def calc_random_normal(self, i):
        if i%3 == 0:
            v = self.mesh[i]
            w = self.mesh[i+1]
        elif i%3 == 1:
            v = self.mesh[i]
            w = self.mesh[i+1]
        else:
            v = self.mesh[i]
            w = self.mesh[i-2]
        r_v = random.choice(self.mesh)
        v = [v[0]-r_v[0], v[1]-r_v[1], v[2]-r_v[2]]
        w = [w[0]-r_v[0], w[1]-r_v[1], w[2]-r_v[2]]
        a=[v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0]]
        n = math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])
        if n != 0:
            return tuple([round(d/n, 6) for d in a])


    def remove_duplicates(self, o):
        '''Removing duplicates in orientation'''
        orientations = list()
        for i in o:
            duplicate = None
            for j in orientations:
                time.sleep(0)  # Yield, so other threads get a bit of breathing space.
                dif = math.sqrt( (i[0][0]-j[0][0])**2 + (i[0][1]-j[0][1])**2 + (i[0][2]-j[0][2])**2 )
                if dif < 0.001:
                    duplicate = True
                    break
            if duplicate is None:
                orientations.append(i)
        return orientations



    def euler(self, bestside):
        '''Calculating euler params and rotation matrix'''
        if bestside[0] == [0, 0, -1]:
            v = [1, 0, 0]
            phi = math.pi
        elif bestside[0]==[0,0,1]:
            v=[1,0,0]
            phi=0
        else:
            phi = float("{:2f}".format(math.pi - math.acos( -bestside[0][2] )))
            v = [-bestside[0][1] , bestside[0][0], 0]
            v = [i / math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) for i in v]
            v = [float("{:2f}".format(i)) for i in v]

        R = [[v[0] * v[0] * (1 - math.cos(phi)) + math.cos(phi),
              v[0] * v[1] * (1 - math.cos(phi)) - v[2] * math.sin(phi),
              v[0] * v[2] * (1 - math.cos(phi)) + v[1] * math.sin(phi)],
             [v[1] * v[0] * (1 - math.cos(phi)) + v[2] * math.sin(phi),
              v[1] * v[1] * (1 - math.cos(phi)) + math.cos(phi),
              v[1] * v[2] * (1 - math.cos(phi)) - v[0] * math.sin(phi)],
             [v[2] * v[0] * (1 - math.cos(phi)) - v[1] * math.sin(phi),
              v[2] * v[1] * (1 - math.cos(phi)) + v[0] * math.sin(phi),
              v[2] * v[2] * (1 - math.cos(phi)) + math.cos(phi)]]
        R = [[float("{:2f}".format(val)) for val in row] for row in R] 
        return v,phi,R
