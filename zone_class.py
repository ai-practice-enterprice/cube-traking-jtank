class Zone:
    def __init__(self, points, number,row,col):#row horizontaal(x) col verticaal(y)
        self.points=points
        self.number = number
        self.row = row
        self.col = col
        self.corect_boxes=[]
        self.incorect_boxes=[]
        self.cal_subzones(points, row, col)
    def cal_subzones(self, points,row,col):
        sqare_x=round(abs(points[0][0]-points[1][0])/row)
        sqare_y=round(abs(points[0][1]-points[2][1])/col)
        self.subzones=[]
        xy=(points[0])
        for sqares_y in range(col):
            for sqares_x in range(row):
                sqare=[]
                sqare.append(xy)
                sqare.append((xy[0]+sqare_x,xy[1]))
                sqare.append((xy[0]+sqare_x,xy[1]+sqare_y))
                sqare.append((xy[0],xy[1]+sqare_y))
                self.subzones.append(sqare)
                xy=(xy[0]+sqare_x,xy[1])
            xy=(points[0][0],xy[1]+sqare_y)
    def boxes_in_zone(self,boxes):
        self.corect_boxes=[]
        self.incorect_boxes=[]
        for index, sub_zone in enumerate(self.subzones):
            in_zone=False
            for box in boxes:
                point=box.center
                if sub_zone[0][0] <= point[0] <= sub_zone[1][0] and sub_zone[0][1] <= point[1] <= sub_zone[2][1]:
                    in_zone = True
                    break
            if in_zone:
                if box.number==self.number:
                    self.corect_boxes.append((box,index))
                else:
                    self.incorect_boxes.append((box,index))
    def get_center_subzone(self,index):
        subzone = self.subzones[index]
        center_x = (subzone[0][0] + subzone[2][0]) // 2
        center_y = (subzone[0][1] + subzone[2][1]) // 2
        return (center_x, center_y)