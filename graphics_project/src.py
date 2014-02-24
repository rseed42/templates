# Check if 330 can be supported on this machine
VERTEX_SHADER = """#version 130
uniform mat4 View, Model, Projection;
in vec4 Vertex;
void main(){
     gl_Position = Projection * View * Model * Vertex;
}
"""
FRAGMENT_SHADER = """#version 130
void main(){
//  gl_FragColor = vec4(0,0,1,0.7);
  gl_FragColor = vec4(1,1,1,1);
}
"""
