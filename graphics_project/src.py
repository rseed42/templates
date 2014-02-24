# Check if 330 can be supported on this machine
VERTEX_SHADER = """#version 130
uniform mat4 View, Model, Projection;
out vec4 vCol;
void main(){
     gl_Position = Projection * View * Model * gl_Vertex;
     vCol = gl_Color;
}
"""
FRAGMENT_SHADER = """#version 130
in vec4 vCol;
void main(){
//    gl_FragColor = vertex_color;
    gl_FragColor = vCol;
}
"""
