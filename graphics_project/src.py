# Check if 330 can be supported on this machine
VERTEX_SHADER = """#version 130
// Can't use layout due to 130
//in vec4 vPos;
//in vec4 vCol;
uniform mat4 View, Model, Projection;
out vec4 vColor;
void main(){
     gl_Position = Projection * View * Model * gl_Vertex;
     vColor = gl_Color;
}
"""
FRAGMENT_SHADER = """#version 130
in vec4 vColor;
void main(){
    gl_FragColor = vColor;
}
"""
