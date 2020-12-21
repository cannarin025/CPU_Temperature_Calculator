class BoundaryRef:
    def __init__(self, object, x_offset, self_mount_y, object_mount_y, self_boundary_start = None, self_boundary_end = None):
        self._object = object
        self._self_boundary_start = self_boundary_start
        self._self_boundary_end = self_boundary_end
        self._x_offset = int(x_offset)
        self._self_mount_y = self_mount_y
        self._object_mount_y = object_mount_y

    def get_object(self):
        return self._object

    def get_self_mount_y(self):
        return self._self_mount_y

    def get_object_mount_y(self):
        return self._object_mount_y

    def get_self_boundary_start(self):
        return self._self_boundary_start

    def get_self_boundary_end(self):
        return self._self_boundary_end

    def set_self_boundary_start(self, start):
        self._self_boundary_start = start

    def set_self_boundary_end(self, end):
        self._self_boundary_end = end



    def convert_coordinate(self, x):
        return x - self._x_offset

