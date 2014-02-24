# Check if 330 can be supported on this machine
VERTEX_SHADER = """#version 130
uniform mat4 View, Model, Projection;
in vec4 vPos;
in vec4 vCol;
out vec4 vColor;
void main(){
     gl_Position = Projection * View * Model * vPos;
     vColor = vCol;
}
"""
FRAGMENT_SHADER = """#version 130
in vec4 vColor;
void main(){
    gl_FragColor = vColor;
}
"""
