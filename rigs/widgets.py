import bpy
import importlib
import importlib
from mathutils import Matrix, Vector
from math import pi, sin, cos
from ..utils import create_widget, create_circle_polygon

MODULE_NAME = "super_widgets"  # Windows/Mac blender is weird, so __package__ doesn't work


def create_eye_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(1.1920928955078125e-07*size, 0.5000000596046448*size, 0.0*size), (-0.12940943241119385*size, 0.482962965965271*size, 0.0*size), (-0.24999988079071045*size, 0.4330127537250519*size, 0.0*size), (-0.35355329513549805*size, 0.35355344414711*size, 0.0*size), (-0.43301260471343994*size, 0.2500000596046448*size, 0.0*size), (-0.4829627275466919*size, 0.12940959632396698*size, 0.0*size), (-0.49999988079071045*size, 1.0094120739267964e-07*size, 0.0*size), (-0.482962965965271*size, -0.12940940260887146*size, 0.0*size), (-0.43301260471343994*size, -0.24999986588954926*size, 0.0*size), (-0.3535534143447876*size, -0.35355323553085327*size, 0.0*size), (-0.25*size, -0.43301257491111755*size, 0.0*size), (-0.1294095516204834*size, -0.48296281695365906*size, 0.0*size), (-1.1920928955078125e-07*size, -0.4999999403953552*size, 0.0*size), (0.12940943241119385*size, -0.4829629063606262*size, 0.0*size), (0.24999988079071045*size, -0.4330127537250519*size, 0.0*size), (0.35355329513549805*size, -0.35355353355407715*size, 0.0*size), (0.4330127239227295*size, -0.25000008940696716*size, 0.0*size), (0.482962965965271*size, -0.12940965592861176*size, 0.0*size), (0.5000001192092896*size, -1.6926388468618825e-07*size, 0.0*size), (0.48296308517456055*size, 0.1294093281030655*size, 0.0*size), (0.4330129623413086*size, 0.24999980628490448*size, 0.0*size), (0.35355377197265625*size, 0.35355323553085327*size, 0.0*size), (0.25000035762786865*size, 0.43301260471343994*size, 0.0*size), (0.1294100284576416*size, 0.48296287655830383*size, 0.0*size), ]
        edges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19), (21, 20), (22, 21), (23, 22), (0, 23), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_eyes_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(0.8928930759429932*size, -0.7071065902709961*size, 0.0*size), (0.8928932547569275*size, 0.7071067690849304*size, 0.0*size), (-1.8588197231292725*size, -0.9659252762794495*size, 0.0*size), (-2.100001096725464*size, -0.8660248517990112*size, 0.0*size), (-2.3071072101593018*size, -0.7071059942245483*size, 0.0*size), (-2.4660258293151855*size, -0.49999913573265076*size, 0.0*size), (-2.5659260749816895*size, -0.258818119764328*size, 0.0*size), (-2.5999999046325684*size, 8.575012770961621e-07*size, 0.0*size), (-2.5659255981445312*size, 0.2588198482990265*size, 0.0*size), (-2.4660253524780273*size, 0.5000006556510925*size, 0.0*size), (-2.3071064949035645*size, 0.7071075439453125*size, 0.0*size), (-2.099999189376831*size, 0.866025984287262*size, 0.0*size), (-1.8588184118270874*size, 0.9659261703491211*size, 0.0*size), (-1.5999996662139893*size, 1.000000238418579*size, 0.0*size), (-1.341180443763733*size, 0.9659258723258972*size, 0.0*size), (-1.0999995470046997*size, 0.8660253882408142*size, 0.0*size), (-0.8928929567337036*size, 0.7071067094802856*size, 0.0*size), (-0.892893373966217*size, -0.7071066498756409*size, 0.0*size), (-1.100000262260437*size, -0.8660252690315247*size, 0.0*size), (-1.3411810398101807*size, -0.9659255743026733*size, 0.0*size), (1.600000023841858*size, 1.0*size, 0.0*size), (1.3411810398101807*size, 0.9659258127212524*size, 0.0*size), (1.100000023841858*size, 0.8660253882408142*size, 0.0*size), (-1.600000262260437*size, -0.9999997615814209*size, 0.0*size), (1.0999997854232788*size, -0.8660252690315247*size, 0.0*size), (1.341180682182312*size, -0.9659257531166077*size, 0.0*size), (1.5999996662139893*size, -1.0*size, 0.0*size), (1.8588186502456665*size, -0.965925931930542*size, 0.0*size), (2.0999996662139893*size, -0.8660256266593933*size, 0.0*size), (2.3071064949035645*size, -0.7071071863174438*size, 0.0*size), (2.4660253524780273*size, -0.5000002980232239*size, 0.0*size), (2.5659255981445312*size, -0.25881943106651306*size, 0.0*size), (2.5999999046325684*size, -4.649122899991198e-07*size, 0.0*size), (2.5659260749816895*size, 0.25881853699684143*size, 0.0*size), (2.4660258293151855*size, 0.4999994933605194*size, 0.0*size), (2.3071072101593018*size, 0.707106351852417*size, 0.0*size), (2.1000006198883057*size, 0.8660250902175903*size, 0.0*size), (1.8588197231292725*size, 0.9659256339073181*size, 0.0*size), (-1.8070557117462158*size, -0.7727401852607727*size, 0.0*size), (-2.0000009536743164*size, -0.6928198337554932*size, 0.0*size), (-2.1656856536865234*size, -0.5656847357749939*size, 0.0*size), (-2.292820692062378*size, -0.3999992609024048*size, 0.0*size), (-2.3727407455444336*size, -0.20705445110797882*size, 0.0*size), (-2.3999998569488525*size, 7.336847716032935e-07*size, 0.0*size), (-2.3727405071258545*size, 0.207055926322937*size, 0.0*size), (-2.2928202152252197*size, 0.40000057220458984*size, 0.0*size), (-2.1656851768493652*size, 0.5656861066818237*size, 0.0*size), (-1.9999992847442627*size, 0.6928208470344543*size, 0.0*size), (-1.8070547580718994*size, 0.7727410197257996*size, 0.0*size), (-1.5999996662139893*size, 0.8000002503395081*size, 0.0*size), (-1.3929443359375*size, 0.7727407813072205*size, 0.0*size), (-1.1999995708465576*size, 0.6928203701972961*size, 0.0*size), (-1.0343143939971924*size, 0.5656854510307312*size, 0.0*size), (-1.0343146324157715*size, -0.5656852722167969*size, 0.0*size), (-1.2000001668930054*size, -0.6928201913833618*size, 0.0*size), (-1.3929448127746582*size, -0.7727404236793518*size, 0.0*size), (-1.6000001430511475*size, -0.7999997735023499*size, 0.0*size), (1.8070557117462158*size, 0.772739827632904*size, 0.0*size), (2.0000009536743164*size, 0.6928195953369141*size, 0.0*size), (2.1656856536865234*size, 0.5656843781471252*size, 0.0*size), (2.292820692062378*size, 0.39999890327453613*size, 0.0*size), (2.3727407455444336*size, 0.20705409348011017*size, 0.0*size), (2.3999998569488525*size, -1.0960745839838637e-06*size, 0.0*size), (2.3727405071258545*size, -0.20705628395080566*size, 0.0*size), (2.2928202152252197*size, -0.4000009298324585*size, 0.0*size), (2.1656851768493652*size, -0.5656863451004028*size, 0.0*size), (1.9999992847442627*size, -0.692821204662323*size, 0.0*size), (1.8070547580718994*size, -0.7727413773536682*size, 0.0*size), (1.5999996662139893*size, -0.8000004887580872*size, 0.0*size), (1.3929443359375*size, -0.7727410197257996*size, 0.0*size), (1.1999995708465576*size, -0.6928204894065857*size, 0.0*size), (1.0343143939971924*size, -0.5656855702400208*size, 0.0*size), (1.0343146324157715*size, 0.5656850337982178*size, 0.0*size), (1.2000004053115845*size, 0.6928199529647827*size, 0.0*size), (1.3929448127746582*size, 0.7727401852607727*size, 0.0*size), (1.6000001430511475*size, 0.7999995350837708*size, 0.0*size), ]
        edges = [(24, 0), (1, 22), (16, 1), (17, 0), (23, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (21, 20), (22, 21), (13, 14), (14, 15), (15, 16), (17, 18), (18, 19), (19, 23), (25, 24), (26, 25), (27, 26), (28, 27), (29, 28), (30, 29), (31, 30), (32, 31), (33, 32), (34, 33), (35, 34), (36, 35), (37, 36), (20, 37), (56, 38), (38, 39), (39, 40), (40, 41), (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50), (50, 51), (51, 52), (53, 54), (54, 55), (55, 56), (75, 57), (57, 58), (58, 59), (59, 60), (60, 61), (61, 62), (62, 63), (63, 64), (64, 65), (65, 66), (66, 67), (67, 68), (68, 69), (69, 70), (70, 71), (72, 73), (73, 74), (74, 75), (52, 72), (53, 71), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_ear_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(-2.4903741291382175e-09*size, 1.0*size, -3.123863123732917e-08*size), (-7.450580596923828e-09*size, 0.9829629063606262*size, 0.0776456817984581*size), (-1.4901161193847656e-08*size, 0.9330127239227295*size, 0.1499999761581421*size), (-2.9802322387695312e-08*size, 0.8535534143447876*size, 0.2121320217847824*size), (-2.9802322387695312e-08*size, 0.75*size, 0.25980761647224426*size), (-2.9802322387695312e-08*size, 0.6294095516204834*size, 0.2897777259349823*size), (-2.9802322387695312e-08*size, 0.5000000596046448*size, 0.29999998211860657*size), (-5.960464477539063e-08*size, 0.37059056758880615*size, 0.2897777855396271*size), (-5.960464477539063e-08*size, 0.25000008940696716*size, 0.25980767607688904*size), (-4.470348358154297e-08*size, 0.14644670486450195*size, 0.21213211119174957*size), (-4.470348358154297e-08*size, 0.06698736548423767*size, 0.15000009536743164*size), (-4.470348358154297e-08*size, 0.017037123441696167*size, 0.07764581590890884*size), (-3.6718930118695425e-08*size, 0.0*size, 1.1981423142515268e-07*size), (-2.9802322387695312e-08*size, 0.017037034034729004*size, -0.07764559239149094*size), (-2.9802322387695312e-08*size, 0.06698718667030334*size, -0.14999987185001373*size), (-1.4901161193847656e-08*size, 0.14644640684127808*size, -0.21213191747665405*size), (0.0*size, 0.24999985098838806*size, -0.25980761647224426*size), (0.0*size, 0.3705902695655823*size, -0.2897777259349823*size), (0.0*size, 0.4999997615814209*size, -0.30000004172325134*size), (0.0*size, 0.6294092535972595*size, -0.2897777855396271*size), (0.0*size, 0.7499997615814209*size, -0.2598077356815338*size), (1.4901161193847656e-08*size, 0.8535531759262085*size, -0.21213220059871674*size), (0.0*size, 0.9330125451087952*size, -0.15000019967556*size), (0.0*size, 0.9829628467559814*size, -0.07764596492052078*size), ]
        edges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19), (21, 20), (22, 21), (23, 22), (0, 23), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_jaw_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(0.606898307800293*size, 0.6533132195472717*size, 0.09324522316455841*size), (0.5728408694267273*size, 0.7130533456802368*size, 0.04735109210014343*size), (0.478340744972229*size, 0.856249213218689*size, 0.0167550016194582*size), (0.3405401408672333*size, 1.0092359781265259*size, 0.003642391413450241*size), (0.1764744222164154*size, 1.1159402132034302*size, 0.0003642391529865563*size), (0.5728408694267273*size, 0.7130533456802368*size, 0.1391393542289734*size), (0.478340744972229*size, 0.856249213218689*size, 0.16973544657230377*size), (0.3405401408672333*size, 1.0092359781265259*size, 0.18284805119037628*size), (0.1764744222164154*size, 1.1159402132034302*size, 0.1861262023448944*size), (0.0*size, 1.153113603591919*size, 0.0*size), (-0.606898307800293*size, 0.6533132195472717*size, 0.09324522316455841*size), (-0.5728408694267273*size, 0.7130533456802368*size, 0.04735109210014343*size), (-0.478340744972229*size, 0.856249213218689*size, 0.0167550016194582*size), (-0.3405401408672333*size, 1.0092359781265259*size, 0.003642391413450241*size), (-0.1764744222164154*size, 1.1159402132034302*size, 0.0003642391529865563*size), (0.0*size, 1.153113603591919*size, 0.18649044632911682*size), (-0.5728408694267273*size, 0.7130533456802368*size, 0.1391393542289734*size), (-0.478340744972229*size, 0.856249213218689*size, 0.16973544657230377*size), (-0.3405401408672333*size, 1.0092359781265259*size, 0.18284805119037628*size), (-0.1764744222164154*size, 1.1159402132034302*size, 0.1861262023448944*size), ]
        edges = [(1, 0), (2, 1), (3, 2), (4, 3), (9, 4), (6, 5), (7, 6), (8, 7), (15, 8), (5, 0), (11, 10), (12, 11), (13, 12), (14, 13), (9, 14), (17, 16), (18, 17), (19, 18), (15, 19), (16, 10), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_teeth_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(0.6314387321472168*size, 0.4999997019767761*size, 0.09999999403953552*size), (0.5394065976142883*size, 0.29289281368255615*size, 0.09999999403953552*size), (0.3887903690338135*size, 0.1339743733406067*size, 0.09999999403953552*size), (0.19801488518714905*size, 0.03407406806945801*size, 0.09999999403953552*size), (-3.4034394502668874e-07*size, 0.0*size, 0.09999999403953552*size), (-0.19801555573940277*size, 0.034074246883392334*size, 0.09999999403953552*size), (-0.7000000476837158*size, 1.0000001192092896*size, -0.10000000894069672*size), (-0.6778771877288818*size, 0.7411810755729675*size, -0.10000000894069672*size), (-0.6314389705657959*size, 0.5000001192092896*size, -0.10000000894069672*size), (-0.5394070148468018*size, 0.2928934097290039*size, -0.10000000894069672*size), (-0.38879096508026123*size, 0.13397473096847534*size, -0.10000000894069672*size), (-0.19801555573940277*size, 0.034074246883392334*size, -0.10000000894069672*size), (-3.4034394502668874e-07*size, 0.0*size, -0.10000000894069672*size), (0.19801488518714905*size, 0.03407406806945801*size, -0.10000000894069672*size), (0.3887903690338135*size, 0.1339743733406067*size, -0.10000000894069672*size), (0.5394065976142883*size, 0.29289281368255615*size, -0.10000000894069672*size), (0.6314387321472168*size, 0.4999997019767761*size, -0.10000000894069672*size), (0.6778769493103027*size, 0.7411805391311646*size, -0.10000000894069672*size), (0.6999999284744263*size, 0.9999995231628418*size, -0.10000000894069672*size), (-0.38879096508026123*size, 0.13397473096847534*size, 0.09999999403953552*size), (-0.5394070148468018*size, 0.2928934097290039*size, 0.09999999403953552*size), (-0.6314389705657959*size, 0.5000001192092896*size, 0.09999999403953552*size), (-0.6778771877288818*size, 0.7411810755729675*size, 0.09999999403953552*size), (-0.7000000476837158*size, 1.0000001192092896*size, 0.09999999403953552*size), (0.6778769493103027*size, 0.7411805391311646*size, 0.09999999403953552*size), (0.6999999284744263*size, 0.9999995231628418*size, 0.09999999403953552*size), ]
        edges = [(25, 24), (24, 0), (0, 1), (1, 2), (2, 3), (3, 4), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (4, 5), (5, 19), (19, 20), (20, 21), (21, 22), (22, 23), (18, 25), (6, 23), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_face_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(-0.25*size, -0.25*size, 0.07499998807907104*size), (-0.25*size, 0.25*size, 0.07499998807907104*size), (0.25*size, 0.25*size, 0.07499998807907104*size), (0.25*size, -0.25*size, 0.07499998807907104*size), (-0.25*size, -0.25*size, -0.07499998807907104*size), (-0.25*size, 0.25*size, -0.07499998807907104*size), (0.25*size, 0.25*size, -0.07499998807907104*size), (0.25*size, -0.25*size, -0.07499998807907104*size), ]
        edges = [(4, 5), (5, 1), (1, 0), (0, 4), (5, 6), (6, 2), (2, 1), (6, 7), (7, 3), (3, 2), (7, 4), (0, 3), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_ikarrow_widget(rig, bone_name, size=1.0, bone_transform_name=None, roll=0):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(0.10000000149011612*size, 0.0*size, -0.30000001192092896*size), (0.10000000149011612*size, 0.699999988079071*size, -0.30000001192092896*size), (-0.10000000149011612*size, 0.0*size, -0.30000001192092896*size), (-0.10000000149011612*size, 0.699999988079071*size, -0.30000001192092896*size), (0.20000000298023224*size, 0.699999988079071*size, -0.30000001192092896*size), (0.0*size, 1.0*size, -0.30000001192092896*size), (-0.20000000298023224*size, 0.699999988079071*size, -0.30000001192092896*size), (0.10000000149011612*size, 0.0*size, 0.30000001192092896*size), (0.10000000149011612*size, 0.699999988079071*size, 0.30000001192092896*size), (-0.10000000149011612*size, 0.0*size, 0.30000001192092896*size), (-0.10000000149011612*size, 0.699999988079071*size, 0.30000001192092896*size), (0.20000000298023224*size, 0.699999988079071*size, 0.30000001192092896*size), (0.0*size, 1.0*size, 0.30000001192092896*size), (-0.20000000298023224*size, 0.699999988079071*size, 0.30000001192092896*size), ]
        edges = [(0, 1), (2, 3), (1, 4), (4, 5), (3, 6), (5, 6), (0, 2), (7, 8), (9, 10), (8, 11), (11, 12), (10, 13), (12, 13), (7, 9), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()

        if roll != 0:
            rot_mat = Matrix.Rotation(roll, 4, 'Y')
            mesh.transform(rot_mat)
        return obj
    else:
        return None


def create_hand_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    # Create hand widget
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(0.0*size, 1.5*size, -0.7000000476837158*size), (1.1920928955078125e-07*size, -0.25*size, -0.6999999284744263*size), (0.0*size, -0.25*size, 0.7000000476837158*size), (-1.1920928955078125e-07*size, 1.5*size, 0.6999999284744263*size), (5.960464477539063e-08*size, 0.7229999899864197*size, -0.699999988079071*size), (-5.960464477539063e-08*size, 0.7229999899864197*size, 0.699999988079071*size), (1.1920928955078125e-07*size, -2.9802322387695312e-08*size, -0.699999988079071*size), (0.0*size, 2.9802322387695312e-08*size, 0.699999988079071*size), ]
        edges = [(1, 2), (0, 3), (0, 4), (3, 5), (4, 6), (1, 6), (5, 7), (2, 7)]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()

        mod = obj.modifiers.new("subsurf", 'SUBSURF')
        mod.levels = 2
        return obj
    else:
        return None


def create_foot_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    # Create hand widget
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(-0.6999998688697815*size, -0.5242648720741272*size, 0.0*size), (-0.7000001072883606*size, 1.2257349491119385*size, 0.0*size), (0.6999998688697815*size, 1.2257351875305176*size, 0.0*size), (0.7000001072883606*size, -0.5242648720741272*size, 0.0*size), (-0.6999998688697815*size, 0.2527350187301636*size, 0.0*size), (0.7000001072883606*size, 0.2527352571487427*size, 0.0*size), (-0.7000001072883606*size, 0.975735068321228*size, 0.0*size), (0.6999998688697815*size, 0.9757352471351624*size, 0.0*size), ]
        edges = [(1, 2), (0, 3), (0, 4), (3, 5), (4, 6), (1, 6), (5, 7), (2, 7), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()

        mod = obj.modifiers.new("subsurf", 'SUBSURF')
        mod.levels = 2
        return obj
    else:
        return None


def create_ballsocket_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(-0.050000108778476715*size, 0.779460072517395*size, -0.2224801927804947*size), (0.049999915063381195*size, 0.779460072517395*size, -0.22248023748397827*size), (0.09999985247850418*size, 0.6790841817855835*size, -0.3658318817615509*size), (-2.3089636158601934e-07*size, 0.5930476188659668*size, -0.488704651594162*size), (-0.10000013560056686*size, 0.6790841817855835*size, -0.3658317029476166*size), (0.04999981075525284*size, 0.6790841817855835*size, -0.36583182215690613*size), (-0.050000183284282684*size, 0.6790841817855835*size, -0.3658318519592285*size), (-0.3658319115638733*size, 0.6790841221809387*size, 0.05000019446015358*size), (-0.3658318817615509*size, 0.6790841221809387*size, -0.04999979957938194*size), (-0.36583176255226135*size, 0.6790841221809387*size, 0.10000018030405045*size), (-0.48870471119880676*size, 0.5930476188659668*size, 2.4472291215715813e-07*size), (-0.3658319413661957*size, 0.679084062576294*size, -0.0999998077750206*size), (-0.22248037159442902*size, 0.7794600129127502*size, -0.04999985918402672*size), (-0.22248034179210663*size, 0.7794600129127502*size, 0.05000016465783119*size), (0.3658319115638733*size, 0.6790841221809387*size, -0.05000000819563866*size), (0.3658319115638733*size, 0.6790841221809387*size, 0.05000000074505806*size), (0.36583179235458374*size, 0.6790841221809387*size, -0.09999998658895493*size), (0.4887046813964844*size, 0.5930476188659668*size, -3.8399143420519977e-08*size), (0.3658319413661957*size, 0.679084062576294*size, 0.10000000149011612*size), (0.050000034272670746*size, 0.7794599533081055*size, 0.2224804311990738*size), (-0.04999997466802597*size, 0.7794599533081055*size, 0.2224804311990738*size), (-0.09999992698431015*size, 0.679084062576294*size, 0.36583200097084045*size), (1.267315070663244e-07*size, 0.5930474996566772*size, 0.48870477080345154*size), (0.1000000610947609*size, 0.679084062576294*size, 0.3658318519592285*size), (-0.049999915063381195*size, 0.679084062576294*size, 0.3658319413661957*size), (0.05000007897615433*size, 0.679084062576294*size, 0.36583197116851807*size), (0.22248029708862305*size, 0.7794600129127502*size, 0.05000004544854164*size), (0.22248028218746185*size, 0.7794600129127502*size, -0.04999994859099388*size), (-4.752442350763886e-08*size, 0.8284152746200562*size, -0.1499999612569809*size), (-0.03882290795445442*size, 0.8284152746200562*size, -0.14488883316516876*size), (-0.07500004768371582*size, 0.8284152746200562*size, -0.12990377843379974*size), (-0.10606606304645538*size, 0.8284152746200562*size, -0.10606598109006882*size), (-0.1299038827419281*size, 0.8284152746200562*size, -0.07499996572732925*size), (-0.14488893747329712*size, 0.8284152746200562*size, -0.038822825998067856*size), (-0.15000006556510925*size, 0.8284152746200562*size, 2.4781975582754967e-08*size), (-0.1448889672756195*size, 0.8284152746200562*size, 0.038822878152132034*size), (-0.1299038827419281*size, 0.8284152746200562*size, 0.07500001043081284*size), (-0.10606609284877777*size, 0.8284152746200562*size, 0.1060660257935524*size), (-0.0750000923871994*size, 0.8284152746200562*size, 0.12990383803844452*size), (-0.038822952657938004*size, 0.8284152746200562*size, 0.14488889276981354*size), (-1.0593657862045802e-07*size, 0.8284152746200562*size, 0.15000005066394806*size), (0.03882275149226189*size, 0.8284152746200562*size, 0.14488892257213593*size), (0.07499989867210388*size, 0.8284152746200562*size, 0.1299038976430893*size), (0.10606591403484344*size, 0.8284152746200562*size, 0.10606611520051956*size), (0.12990373373031616*size, 0.8284152746200562*size, 0.0750000849366188*size), (0.14488881826400757*size, 0.8284152746200562*size, 0.038822952657938004*size), (0.1499999463558197*size, 0.8284152746200562*size, 1.0584351883835552e-07*size), (0.14488881826400757*size, 0.8284152746200562*size, -0.03882275149226189*size), (0.12990379333496094*size, 0.8284152746200562*size, -0.07499989122152328*size), (0.10606604814529419*size, 0.8284152746200562*size, -0.10606592148542404*size), (0.07500004768371582*size, 0.8284152746200562*size, -0.12990371882915497*size), (0.03882291540503502*size, 0.8284152746200562*size, -0.14488880336284637*size), ]
        edges = [(1, 0), (3, 2), (5, 2), (4, 3), (6, 4), (1, 5), (0, 6), (13, 7), (12, 8), (7, 9), (9, 10), (8, 11), (27, 14), (26, 15), (14, 16), (16, 17), (15, 18), (17, 18), (10, 11), (12, 13), (20, 19), (22, 21), (24, 21), (23, 22), (29, 28), (30, 29), (31, 30), (32, 31), (33, 32), (34, 33), (35, 34), (36, 35), (37, 36), (38, 37), (39, 38), (40, 39), (41, 40), (42, 41), (43, 42), (44, 43), (45, 44), (46, 45), (47, 46), (48, 47), (49, 48), (50, 49), (51, 50), (28, 51), (26, 27), (25, 23), (20, 24), (19, 25), ]
        faces = []

        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        return obj
    else:
        return None


def create_gear_widget(rig, bone_name, size=1.0, bone_transform_name=None):
    obj = create_widget(rig, bone_name, bone_transform_name)
    if obj is not None:
        verts = [(0.11251477152109146*size, -8.06030631128607e-10*size, 0.01843983121216297*size), (0.018439611420035362*size, -4.918176976786981e-09*size, 0.11251477152109146*size), (0.09270283579826355*size, -8.06030631128607e-10*size, 0.01843983121216297*size), (0.08732416480779648*size, -1.5810827092010982e-09*size, 0.03617095574736595*size), (0.07858962565660477*size, -2.295374557093055e-09*size, 0.05251204967498779*size), (0.052511852234601974*size, -3.4352671818282943e-09*size, 0.07858975231647491*size), (0.03617073595523834*size, -3.8170644423018985e-09*size, 0.08732425421476364*size), (0.018439611420035362*size, -4.0521714872454595e-09*size, 0.09270287305116653*size), (0.09402976930141449*size, -2.937612375575327e-09*size, 0.06720473617315292*size), (0.08150213211774826*size, -3.513068946858766e-09*size, 0.08036965131759644*size), (0.06872907280921936*size, -4.0997978345558295e-09*size, 0.09379243850708008*size), (-0.1125146746635437*size, -8.06030631128607e-10*size, 0.01843983121216297*size), (-0.01843959279358387*size, -4.918176976786981e-09*size, 0.11251477152109146*size), (1.078764189088588e-08*size, -4.918176976786981e-09*size, 0.11251477152109146*size), (-0.09270282834768295*size, -8.06030631128607e-10*size, 0.01843983121216297*size), (-0.0873241126537323*size, -1.5810827092010982e-09*size, 0.03617095574736595*size), (-0.07858961820602417*size, -2.295374557093055e-09*size, 0.05251204967498779*size), (-0.05251181498169899*size, -3.4352671818282943e-09*size, 0.07858975231647491*size), (-0.036170728504657745*size, -3.8170644423018985e-09*size, 0.08732425421476364*size), (-0.01843959279358387*size, -4.0521714872454595e-09*size, 0.09270287305116653*size), (-0.09402971714735031*size, -2.937612375575327e-09*size, 0.06720473617315292*size), (-0.08150212466716766*size, -3.513068946858766e-09*size, 0.08036965131759644*size), (-0.06872902065515518*size, -4.0997978345558295e-09*size, 0.09379243850708008*size), (0.11251477152109146*size, 8.06031352773573e-10*size, -0.018439847975969315*size), (0.11251477152109146*size, 3.801315519479033e-16*size, -8.696396491814085e-09*size), (0.018439611420035362*size, 4.918176532697771e-09*size, -0.11251476407051086*size), (0.09270283579826355*size, 8.06031352773573e-10*size, -0.018439847975969315*size), (0.08732416480779648*size, 1.5810828202234006e-09*size, -0.03617095947265625*size), (0.07858962565660477*size, 2.29537477913766e-09*size, -0.05251205340027809*size), (0.052511852234601974*size, 3.435267403872899e-09*size, -0.07858975976705551*size), (0.03617073595523834*size, 3.8170644423018985e-09*size, -0.08732425421476364*size), (0.018439611420035362*size, 4.0521714872454595e-09*size, -0.09270287305116653*size), (0.09402976930141449*size, 2.937614596021376e-09*size, -0.0672047883272171*size), (0.08150213211774826*size, 3.513068946858766e-09*size, -0.08036965131759644*size), (0.06872907280921936*size, 4.099800055001879e-09*size, -0.09379249066114426*size), (-0.1125146746635437*size, 8.06031352773573e-10*size, -0.018439847975969315*size), (-0.1125146746635437*size, 3.801315519479033e-16*size, -8.696396491814085e-09*size), (-0.01843959279358387*size, 4.918176532697771e-09*size, -0.11251476407051086*size), (1.078764189088588e-08*size, 4.918176532697771e-09*size, -0.11251476407051086*size), (-0.09270282834768295*size, 8.06031352773573e-10*size, -0.018439847975969315*size), (-0.0873241126537323*size, 1.5810828202234006e-09*size, -0.03617095947265625*size), (-0.07858961820602417*size, 2.29537477913766e-09*size, -0.05251205340027809*size), (-0.05251181498169899*size, 3.435267403872899e-09*size, -0.07858975976705551*size), (-0.036170728504657745*size, 3.8170644423018985e-09*size, -0.08732425421476364*size), (-0.01843959279358387*size, 4.0521714872454595e-09*size, -0.09270287305116653*size), (-0.09402971714735031*size, 2.937614596021376e-09*size, -0.0672047883272171*size), (-0.08150212466716766*size, 3.513068946858766e-09*size, -0.08036965131759644*size), (-0.06872902065515518*size, 4.099800055001879e-09*size, -0.09379249066114426*size), ]
        edges = [(0, 2), (0, 24), (7, 1), (13, 1), (3, 2), (4, 3), (6, 5), (7, 6), (9, 8), (10, 9), (10, 5), (4, 8), (11, 14), (11, 36), (19, 12), (13, 12), (15, 14), (16, 15), (18, 17), (19, 18), (21, 20), (22, 21), (22, 17), (16, 20), (23, 26), (23, 24), (31, 25), (38, 25), (27, 26), (28, 27), (30, 29), (31, 30), (33, 32), (34, 33), (34, 29), (28, 32), (35, 39), (35, 36), (44, 37), (38, 37), (40, 39), (41, 40), (43, 42), (44, 43), (46, 45), (47, 46), (47, 42), (41, 45), ]
        faces = []
        mesh = obj.data
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        mesh.update()
        return obj
    else:
        return None


def create_widget_from_cluster(rig, bone_name, cluster, size=1.0, bone_transform_name=None):
    """

    :param rig:
    :param bone_name:
    :param cluster: point cloud
    :type cluster: list(Vector)
    :param size:
    :param direction:
    :param bone_transform_name:
    :return:
    """
    obj = create_widget(rig, bone_name, bone_transform_name)

    if obj is not None:
        ctrl_x = rig.pose.bones[bone_name].x_axis
        ctrl_y = rig.pose.bones[bone_name].y_axis

        cluster = get_cluster_projection(cluster, ctrl_x, ctrl_y)

        size = 1/rig.pose.bones[bone_name].length

        [verts, edges] = get_2d_border(cluster, size=size)

        mesh = obj.data
        mesh.from_pydata(verts, edges, [])
        mesh.validate()
        mesh.update()
        return obj
    else:
        return None


def get_cluster_projection(cluster, x_axis, y_axis):

    new_cluster = []
    cluster_sum = Vector((0, 0, 0))

    for point in cluster:
        cluster_sum += point

    cluster_center = cluster_sum / len(cluster)

    for point in cluster:
        _point = point - cluster_center
        new_point = Vector((_point.dot(x_axis), _point.dot(y_axis), 0))
        new_cluster.append(new_point)

    return new_cluster


def get_cluster_span(cluster):

    x_span = 0
    y_span = 0
    z_span = 0

    for point in cluster:
        x_span = max(x_span, abs(point.x))
        y_span = max(y_span, abs(point.y))
        z_span = max(z_span, abs(point.z))

    return [x_span, y_span, z_span]


def get_2d_border(cluster, max_points=None, size=1.0, double=True):

    if not max_points:
        max_points = 2*len(cluster)

    angle_step = 2*pi/max_points

    x_axis = Vector((1, 0))

    points = [(-1, 0)] * max_points

    for i, point in enumerate(cluster):
        angle = point.to_2d().angle_signed(x_axis)
        angle = angle if angle >= 0 else 2*pi + angle
        index = int(round(angle/angle_step, 2)) % len(points)
        if point.magnitude > points[index][1]:
            points[index] = (i, point.magnitude)

    points = [p for p in points if p[0] >= 0]

    verts = []
    edges = []

    if len(points) == 1:
        return verts, edges

    if len(points) == 2:
        i0 = points[0][0]
        i1 = points[1][0]
        # displ = (cluster[i1] - cluster[i0]).magnitude * 0.05
        displ = 0.1 / size
        angle = cluster[i0].to_2d().angle(x_axis)
        displ_vect = displ * Vector((sin(angle), -cos(angle), 0))

        verts = [cluster[i0] + displ_vect, cluster[i1] + displ_vect, cluster[i0]
                 - displ_vect, cluster[i1] - displ_vect]
        verts = [size*v for v in verts]
        edges = [(0, 1), (2, 3)]
        return verts, edges

    j = 0
    for p in points:
        if p[0] >= 0:
            vert = size*cluster[p[0]]
            verts.append(vert.to_tuple())
            edges.append(((j+1) % len(points), j))
            j += 1

    if double:
        for p in points:
            if p[0] >= 0:
                vert = size * 1.1 * cluster[p[0]]
                verts.append(vert.to_tuple())
                edges.append(((j + 1) % len(points) + len(points), j))
                j += 1

    return verts, edges
