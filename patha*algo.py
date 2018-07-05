import psycopg2
import numpy
import os.path
from geopy.distance import distance as distc
startnode=(78.2289493775353, 17.2105959876537)
endnode=(78.2280678607469, 17.2120758472188)
def distance(a,b):
	return distc([a[1],a[0]],[b[1],b[0]])
def hueristic(currentnode,previousdistance):
	return distance(currentnode,endnode).km+previousdistance
def binarysearch(left,right,thelist,tofind):
	if left>right:
		return left
	mid=int((left+right)/2)
	if thelist[mid][1]<tofind:
		left=mid+1
	elif thelist[mid][1]>tofind:
		right=mid-1
	else:
		return mid
	return binarysearch(left,right,thelist,tofind)
def closedbinarysearch(left,right,thelist,tofind):
	if left>right:
		return left
	mid=int((left+right)/2)
	if thelist[mid][0][0]<tofind:
		left=mid+1
	elif thelist[mid][0][0]>tofind:
		right=mid-1
	else:
		return mid
	return closedbinarysearch(left,right,thelist,tofind)

conn = psycopg2.connect("dbname=hyd_map_db user=postgres password=newpassword")
cur = conn.cursor()
if os.path.isfile("file.npy"):
	listofways=numpy.load("file.npy")
else:
	cur.execute("""SELECT ST_AsText(ST_Transform(ST_GeomFromText(ST_AsText(way),900913),4326)) As wgs_geom from planet_osm_line """)
	way=cur.fetchall()
	listofways = []
	for points in way:
		nodes=points[0][11:-1].split(",")
		listofnodes=[]
		for node in nodes:
			point=tuple(map(float,node.split()))
			#point=map(float,node.split())
			listofnodes.append(point)
		listofways.append(listofnodes)
	listofways=numpy.array(listofways)
	numpy.save("file",listofways)
print listofways[0]
print listofways[1]
fp=[startnode,hueristic(startnode,0),0,startnode] #currentnode,F,distance,previousnode
openlist=[]
closedlist=[]
openlist.append(fp)
f=1
i=10
while f and len(openlist):
	i-=1
	checknode=openlist[0]
	currentnode=checknode[0]
	del openlist[0]
	itemindex = [(index, row.index(currentnode)) for index, row in enumerate(listofways) if currentnode in row]
	childnodes=[]
	for item in itemindex:
		if item[1]+1<len(listofways[item[0]]):
			childnodes.append(listofways[item[0]][item[1]+1])
		if item[1]-1>=0:
			childnodes.append(listofways[item[0]][item[1]-1])
	for node in childnodes:
		if node==endnode:
			f=0
		dist=checknode[2]+distance(currentnode,node).km
		hvalue=hueristic(node,dist)
		openindex=0
		for opennode in openlist:
			if opennode[0]==node:
				break
			openindex+=1
		closedindex=closedbinarysearch(0,len(closedlist)-1,closedlist,node[0])
		if closedindex!=len(closedlist) and closedlist[closedindex][0]!=node:
			closedindex=len(closedlist)
		point=[node,hvalue,dist,currentnode]
		if node==endnode:
			endpoint=point
		index=binarysearch(0,len(openlist)-1,openlist,hvalue)
		if openindex==len(openlist) and closedindex==len(closedlist):
			openlist.insert(index,point)
		elif openindex!=len(openlist):
			if hvalue<openlist[openindex][1]:
				del openlist[openindex]
				if openindex>index:
					openlist.insert(index,point)
				else:
					openlist.insert(index-1,point)
		else:
			if hvalue<closedlist[closedindex][1]:
				del closedlist[closedindex]
				openlist.insert(index,point)
	closedlist.insert(closedbinarysearch(0,len(closedlist)-1,closedlist,checknode[0][0]),checknode)
	print openlist,'\n\n',closedlist,'\n\n\n'
print endpoint[2]
	
