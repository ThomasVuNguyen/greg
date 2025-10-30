const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(1, 2, 3);
scene.add(directionalLight);

// Pen body (main cylinder)
const penBodyGeometry = new THREE.CylinderGeometry(0.15, 0.15, 4, 32);
const penBodyMaterial = new THREE.MeshPhongMaterial({ color: 0x1a1a1a });
const penBody = new THREE.Mesh(penBodyGeometry, penBodyMaterial);
scene.add(penBody);

// Pen tip (cone)
const penTipGeometry = new THREE.ConeGeometry(0.12, 0.6, 32);
const penTipMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
const penTip = new THREE.Mesh(penTipGeometry, penTipMaterial);
penTip.position.y = -2.3;
penTip.rotation.x = Math.PI;
scene.add(penTip);

// Pen clip (thin box)
const penClipGeometry = new THREE.BoxGeometry(0.3, 1.2, 0.05);
const penClipMaterial = new THREE.MeshPhongMaterial({ color: 0x444444 });
const penClip = new THREE.Mesh(penClipGeometry, penClipMaterial);
penClip.position.set(0.25, 1.8, 0);
scene.add(penClip);

// Clicker button (small cylinder)
const buttonGeometry = new THREE.CylinderGeometry(0.2, 0.2, 0.2, 32);
const buttonMaterial = new THREE.MeshPhongMaterial({ color: 0x2c2c2c });
const button = new THREE.Mesh(buttonGeometry, buttonMaterial);
button.position.y = 2.1;
scene.add(button);

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

animate();

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener('resize', onWindowResize);