import sys
class Game:
    #Hàm này kiểm tra xem giá trị của một ký tự trong ma trận trò chơi có hợp lệ hay không
    def is_valid_value(self,char): #các phép toán ma trận
        if ( char == ' ' or #sàn
            char == '#' or #tường
            char == '@' or #nhân vật trên sàn
            char == '.' or #đích
            char == '*' or #hộp trên bến tàu
            char == '$' or #hộp
            char == '+' ): #nhân vật trên bến tàu
            return True
        else:
            return False

    def __init__(self,matrix):
        self.heuristic = 0 #Biến lưu trữ giá trị heuristic để sử dụng trong thuật toán tìm kiếm.
        self.pathSol = "" #Chuỗi lưu trữ đường đi giải của trò chơi.
        self.stack = [] #Ngăn xếp để lưu các di chuyển đã thực hiện, dùng cho tính năng undo.
        self.matrix = matrix #Ma trận lưu trạng thái của bản đồ trò chơi.

    def __lt__(self, other):
        return self.heuristic < other.heuristic #So sánh hai đối tượng Game dựa trên giá trị heuristic

    def load_size(self): #Trả về kích thước màn hình trò chơi dựa trên kích thước ma trận
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self): #Trả về ma trận trò chơi hiện tại.
        return self.matrix

    def print_matrix(self): #In ma trận ra console.
        for row in self.matrix:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def get_content(self,x,y):  #Lấy nội dung tại vị trí (x, y) trong ma trận.
        return self.matrix[y][x]

    def set_content(self,x,y,content):  #Đặt nội dung cho vị trí (x, y) nếu giá trị hợp lệ (kiểm tra bằng is_valid_value).
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print("ERROR: Value '"+content+"' to be added is not valid")

    def worker(self):   #Tìm vị trí hiện tại của nhân vật (@ hoặc +) trên bản đồ.
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def box_list(self): #Trả về danh sách vị trí của tất cả các hộp ($) trên bản đồ.
        x = 0
        y = 0
        boxList = []
        for row in self.matrix:
            for pos in row:
                if pos == '$':
                    boxList.append((x,y))
                x = x + 1
            y = y + 1
            x = 0
        return boxList

    def dock_list(self):    #Trả về danh sách vị trí của tất cả các đích (.) trên bản đồ.
        x = 0
        y = 0
        dockList = []
        for row in self.matrix:
            for pos in row:
                if pos == '.':
                    dockList.append((x,y))
                x = x + 1
            y = y + 1
            x = 0
        return dockList

    def can_move(self,x,y): # Kiểm tra xem nhân vật có thể di chuyển đến vị trí (x, y) hay không
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y) not in ['#','*','$']

    def next(self,x,y): #Lấy giá trị tại vị trí kế tiếp mà nhân vật định di chuyển.
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def can_push(self,x,y): #Kiểm tra xem nhân vật có thể đẩy hộp (ký tự * hoặc $) từ vị trí hiện tại đến vị trí mới hay không.
        return (self.next(x,y) in ['*','$'] and self.next(x+x,y+y) in [' ','.'])

    def is_completed(self): #Kiểm tra xem trò chơi đã hoàn thành hay chưa (không còn hộp nào chưa được đẩy vào đích).
        for row in self.matrix:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self,x,y,a,b): #Di chuyển hộp từ vị trí (x, y) đến vị trí (x+a, y+b).
#        (x,y) -> move to do
#        (a,b) -> box to move
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        if current_box == '$' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,'.')
        elif current_box == '*' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,'.')

    def unmove(self):   #Undo di chuyển cuối cùng
        if len(self.stack) > 0:
            movement = self.stack.pop()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
                self.move_box(current[0]+movement[0],current[1]+movement[1],movement[0] * -1,movement[1] * -1)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def move(self,x,y,save):
        if self.can_move(x,y):
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
                if save: self.stack.append((x,y,False))
            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
                if save: self.stack.append((x,y,False))
            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
                if save: self.stack.append((x,y,False))
            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
                if save: self.stack.append((x,y,False))
        elif self.can_push(x,y):
            current = self.worker()
            future = self.next(x,y)
            future_box = self.next(x+x,y+y)
            if current[2] == '@' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
