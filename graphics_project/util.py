def orthographic(self, width, height, zn, zf):
    mat = np.identity(4, 'f')
    # invert
    mat[0,0] = 2/width
    mat[1,1] = 2/height
    mat[2,2] = -2/(zf-zn)
    mat[2,3] = -(zf+zn)/(zf-zn)
    return mat.T
    return mat

def frustrum2(self, phi, zn, zf):
    """
    """
    phi = np.deg2rad(phi)
    aspect = float(WND_SIZE[0]/WND_SIZE[1])
    mat = np.identity(4,'f')
    mat[0,0] = 1./np.tan(phi)
    mat[1,1] = aspect/np.tan(phi)
    mat[2,2] = (zf+zn)/(zf-zn)
    mat[2,3] = -(2*zf*zn)/(zf-zn)
    mat[3,2] = 1
    mat[3,3] = 0
    return mat.T
    return mat

def frustrum(self, width, height, zn, zf):
    """
    """
    mat = np.identity(4, 'f')
    mat[0,0] = 2*zn/width
    mat[1,1] = 2*zn/height
    mat[2,2] = -(zf+zn)/(zf-zn)
    mat[2,3] = (2*zf*zn)/(zf-zn)
    mat[3,2] = -1.0
    mat[3,3] = 0.0
    return mat.T
