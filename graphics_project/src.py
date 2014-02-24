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
out vec4 FragColor;
void main(){
    vec3 scatteredLight = vec3(Ambient.rgb);
    vec3 rgb = min(vColor.rgb * scatteredLight, vec3(1.0));
    FragColor = vec4(rgb, vColor.a);
}
"""
