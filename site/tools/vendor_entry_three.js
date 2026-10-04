// Single-module three.js bundle for the theme (Shopify assets are a flat folder, so relative imports can't resolve).
export { WebGLRenderer, Scene, PerspectiveCamera, OrthographicCamera, Color, Vector3, Quaternion, Box3, Group,
  DirectionalLight, AmbientLight, PMREMGenerator, SRGBColorSpace, ACESFilmicToneMapping, MathUtils, Clock,
  Matrix4, Euler } from 'three';
export { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
export { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
export { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
