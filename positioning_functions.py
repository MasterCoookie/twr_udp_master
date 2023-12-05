import numpy as np

def trilaterate_3d_4dists(distances):
    p1=np.array(distances[0][:3])
    p2=np.array(distances[1][:3])
    p3=np.array(distances[2][:3])       
    p4=np.array(distances[3][:3])

    r1=distances[0][-1]
    r2=distances[1][-1]
    r3=distances[2][-1]
    r4=distances[3][-1]

    e_x=(p2-p1)/np.linalg.norm(p2-p1)
    i=np.dot(e_x,(p3-p1))
    e_y=(p3-p1-(i*e_x))/(np.linalg.norm(p3-p1-(i*e_x)))
    e_z=np.cross(e_x,e_y)

    d=np.linalg.norm(p2-p1)
    j=np.dot(e_y,(p3-p1))

    x=((r1**2)-(r2**2)+(d**2))/(2*d)
    y=(((r1**2)-(r3**2)+(i**2)+(j**2))/(2*j))-((i/j)*(x))

    pre_sqrt=(r1**2-x**2-y**2)

    print("pre_sqrt", pre_sqrt)
    if pre_sqrt < 0:
        if pre_sqrt > -0.0001:
            pre_sqrt = 0
        else:
            print("no intersection")
            return None
        # pre_sqrt = np.abs(pre_sqrt)

    z1=np.sqrt(pre_sqrt)
    z2=np.sqrt(pre_sqrt)*(-1)

    ans1=p1+(x*e_x)+(y*e_y)+(z1*e_z)
    ans2=p1+(x*e_x)+(y*e_y)+(z2*e_z)

    dist1=np.linalg.norm(p4-ans1)
    dist2=np.linalg.norm(p4-ans2)

    if np.abs(r4-dist1)<np.abs(r4-dist2):
        return ans1
    else: 
        return ans2
    
def polyfit_3d(points):
    x = []
    y = []
    z = []
    timestamps = []
    for point in points:
        x.append(point[0])
        y.append(point[1])
        z.append(point[2])
        timestamps.append(point[3])

    diff = 0

    for timestamp in timestamps:
        diff += timestamp - timestamps[0]

    mean_step = diff / len(timestamps)    
    
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    timestamps = np.array(timestamps)

    x_fit = np.polyfit(timestamps, x, 2)
    y_fit = np.polyfit(timestamps, y, 2)
    z_fit = np.polyfit(timestamps, z, 2)

    new_timestamp = timestamps[-1] + mean_step

    x_new = np.polyval(x_fit, new_timestamp)
    y_new = np.polyval(y_fit, new_timestamp)
    z_new = np.polyval(z_fit, new_timestamp)

    return [x_new, y_new, z_new]
