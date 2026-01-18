import pygame
import math, json

# Node class
class Node:
    # friction: horizontal and vertical movement are multiplied by friction. A lower friction will restrict movement. Friction should not exceed 1, or node velocities will increase infinitely.
    friction = 0.99
    mass = 1
    def __init__(self, render_surf, x, y, gridpos, fixed, border, id):
        self.render_surf = render_surf
        # (x,y) GRID positions. Actual pixel positions based on the assigned spacing in the SoftBody object it is part of.
        self.x = x
        self.y = y
        self.gridpos = gridpos

        # fixed and border property
        # fixed nodes are not affected by external forces. They remain where they are initialized.
        # border nodes are used to create the vertices and sides of the polygon that will be filled with solid color.
        # a node can be fixed, border, both, or none.
        self.fixed = fixed
        self.border = border
        
        # integer value
        self.id = id 

        self.vx = 0
        self.vy = 0

    def render(self):
        color = (255,255,255)
        pygame.draw.circle(self.render_surf, color, (self.x, self.y), 2)

    def apply_force(self, fx, fy):
        self.vx += fx/Node.mass
        self.vy += fy/Node.mass

    # updates node velocity as a response to force, and positions as a result.
    def update(self, wind, gravity):
        if self.fixed:
            return
        
        # gravity
        self.vy += gravity
        # wind. take sin(wind + self.x/100) so softbodies do not "sway" in the wind in unison.
        self.vx += 0.1*math.sin(wind+self.x/200)
        # friction
        self.vx *= Node.friction
        self.vy *= Node.friction

        # update current node positions
        self.x += self.vx
        self.y += self.vy

# Spring class: connects Node objects.
class Spring:
    k = 0.5 # spring constant
    def __init__(self, render_surf, node1, node2, length):
        self.render_surf = render_surf
        # A spring connects two nodes.
        self.node1 = node1
        self.node2 = node2
        # default length between nodes and the width of the spring.
        self.length = length
        self.linewidth = 1
    
    def update(self):
        dx = self.node2.x-self.node1.x
        dy = self.node2.y-self.node1.y
        distance = math.sqrt(dx**2+dy**2)
        if distance == 0:
            return
        
        # Hooke's law : F = -k*x
        difference = distance-self.length
        forceX = (dx/distance)*difference*Spring.k
        forceY = (dy/distance)*difference*Spring.k

        # Apply forces to nodes
        self.node1.apply_force(forceX, forceY)
        self.node2.apply_force(-forceX, -forceY)

    def render(self, color):
        pygame.draw.line(self.render_surf, color, (self.node1.x, self.node1.y), (self.node2.x, self.node2.y), self.linewidth)

# "wrapper" for pygame polygon object
class Polygon:
    def __init__(self):
        self.nodes = [] # list of Node objects

    def fill(self, surface, color):
        pygame.draw.polygon(surface, color, self.get_node_loc())

    def add_node(self, n):
        self.nodes.append(n)

    def get_node_loc(self):
        # in order of trace, a list of tuples
        node_locs = []
        for node in self.nodes:
            loc = (node.x, node.y)
            node_locs.append(loc)
        return node_locs

# SoftBody object: a network of nodes connected with springs.
class SoftBody:
    def __init__(self, render_surf, pos, spacing, color, directory):
        self.render_surf = render_surf
        self.x, self.y = pos[0], pos[1]
        # spacing between nodes: for different sized (but equally proportioned) entities
        self.spacing = spacing
        self.color = color
        # file location of SoftBody data.
        self.directory = directory

        # nodes and springs
        self.nodes = {}
        self.springs = []
        self.border_nodes = {} # border nodes: collection of nodes that are used to fill in polygon, if border nodes exist.
        self.polygons = []

        # load in SoftBody Data
        with open(self.directory, 'r') as file:
            self.data = json.load(file)
        self.node_data = self.data['node_data']
        self.adjacency_list = self.data['adjacency_list']

        # create nodes
        for pos in self.node_data:
            node = self.node_data[pos]
            self.nodes[str(node['id'])] = Node(self.render_surf, self.x+node['pos'][0]*self.spacing, self.y+node['pos'][1]*self.spacing, node['pos'], node['fixed'], node['border'], node['id'])

        # creates a list of border nodes that are used to draw the polygon
        for i in self.nodes:
            node = self.nodes[i]
            if node.border == True:
                self.border_nodes[i] = node

        # create springs: every spring connects two nodes attached to to either end.
        for i in self.adjacency_list:
            id_list = self.adjacency_list[i]['adjacency']
            for node_id in id_list:
                if int(node_id) > int(i): # so that springs are not created and drawn twice.
                    node1 = self.nodes[str(i)]
                    node2 = self.nodes[str(node_id)]
                    self.springs.append(Spring(
                        self.render_surf, 
                        node1, 
                        node2, 
                        math.sqrt(
                            (node2.gridpos[0] - node1.gridpos[0])**2 + 
                            (node2.gridpos[1] - node1.gridpos[1])**2
                        )*self.spacing
                    ))
        self.create_polygons()

    # Using a BFS(breadth first search) algorithm to traverse border nodes to create polygon objects
    def create_polygons(self):
        unseen = self.border_nodes.copy()
        while len(unseen) > 0:
            new_polygon = Polygon()
            frontier = [] # queue of Node objects
            #explored = [] # added to polygon
            first_key = next(iter(unseen))
            frontier.append(unseen.pop(first_key))
            while len(frontier) > 0: # when len(frontier) = 0, the nodes of one connected component have all been explored. create the polygon and move onto the next component, if exists.
                current_adjacency = self.adjacency_list[str(frontier[0].id)]['adjacency']
                for i in current_adjacency:
                    if str(i) in unseen: # assuming only 1 next node connection, apart from the first node in sequence
                        frontier.append(unseen.pop(str(i)))
                        break
                new_polygon.add_node(frontier.pop(0))
            self.polygons.append(new_polygon)

    # fill in SoftBody with a solid color:
    def fill(self):
        for p in self.polygons:
            p.fill(self.render_surf, self.color)

    def render_spring(self):
        for spring in self.springs:
            spring.render(self.color)

    def render_node(self):
        for i in self.nodes:
            node = self.nodes[i]
            node.render()

    def apply_force(self, fx, fy):
        for i in self.nodes:
            self.nodes[i].apply_force(fx,fy)
            
    # update state of Softbody springs and nodes
    def update(self, wind, gravity):
        for spring in self.springs:
            spring.update()
        for i in self.nodes:
            node = self.nodes[i]
            node.update(wind, gravity)

