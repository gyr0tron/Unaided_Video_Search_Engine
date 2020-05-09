"use strict";

const {
  PI,
  cos,
  sin,
  tan,
  abs,
  sqrt,
  pow,
  min,
  max,
  ceil,
  floor,
  round,
  random,
  atan2,
} = Math;
const HALF_PI = 0.5 * PI;
const QUART_PI = 0.25 * PI;
const TAU = 2 * PI;
const TO_RAD = PI / 180;
const G = 6.67 * pow(10, -11);
const EPSILON = 2.220446049250313e-16;
const rand = (n) => n * random();
const randIn = (_min, _max) => rand(_max - _min) + _min;
const randRange = (n) => n - rand(2 * n);
const fadeIn = (t, m) => t / m;
const fadeOut = (t, m) => (m - t) / m;
const fadeInOut = (t, m) => {
  let hm = 0.5 * m;
  return abs(((t + hm) % m) - hm) / hm;
};
const dist = (x1, y1, x2, y2) => sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));
const angle = (x1, y1, x2, y2) => atan2(y2 - y1, x2 - x1);
const lerp = (a, b, amt) => (1 - amt) * a + amt * b;
const vh = (p) => p * window.innerHeight * 0.01;
const vw = (p) => p * window.innerWidth * 0.01;
const vmin = (p) => min(vh(p), vw(p));
const vmax = (p) => max(vh(p), vw(p));
const clamp = (n, _min, _max) => min(max(n, _min), _max);
const norm = (n, _min, _max) => (n - _min) / (_max - _min);

Array.prototype.lerp = function (t = [], a = 0) {
  this.forEach((n, i) => (this[i] = lerp(n, t[i], a)));
};

Float32Array.prototype.get = function (i = 0, n = 0) {
  const t = i + n;

  let r = [];

  for (; i < t; i++) {
    r.push(this[i]);
  }

  return r;
};

class PropsArray {
  constructor(count = 0, props = []) {
    this.count = count;
    this.props = props;
    this.spread = props.length; // TODO: Need to implement indexing based on spread
    this.values = new Float32Array(count * props.length);
  }
  get length() {
    return this.values.length;
  }
  set(a = [], i = 0) {
    this.values.set(a, i);
  }
  setMap(o = {}, i = 0) {
    this.set(Object.values(o), i);
  }
  get(i = 0) {
    return this.values.get(i, this.props.length);
  }
  getMap(i = 0) {
    return this.get(i).reduce(
      (r, v, i) => ({
        ...r,
        ...{ [this.props[i]]: v },
      }),

      {}
    );
  }
  forEach(cb) {
    let i = 0;

    for (; i < this.length; i += this.props.length) {
      cb(this.get(this, i), i, this);
    }
  }
  map(cb) {
    let i = 0;

    for (; i < this.length; i += this.props.length) {
      this.set(cb(this.get(this, i), i, this), i);
    }
  }
  async *read() {
    let i = 0;

    for (; i < this.length; i += this.props.length) {
      yield this.get(i);
    }
  }
}

("use strict");

const particleCount = 500;
const particlePropCount = 9;
const particlePropsLength = particleCount * particlePropCount;
const spawnRadius = rand(200) + 400;
const noiseSteps = 10;

let canvas;
let ctx;
let center;
let tick;
let simplex;
let particleProps;
let positions;
let velocities;
let speeds;
let lifeSpans;
let sizes;
let hues;

function setup() {
  tick = 0;
  center = [];
  createCanvas();
  createParticles();
  draw();
}

function createParticles() {
  simplex = new SimplexNoise();
  particleProps = new Float32Array(particlePropsLength);

  let i;

  for (i = 0; i < particlePropsLength; i += particlePropCount) {
    initParticle(i);
  }
}

function initParticle(i) {
  let iy, ih, rd, rt, cx, sy, x, y, s, rv, vx, vy, t, h, w, l, ttl;

  iy = i + 1;
  ih = (0.5 * i) | 0;
  rd = rand(spawnRadius);
  rt = rand(TAU);
  cx = cos(rt);
  sy = sin(rt);
  x = center[0] + cx * rd;
  y = center[1] + sy * rd;
  rv = randIn(0.1, 1);
  s = randIn(1, 8);
  vx = rv * cx * 0.1;
  vy = rv * sy * 0.1;
  w = randIn(0.1, 2);
  h = randIn(160, 260);
  l = 0;
  ttl = randIn(50, 200);

  particleProps.set([x, y, vx, vy, s, h, w, l, ttl], i);
}

function drawParticle(i) {
  let n, dx, dy, dl, c;

  let [x, y, vx, vy, s, h, w, l, ttl] = particleProps.get(i, particlePropCount);

  n = simplex.noise3D(x * 0.0025, y * 0.0025, tick * 0.0005) * TAU * noiseSteps;
  vx = lerp(vx, cos(n), 0.05);
  vy = lerp(vy, sin(n), 0.05);
  dx = x + vx * s;
  dy = y + vy * s;
  dl = fadeInOut(l, ttl);
  c = `hsla(${h},50%,60%,${dl})`;

  l++;

  ctx.a.save();
  ctx.a.lineWidth = dl * w + 1;
  ctx.a.strokeStyle = c;
  ctx.a.beginPath();
  ctx.a.moveTo(x, y);
  ctx.a.lineTo(dx, dy);
  ctx.a.stroke();
  ctx.a.closePath();
  ctx.a.restore();

  particleProps.set([dx, dy, vx, vy, s, h, w, l, ttl], i);

  (checkBounds(x, y) || l > ttl) && initParticle(i);
}

function checkBounds(x, y) {
  return x > canvas.a.width || x < 0 || y > canvas.a.height || y < 0;
}

function createCanvas() {
  canvas = {
    a: document.createElement("canvas"),
    b: document.createElement("canvas"),
  };

  canvas.b.style = `
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
	`;
  document.body.appendChild(canvas.b);
  ctx = {
    a: canvas.a.getContext("2d"),
    b: canvas.b.getContext("2d"),
  };

  resize();
}

function resize() {
  const { innerWidth, innerHeight } = window;

  canvas.a.width = innerWidth;
  canvas.a.height = innerHeight;

  ctx.a.drawImage(canvas.b, 0, 0);

  canvas.b.width = innerWidth;
  canvas.b.height = innerHeight;

  ctx.b.drawImage(canvas.a, 0, 0);

  center[0] = 0.5 * canvas.a.width;
  center[1] = 0.5 * canvas.a.height;
}

function draw() {
  tick++;
  ctx.a.clearRect(0, 0, canvas.a.width, canvas.a.height);

  ctx.b.fillStyle = "rgba(0,0,0,0.1)";
  ctx.b.fillRect(0, 0, canvas.b.width, canvas.b.height);

  let i = 0;

  for (; i < particlePropsLength; i += particlePropCount) {
    drawParticle(i);
  }

  ctx.b.save();
  ctx.b.filter = "blur(8px)";
  ctx.b.globalCompositeOperation = "lighten";
  ctx.b.drawImage(canvas.a, 0, 0);
  ctx.b.restore();

  ctx.b.save();
  ctx.b.globalCompositeOperation = "lighter";
  ctx.b.drawImage(canvas.a, 0, 0);
  ctx.b.restore();

  window.requestAnimationFrame(draw);
}

window.addEventListener("load", setup);
window.addEventListener("resize", resize);

$(".title-wrapper").css("width", window.innerWidth);
$(".title-wrapper").css("height", window.innerHeight);

(function showText() {
  var title = $("h1"),
    subtitle = $("h2");

  title.removeClass("hidden");
  setTimeout(function () {
    subtitle.removeClass("hidden");
  }, 2000);
})();

// setTimeout(function() {
//   $.each(pathCollection, function(i, el) {
//     var $path = $(this);
//     setTimeout(function() {
//       $path.css("opacity", "1");
//     }, time);
//     time += 10;

//     if (i + 1 === count) {
//       setTimeout(function() {
//         showText();
//       }, 2000);
//     }
//   });
// }, 2000);
