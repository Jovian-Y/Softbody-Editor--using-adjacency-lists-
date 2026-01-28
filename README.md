# Softbody Editor
A simple softbody editor featuring a softbody object system composed of a network of nodes and springs, allowing simulation of dynamic game entities with realistic deformation.

## NEW Features and Improvements
- Data storage: from edge-list representation to adjacency lists. This is done so that an iterative DFS algorithm can be applied to traverse boundaries and to identify connected components, allowing for multiple polygons to be traced from a single softbody data file. Also allows for border node creation in any order within the editor, as opposed to order dependent polygon tracing previously: "zigzag" filling is no longer a major issue (though it may still occur in cases of improper node and edge placement).

## softbody_editor.py
### Features
- Softbody editor.
- Softbody data saving in JSON format.
- SoftBody object: consists of configuration(s) of connected nodes and springs.
- Can mimic "soft body" behavior through creating a sparse network of nodes and springs. e.g., cloth, vine, spider web, net, hanging mobile.
- Can mimic stiff "rigid body" behavior through triangular node connections or compact node connections. e.g., ball, bridge.
- Grid lines.

### Instructions
- To make new softbody data, in [softbody_editor.py] code, choose a file name inside file path. If nonexistent, a new JSON file will be created automatically. If the file name exists already, running the editor will load in the already existing data.
- WASD or arrow keys to move the camera.
- actions:
  - 1: action = node. Click left mouse button to place a node at cursor's grid position. Nodes can be border and/or fixed (or none). Right click a node to delete the node.
  - 2: action = spring. Drag left mouse cursor between two grid positions with existing nodes to create a spring connecting the two nodes. Likewise, to delete a spring between two nodes, use right mouse button.
  - 3: toggle fixed on/off. Nodes placed when fixed is true will be labeled with "F" (fixed).
    - Fixed nodes are not affected by wind, gravity, or any other external force. Remains in the position in which they are initialized.
  - 4: toggle border on/off. Nodes placed when border is true will be labeled with "B" (border).
- p: save current map.

## main.py (game)
### Features
- Wind, gravity, other "external forces": use WASD to apply these forces.
  - Toggle on/off:
    - 9: wind
    - 0: gravity
- Visual representation of springs, nodes, and solid color fills.
  - Toggle on/off:
    - 1: node
    - 2: spring
    - 3: fill

### Instructions
to add softbody from data:
```python
softbodies.append(
    SoftBody(
        SURFACE,          # target surface
        (X, Y),           # position
        SCALE,            # scale factor
        (R, G, B),        # color
        "softbody_data/FILE_PATH.json"
    )
)
```
example:
```python
softbodies.append(SoftBody(display, (10,10), 7, (100,20,255), "softbody_data/cloth1.json"))
```

## IMPORTANT
- For filled polygons, All BORDER NODES must be a member of a closed loop. The start and end node does not matter, as long as it forms a closed loop connected by springs.
- To minimize rendering errors, do not DIRECTLY connect two BORDER nodes from different connected components with a spring. If they must be connected, it is best to create an intermediate NON-BORDER node.