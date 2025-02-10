class Box:
    def __init__(self, points, number):
        self.points=points
        self.number = number
        self.cal_center(points)
    def cal_center(self, points):
        mx = 0
        my = 0
        for point in points:
            mx += point[0]
            my += point[1]
        self.center = (mx // len(points), my // len(points))