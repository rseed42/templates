class Camera(object):
    def __init__(self, eye=np.array([0,0,-1],'f'), target=np.zeros(3,'f'),
                 up = np.array([0,0,1])):
        self.eye = eye
        self.target = target
        self.up = up

    def normalize(self, x):
        norm = sum(x*x)**0.5
        if norm == 0: return np.zeros(3, 'f')
        return x/norm

    def view_matrix(self):
        """ eye, target, up are 3-vectors in world space
        """
        # Check the optimization later
        zaxis = self.normalize(self.eye - self.target)
        xaxis = self.normalize(np.cross(self.up, zaxis))
        yaxis = np.cross(zaxis, xaxis)
        orientation = np.identity(4, 'f')
        orientation[0:3,0] = xaxis
        orientation[0:3,1] = yaxis
        orientation[0:3,2] = zaxis
        translation = np.identity(4, 'f')
        translation[3,0:3] = -self.eye
        return np.dot(orientation, translation)
