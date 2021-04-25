class SurfaceCell:
    def __init__(self, coordinates: tuple, edge_count: int):
        self.coordinates = coordinates
        self.exposed_edges = edge_count
