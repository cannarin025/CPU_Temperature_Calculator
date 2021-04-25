class BoundaryRef:
    def __init__(self, target, x_offset, self_mount_y, target_mount_y, self_boundary_start = None, self_boundary_end = None):
        self.__target = target
        self.__self_boundary_start = self_boundary_start
        self.__self_boundary_end = self_boundary_end
        self.__x_offset = int(x_offset)
        self.__self_mount_y = self_mount_y
        self.__target_mount_y = target_mount_y

    def get_target(self):
        return self.__target

    def get_self_mount_y(self):
        return self.__self_mount_y

    def get_target_mount_y(self):
        return self.__target_mount_y

    def get_self_boundary_start(self):
        return self.__self_boundary_start

    def get_self_boundary_end(self):
        return self.__self_boundary_end

    def set_self_boundary_start(self, start):
        self.__self_boundary_start = start

    def set_self_boundary_end(self, end):
        self.__self_boundary_end = end

    def convert_coordinate(self, x):
        return x - self.__x_offset

