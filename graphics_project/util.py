import OpenGL.GL as gl
import numpy as np
#-------------------------------------------------------------------------------
def glinfo():
    print gl.glGetString(gl.GL_VERSION)
    print gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)

def orthographic(left, right, bottom, top, near, far):
    """ Orthographic projection
    """
    mat = np.identity(4, 'f')
    mat[0,0] = 2/float(right-left)
    mat[1,1] = 2/float(top-bottom)
    mat[2,2] = 2/float(near-far)
    mat[0,3] = float(left+right)/(left-right)
    mat[1,3] = float(bottom+top)/(bottom-top)
    mat[2,3] = float(near+far)/(far-near)
    return mat

# To be fixed:
#def frustrum2(phi, zn, zf):
#    """
#    """
#    phi = np.deg2rad(phi)
#    aspect = float(WND_SIZE[0]/WND_SIZE[1])
#    mat = np.identity(4,'f')
#    mat[0,0] = 1./np.tan(phi)
#    mat[1,1] = aspect/np.tan(phi)
#    mat[2,2] = (zf+zn)/(zf-zn)
#    mat[2,3] = -(2*zf*zn)/(zf-zn)
#    mat[3,2] = 1
#    mat[3,3] = 0
#    return mat
#
def frustrum(left, right, bottom, top, near, far):
    """
    """
    mat = np.identity(4, 'f')
    mat[0,0] = 2*near/float(right-left)
    mat[1,1] = 2*near/float(top - bottom)
    mat[2,2] = float(near+far)/(near-far)
    mat[2,3] = (2*near*far)/float(near-far)
    mat[3,2] = -1.0
    mat[3,3] = 0.0
    return mat
