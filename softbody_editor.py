import pygame
import sys, os, math, json

# initialize, clock
pygame.init()
clock = pygame.time.Clock()
FPS = 60

# screen dimensions/aspect ratios
display_info = pygame.display.Info()
display_width = display_info.current_w
display_height = display_info.current_h
aspect_ratio = display_width / display_height

# internal game resolution
display_mode = (int(aspect_ratio*360),360)
display = pygame.Surface(display_mode)
pygame.display.set_caption("SOFTBODY EDITOR (using adjacency list)")

screen_mode = (int(aspect_ratio*display_height/2),int(display_height/2))
screen = pygame.display.set_mode(screen_mode, pygame.RESIZABLE)

# ----------------- FILE PATH ----------------- #
file_name = "cloth2"
file_path = f"softbody_data/{file_name}.json"

# Grid class: creating and updating a Grid object will render a grid onto the display.
class Grid:
    def __init__(self, unit_length, editor):
        self.unit_length = unit_length
        self.editor = editor

    # draw the gridlines vertically and horizontally, separately
    def draw_grid(self):
        # Visible world bounds (left, top, right, bottom)
        view_left = self.editor.scroll[0]
        view_right = self.editor.scroll[0] + display.get_width()
        
        view_top = self.editor.scroll[1]
        view_bottom = self.editor.scroll[1] + display.get_height()

        # integer ranges of grid lines
        # vertical lines: x = k*unit_length
        vertical_start = math.floor(view_left/self.unit_length)
        vertical_end = math.ceil(view_right/self.unit_length)
        for i in range(vertical_start, vertical_end):
            x_pos = i*self.unit_length - self.editor.scroll[0]
            pygame.draw.line(display, (100,100,100), (x_pos, 0), (x_pos, display.get_height()))

        # horizontal lines: y = m*unit_length
        horizontal_start = math.floor(view_top/self.unit_length)
        horizontal_end = math.ceil(view_bottom/self.unit_length)
        for i in range(horizontal_start, horizontal_end):
            y_pos = i*self.unit_length - self.editor.scroll[1]
            pygame.draw.line(display, (50,50,50), (0, y_pos), (display.get_width(), y_pos))

# Editor class
class Editor:
    def __init__(self):
        self.movement = [False,False,False,False] # False: 0, True: 1
        
        # actions
        self.left_clicking = False
        self.right_clicking = False
        self.prev_left_clicking = self.left_clicking
        self.mouse_grid_pos = [0,0]
        self.hold_spring = False
        
        # conditions
        self.action = 'node'
        self.is_fixed = False
        self.is_border = False
        self.scroll_factor = 5
        self.colors = {
          'node': (0,255,255),
          'spring': (150,100,255)  
        }

        # grid size, Grid
        self.tile_size = 24 
        self.grid = Grid(self.tile_size, self)
        # text
        self.font = pygame.font.Font(None, 25)
        # scroll: controlled by WASD or arrow keys
        self.scroll = [0,0] 
        # used for connecting two nodes with a spring.
        self.connect = [None, None]

        # default template data
        self.template_data = {
            "node_data": {},
            "adjacency_list": {}
        }

        self.load_data()
        
        ###
        # identify next unique key
        largest = 0
        for i in self.node_data:
            node = self.node_data[i]
            if node['id'] > largest:
                largest = node['id']
        self.new_node_id = largest + 1

        # all grid coordinates that are already occupied
        self.has_node = []
        for i in self.node_data:
            self.has_node.append(self.node_data[i]['pos'])
        ###

    # dumping current map of nodes and springs (and their states) into JSON file.
    def save(self, path):
        with open(path, "w") as f:
            json.dump(
                {
                    "node_data": self.node_data,
                    "adjacency_list": self.adjacency_list
                },
                f,
                indent=2
            )

    # load in existing SoftBody JSON data
    def parse_saved_data(self, path):
        with open(path, 'r') as f:
            softbody_data = json.load(f)
        self.node_data = softbody_data['node_data']
        self.adjacency_list = softbody_data['adjacency_list']
        # ensure adjacency lists contain strings and remove dangling references
        for i in self.adjacency_list:
            adj = self.adjacency_list[i]['adjacency']
            self.adjacency_list[i]['adjacency'] = [str(x) for x in adj if str(x) in self.node_data]

    def load_data(self):
        # load in data if path already exists
        if os.path.exists(file_path):
            try:
                self.parse_saved_data(file_path)
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
                self.node_data = {}
                self.adjacency_list = {}

        # create new data file if there is no data file associated with the path name.
        else:
            # ensure directory exists
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(file_path, "w") as json_file:
                json.dump(self.template_data, json_file)
            print(f"{file_path} did not exist: created with template data.")
            # load the newly created file so attributes are initialized
            try:
                self.parse_saved_data(file_path)

            except Exception as e:
                print(f"Failed to load newly created {file_path}: {e}")
                self.node_data = {}
                self.adjacency_list = {}

    # render all (onscreen) nodes
    def render_nodes(self, offset):
        for loc in self.node_data:
            node = self.node_data[loc]
            pygame.draw.circle(display, (0,255,255), (node["pos"][0]*self.tile_size - offset[0], node["pos"][1]*self.tile_size - offset[1]), 5)
            # node tags: border (B) and fixed (F)
            if node['fixed'] == True:
                display.blit(self.font.render("F", False, (255, 0, 0)), (self.tile_size*node['pos'][0]-offset[0],self.tile_size*node['pos'][1]-offset[1]))
            if node['border'] == True:
                display.blit(self.font.render("B", False, (0, 255, 0)), (self.tile_size*node['pos'][0]-offset[0]+6,self.tile_size*node['pos'][1]-offset[1]))

    # render all springs: use adjacency
    def render_springs(self, offset):
        for i in self.adjacency_list:
            id_list = self.adjacency_list[i]['adjacency']
            for node_id in id_list:
                if int(node_id) > int(i): # prevents duplicate springs
                    node1_pos = self.node_data[str(i)]['pos']
                    node2_pos = self.node_data[str(node_id)]['pos']
                    pygame.draw.line(display, (150,100,255), (self.tile_size*node1_pos[0]-offset[0], self.tile_size*node1_pos[1]-offset[1]), (self.tile_size*node2_pos[0]-offset[0], self.tile_size*node2_pos[1]-offset[1]), 2)

    # adding nodes
    def add_node(self):
        if self.left_clicking and not self.prev_left_clicking:
            if self.action == 'node' and self.mouse_grid_pos not in self.has_node:
                self.node_data[str(self.new_node_id)] = {
                    'id': self.new_node_id,
                    'pos': self.mouse_grid_pos,
                    'fixed': self.is_fixed,
                    'border': self.is_border
                }
                self.adjacency_list[str(self.new_node_id)] = {
                    'adjacency': []
                }
                self.new_node_id += 1
                self.has_node.append(self.mouse_grid_pos)

    # removing nodes            
    def remove_node(self):
        if self.right_clicking and self.action == 'node':
            delete_id = None  # string
            for i in self.node_data:
                if self.node_data[i]['pos'] == self.mouse_grid_pos:
                    delete_id = i
                    break
            if delete_id != None:
                self.has_node.remove(self.node_data[delete_id]['pos'])
                del self.node_data[delete_id]
                del self.adjacency_list[delete_id]
                # also delete occurences in other lists
                for i in self.adjacency_list:
                    node_ids = self.adjacency_list[i]["adjacency"]
                    if delete_id in node_ids:
                        node_ids.remove(delete_id)

    # create a spring between two nodes
    def add_spring(self):
        for pos in self.node_data:
            node = self.node_data[pos]
            if self.hold_spring == False and self.left_clicking and self.action == 'spring' and (self.mouse_grid_pos == node['pos']):
                self.hold_spring = True
                self.connect[0] = node['id']

    # remove a spring between two nodes
    def remove_spring(self):
        for pos in self.node_data:
            node = self.node_data[pos]
            if self.hold_spring == False and self.right_clicking and self.action == 'spring' and (self.mouse_grid_pos == node['pos']):
                self.hold_spring = True
                self.connect[0] = node['id']

    # main loop
    def main(self):
        while True:
            # render ratio
            window_width, window_height = pygame.display.get_window_size()
            screen_display_ratio_x = display.get_width()/window_width
            screen_display_ratio_y = display.get_height()/window_height
            
            # mouse pos
            mouse_coords = pygame.mouse.get_pos()
            mouse_coords = (list(mouse_coords))

            mouse_coords[0] *= screen_display_ratio_x
            mouse_coords[1] *= screen_display_ratio_y

            # mouse grid coordinates
            self.mouse_grid_pos = [
                int(mouse_coords[0] + self.scroll[0]) // self.tile_size,
                int(mouse_coords[1] + self.scroll[1]) // self.tile_size
            ]

            # scroll
            self.scroll[0] += (self.movement[1] - self.movement[0])*self.scroll_factor
            self.scroll[1] += (self.movement[3] - self.movement[2])*self.scroll_factor
            self.scroll = list(self.scroll)

            # rendering
            # reset display
            display.fill((10,10,20))
            # rendering reference lines and points and nodes/springs
            self.grid.draw_grid()
            # borders between positive and negative
            pygame.draw.line(display, (255,0,0), (screen.get_width()-self.scroll[0], max(2, 0-self.scroll[1])), (0-self.scroll[0], max(2, 0-self.scroll[1])), 1)
            pygame.draw.line(display, (255,0,0), (max(2, 0-self.scroll[0]),screen.get_height()-self.scroll[1]), (max(2, 0-self.scroll[0]), 0-self.scroll[1]), 1)

            # render nodes and springs
            self.render_springs([self.scroll[0]-self.grid.unit_length/2, self.scroll[1]-self.grid.unit_length/2])
            self.render_nodes([self.scroll[0]-self.grid.unit_length/2, self.scroll[1]-self.grid.unit_length/2])

            # mouse pos and grid pos circles         
            #pygame.draw.circle(display, (0,0,255), mouse_coords, 5)
            pygame.draw.circle(display, self.colors[self.action], (self.mouse_grid_pos[0]*self.tile_size + self.tile_size/2 - self.scroll[0], self.mouse_grid_pos[1]*self.tile_size + self.tile_size/2 - self.scroll[1]), 5)
            # circle at origin
            #pygame.draw.circle(display, (0,255,0), (0-self.scroll[0], 0-self.scroll[1]), 3)
            # line connecting both
            #pygame.draw.line(display, (255,255,255), (mouse_coords[0], mouse_coords[1]), (0-self.scroll[0], 0-self.scroll[1]), 1)

            # rendering conditions (text)
            display.blit(self.font.render(f"1;2: action: {self.action}", False, (255, 150, 100)), (10,10))
            display.blit(self.font.render(f"3: fixed: {str(self.is_fixed)}", False, (255, 0, 0)), (10,30))
            display.blit(self.font.render(f"4: border: {str(self.is_border)}", False, (0, 255, 0)), (10,50))
            display.blit(self.font.render(f"coordiantes: {str(self.mouse_grid_pos)}", False, (255,255,255)), (10,70))
            #
            display.blit(self.font.render(file_name, False, (255,255,255)), (10,display.get_height() - 50))
            display.blit(self.font.render("save: p", False, (255,255,255)), (10,display.get_height() - 30))

            # node: add and remove
            self.add_node()
            self.remove_node()
            # spring: add and remove
            self.add_spring()
            self.remove_spring()
            
            # eventhandler
            self.prev_left_clicking = self.left_clicking
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_clicking = True
                    if event.button == 3:
                        self.right_clicking = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_clicking = False
                        for pos in self.node_data:
                            node = self.node_data[pos]
                            # on mousebutton UP, add spring to data
                            if self.hold_spring == True and self.action == 'spring' and (self.mouse_grid_pos == node['pos']):
                                self.connect[1] = node['id']
                                print(self.adjacency_list)
                                # cannot easily make adjacency lists sets instead: we don't want duplicate items in list, but JSON does not have sets. Just check if duplicate instead.
                                a = str(self.connect[0])
                                b = str(self.connect[1])
                                if b not in self.adjacency_list[a]['adjacency']:
                                    self.adjacency_list[a]['adjacency'].append(b)
                                if a not in self.adjacency_list[b]['adjacency']:
                                    self.adjacency_list[b]['adjacency'].append(a)
                                # reset
                                self.connect = [None, None]
                                self.hold_spring = False

                    if event.button == 3:
                        self.right_clicking = False
                        for pos in self.node_data:
                            node = self.node_data[pos]
                            # on mousebutton UP, add spring to data
                            if self.hold_spring == True and self.action == 'spring' and (self.mouse_grid_pos == node['pos']):
                                self.connect[1] = node['id']
                                a = str(self.connect[0])
                                b = str(self.connect[1])
                                # delete
                                self.adjacency_list[a]['adjacency'].remove(b) if b in self.adjacency_list[a]['adjacency'] else None
                                self.adjacency_list[b]['adjacency'].remove(a) if a in self.adjacency_list[b]['adjacency'] else None

                                # reset
                                self.connect = [None, None]
                                self.hold_spring = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key == pygame.K_1:
                        self.action = 'node'
                    if event.key == pygame.K_2:
                        self.action = 'spring'
                    if event.key == pygame.K_3:
                        if self.is_fixed == False:
                            self.is_fixed = True
                        elif self.is_fixed == True:
                            self.is_fixed = False
                    if event.key == pygame.K_4:
                        if self.is_border == False:
                            self.is_border = True
                        elif self.is_border == True:
                            self.is_border = False
                        
                    # save data of current node and spring configuration
                    if event.key == pygame.K_p:
                        self.save(file_path)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.movement[3] = False
                        
            # pygame update
            screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
            pygame.display.update()
            clock.tick(FPS)

Editor().main()