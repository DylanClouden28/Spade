import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 25;

const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1;

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.enablePan = false;
controls.target.set(0, 0, 0);
controls.update();

const textureLoader = new THREE.TextureLoader();
textureLoader.load("src/assets/starmap_8k.jpg", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;

  texture.colorSpace = THREE.SRGBColorSpace;

  scene.background = texture;
  console.log("Skybox loaded successfully.");
});

const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 2.5);
camera.add(directionalLight);
scene.add(camera);

const gltfLoader = new GLTFLoader();

let earthModel;

gltfLoader.load(
  "src/assets/earth.glb",
  function (gltf) {
    earthModel = gltf.scene;

    earthModel.traverse(function (child) {
      if (child.isMesh && child.material) {
        child.material.roughness = 0.9;
        child.material.needsUpdate = true;
      }
    });

    scene.add(earthModel);
    console.log("Model loaded successfully!");

    animate();
  },
  function (xhr) {
    console.log((xhr.loaded / xhr.total) * 100 + "% loaded");
  },
  function (error) {
    console.error("An error happened:", error);
  }
);

function animate() {
  requestAnimationFrame(animate);

  controls.update();

  renderer.render(scene, camera);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
