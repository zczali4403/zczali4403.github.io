'use strict';
const profile = window.PROFILE;
const stops = profile.stops;
const byId = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const points = stops.map(stop => ({ x: (stop.coordinate[0] - 100) * 31, y: (39 - stop.coordinate[1]) * 27.3 }));
const paths = [];
const markers = [];
const photoCards = [];
let selected = 0;
let frame = null;
let playing = false;
let segment = 0;
let segmentElapsed = 0;
let lastTimestamp = null;
let completed = false;
const duration = 1900;
function svgElement(tag, attributes) {
  const node = document.createElementNS(svgNS, tag);
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
  return node;
}
function textElement(tag, className, content) {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = content;
  return node;
}
if (profile.name) {
  byId('brand-name').textContent = profile.name;
  byId('footer-name').textContent = profile.name + ' · MY JOURNEY';
  document.title = profile.name + ' · AI for Biology';
}
byId('profile-intro').textContent = profile.intro;
byId('about-text').textContent = profile.about;
byId('about-signature').textContent = profile.signature;
profile.links.forEach(link => {
  // Limit contact links to common safe protocols.
  if (!/^(https?:\/\/|mailto:)/i.test(link.url)) return;
  const anchor = textElement('a', '', link.label);
  anchor.href = link.url;
  if (/^https?:/i.test(link.url)) { anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; }
  byId('profile-links').append(anchor);
});
points.slice(0, -1).forEach((start, i) => {
  const end = points[i + 1];
  const bend = i === 1 ? -78 : 62;
  const control = { x: (start.x + end.x) / 2 + bend, y: (start.y + end.y) / 2 - 48 };
  const d = `M${start.x},${start.y} Q${control.x},${control.y} ${end.x},${end.y}`;
  byId('route-layer').append(svgElement('path', { d, class: 'route-background' }));
  const path = svgElement('path', { d, class: 'route-active', pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1 });
  byId('route-layer').append(path);
  paths.push(path);
});
stops.forEach((stop, i) => {
  const point = points[i];
  if (stop.photo) {
    const photoButton = textElement('button', 'campus-photo', '');
    photoButton.type = 'button';
    photoButton.style.left = stop.photo.x;
    photoButton.style.top = stop.photo.y;
    photoButton.style.setProperty('--pin-x', `${point.x / 760 * 100}%`);
    photoButton.style.setProperty('--pin-y', `${point.y / 520 * 100}%`);
    photoButton.setAttribute('aria-label', `View photograph of ${stop.school}`);
    photoButton.setAttribute('aria-haspopup', 'dialog');
    const photo = document.createElement('img');
    photo.src = stop.photo.src;
    photo.alt = stop.photo.alt;
    photo.width = 240;
    photo.height = 150;
    photo.decoding = 'async';
    photoButton.append(photo, textElement('span', '', stop.city));
    photoButton.addEventListener('click', () => { jumpTo(i); openPhoto(stop); });
    byId('campus-photos').append(photoButton);
    photoCards.push(photoButton);
  }

  const marker = svgElement('g', { class: 'city-marker', role: 'button', tabindex: '0', 'aria-label': `${i + 1} ${stop.city}：${stop.school}`, 'aria-pressed': 'false', transform: `translate(${point.x},${point.y})` });
  marker.append(svgElement('circle', { r: 25, class: 'marker-halo' }), svgElement('rect', { x: -34, y: -54, width: 160, height: 100, class: 'marker-hit' }), svgElement('circle', { r: 8, class: 'marker-ring' }), svgElement('circle', { r: 3.4, class: 'marker-dot' }));
  const label = svgElement('text', { x: stop.label[0], y: stop.label[1], class: 'city-label' });
  label.textContent = stop.city;
  const english = svgElement('text', { x: stop.label[0], y: stop.label[1] + 17, class: 'city-english' });
  english.textContent = stop.english;
  marker.append(label, english);
  marker.addEventListener('click', () => jumpTo(i));
  marker.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); jumpTo(i); } });
  byId('marker-layer').append(marker);
  markers.push(marker);
  const card = document.createElement('article');
  card.className = 'education-card';
  const top = textElement('div', 'chapter-top', '');
  top.append(textElement('span', '', `CHAPTER 0${i + 1}`), textElement('span', '', [stop.stage, stop.years].filter(Boolean).join(' · ')));
  const city = textElement('h3', '', stop.city);
  city.append(textElement('span', '', stop.english));
  const button = textElement('button', 'chapter-button', 'View on map ↗');
  button.type = 'button';
  button.setAttribute('aria-label', `View ${stop.school} on the map`);
  button.addEventListener('click', () => { jumpTo(i); byId('journey').scrollIntoView({ behavior: reducedMotion.matches ? 'instant' : 'smooth' }); markers[i].focus({ preventScroll: true }); });
  card.append(top, city, textElement('h4', '', stop.school), textElement('p', '', stop.description), button);
  byId('education-grid').append(card);
});
function selectStop(index) {
  selected = index;
  const stop = stops[index];
  const number = String(index + 1).padStart(2, '0');
  byId('detail-number').textContent = number;
  byId('detail-location').textContent = stop.province === stop.city ? stop.city : `${stop.city} · ${stop.province}`;
  byId('detail-school').textContent = stop.school;
  byId('detail-stage').textContent = [stop.stage, stop.years, stop.title].filter(Boolean).join(' · ');
  byId('detail-count').textContent = `${number} / 04`;
  byId('map-progress-fill').style.width = `${(index + 1) / stops.length * 100}%`;
  photoCards.forEach((card, i) => card.classList.toggle('is-active', i === index));
  markers.forEach((marker, i) => marker.setAttribute('aria-pressed', String(i === index)));
  [...byId('education-grid').children].forEach((card, i) => card.classList.toggle('is-active', i === index));
}
function updatePlayButton() {
  byId('play-label').textContent = reducedMotion.matches ? 'Next chapter' : playing ? 'Pause journey' : completed ? 'Replay journey' : segmentElapsed > 0 || segment > 0 ? 'Resume journey' : 'Play my journey';
  byId('play-button').querySelector('.play-icon').textContent = playing ? 'Ⅱ' : '▶';
}
function stopAnimation() {
  playing = false;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  lastTimestamp = null;
  updatePlayButton();
}
function setTraveler(point) {
  ['traveler', 'traveler-halo'].forEach(id => { byId(id).hidden = false; byId(id).removeAttribute('hidden'); byId(id).setAttribute('cx', point.x); byId(id).setAttribute('cy', point.y); });
}
function hideTraveler() { ['traveler', 'traveler-halo'].forEach(id => byId(id).setAttribute('hidden', '')); }
function jumpTo(index) {
  stopAnimation();
  selected = index;
  segment = index;
  segmentElapsed = 0;
  completed = index === stops.length - 1;
  paths.forEach((path, i) => path.setAttribute('stroke-dashoffset', i < index ? 0 : 1));
  hideTraveler();
  selectStop(index);
  updatePlayButton();
}
function animate(timestamp) {
  if (!playing) return;
  if (lastTimestamp !== null) segmentElapsed += Math.min(timestamp - lastTimestamp, 64);
  lastTimestamp = timestamp;
  const progress = Math.min(segmentElapsed / duration, 1);
  const eased = progress * progress * (3 - 2 * progress);
  const path = paths[segment];
  path.setAttribute('stroke-dashoffset', 1 - eased);
  setTraveler(path.getPointAtLength(path.getTotalLength() * eased));
  if (progress >= 1) {
    segment += 1;
    segmentElapsed = 0;
    selectStop(segment);
    if (segment === paths.length) { completed = true; stopAnimation(); hideTraveler(); return; }
  }
  frame = requestAnimationFrame(animate);
}
byId('play-button').addEventListener('click', () => {
  if (reducedMotion.matches) { jumpTo((selected + 1) % stops.length); return; }
  if (playing) { stopAnimation(); return; }
  if (completed) jumpTo(0);
  playing = true;
  lastTimestamp = null;
  updatePlayButton();
  frame = requestAnimationFrame(animate);
});
byId('previous-stop').addEventListener('click', () => jumpTo((selected + stops.length - 1) % stops.length));
byId('next-stop').addEventListener('click', () => jumpTo((selected + 1) % stops.length));
document.addEventListener('visibilitychange', () => { if (document.hidden && playing) stopAnimation(); });
reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) { stopAnimation(); hideTraveler(); } updatePlayButton(); });
selectStop(0);
updatePlayButton();

function openPhoto(stop) {
  byId('photo-city').textContent = stop.city + ' / ' + stop.english;
  byId('photo-title').textContent = stop.school;
  byId('photo-full').src = stop.photo.src;
  byId('photo-full').alt = stop.photo.alt;
  byId('photo-description').textContent = stop.photo.alt;
  byId('photo-source').href = stop.photo.source;
  byId('photo-source').textContent = 'Photo: ' + stop.photo.credit;
  byId('photo-dialog').showModal();
}
byId('close-photo').addEventListener('click', () => byId('photo-dialog').close());
byId('photo-dialog').addEventListener('click', event => {
  if (event.target !== byId('photo-dialog')) return;
  const box = byId('photo-dialog').getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) byId('photo-dialog').close();
});
