class ShapeManager:
    def __init__(self):
        self.shapes = []

    def create_shape(self, shape_data):
        shape = {'id': len(self.shapes) + 1, 'data': shape_data}
        self.shapes.append(shape)
        return shape
