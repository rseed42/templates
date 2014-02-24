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
uniform vec4 Ambient;
in vec4 vColor;
void main(){
//    gl_FragColor = vColor;
    vec4 scatteredLight = Ambient; // Only light
    // modulate surface color with light, but saturate at white
    gl_FragColor = min(vColor * scatteredLight, vec4(1.0));
}
"""
