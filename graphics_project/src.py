# Check if 330 can be supported on this machine
VERTEX_SHADER = """#version 130
uniform mat4 View, Model, Projection;
in vec4 vPos;
in vec4 vCol;
in vec4 vNorm;
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
VERTEX_SHADER_LIGHT = """#version 130
uniform mat4 View, Model, Projection;
uniform mat3 NormalMatrix;
in vec4 vPos;
in vec4 vCol;
in vec4 vNorm;
out vec4 vColor;
out vec3 Normal;
void main(){
     gl_Position = Projection * View * Model * vPos;
     vColor = vCol;
     // Transform the normal without perspective and normalize it
     Normal = normalize(NormalMatrix * vNorm.xyz);
}
"""
FRAGMENT_SHADER_LIGHT = """#version 130
uniform vec4 Ambient;
uniform vec3 LightColor;
uniform vec3 LightDirection;
uniform vec3 HalfVector;
uniform float Shininess;
uniform float Strength;
in vec4 vColor;
in vec3 Normal;
out vec4 FragColor;
void main(){
    // Compute cosine of the directions, using dot products,
    // to see how much light would be reflected:
    float diffuse = max(0.0, dot(Normal, LightDirection));
    float specular = max(0.0, dot(Normal, HalfVector));

    // Surfaces facing away from the light (negative dot products)
    // won't be lit by the directional light
    if (diffuse == 0.0)
        specular = 0.0;
    else
        specular = pow(specular, Shininess); // sharpen the highlight
    vec3 scatteredLight = Ambient.rgb + LightColor * diffuse;
    vec3 reflectedLight = LightColor * specular * Strength;
    // Don't modulate the underlying color with reflected light,
    // only with scattered light
    vec3 rgb = min(vColor.rgb * scatteredLight + reflectedLight, vec3(1.0));
    FragColor = vec4(rgb, vColor.a);
}
"""
VERTEX_POINT_LIGHT = """#version 130
uniform mat4 ViewMatrix, ModelMatrix, ProjectionMatrix;
uniform mat3 NormalMatrix;
mat4 MVMatrix = ViewMatrix * ModelMatrix;

in vec4 VertexPosition;
in vec3 VertexNormal;
in vec4 VertexColor;

out vec4 Position;
out vec3 Normal;
out vec4 Color;

void main(){
    Color = VertexColor;
    Normal = normalize(NormalMatrix * VertexNormal);
    Position = MVMatrix * VertexPosition;
    gl_Position = ProjectionMatrix * ViewMatrix * ModelMatrix * VertexPosition;
}
"""
FRAGMENT_POINT_LIGHT = """#version 130
uniform vec3 Ambient;
uniform vec3 LightColor;
uniform vec3 LightPosition;
uniform float Shininess;
uniform float Strength;
uniform vec3 EyeDirection;
uniform float ConstantAttenuation;
uniform float LinearAttenuation;
uniform float QuadraticAttenuation;

in vec4 Position;
in vec3 Normal;
in vec4 Color;

out vec4 FragColor;

void main(){
    // Find the direction and distance of the light, which changes fragment
    // to fragment for a local light:
    vec3 lightDirection = LightPosition - vec3(Position);
    float lightDistance = length(lightDirection);

    // Normalize the light direction vector, so that  dot products give cosines:
    lightDirection = lightDirection / lightDistance;

    // Model how much light is available for this fragment:
    float attenuation = 1.0 / (ConstantAttenuation +
                               LinearAttenuation * lightDistance +
                            QuadraticAttenuation * lightDistance * lightDistance
    );

    // The direction of maximum highlight also changes per fragment
    vec3 halfVector = normalize(lightDirection + EyeDirection);
    float diffuse = max(0.0, dot(Normal, lightDirection));
    float specular = max(0.0, dot(Normal, halfVector));
    if (diffuse == 0.0)
        specular = 0.0;
    else
        specular = pow(specular, Shininess) * Strength;

    vec3 scatteredLight = Ambient + LightColor * diffuse * attenuation;
    vec3 reflectedLight = LightColor * specular * attenuation;
    vec3 rgb = min(Color.rgb * scatteredLight + reflectedLight, vec3(1.0));

    FragColor = vec4(rgb, Color.a);
}
"""
