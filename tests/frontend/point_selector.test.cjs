const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const selectorSource = readFileSync(
  path.resolve(__dirname, "../../frontend/js/point-selector.js"),
  "utf8",
);

function createElement() {
  const listeners = new Map();
  const pointerCaptures = new Set();
  return {
    children: [],
    disabled: false,
    style: {},
    textContent: "",
    setAttribute() {},
    addEventListener(type, listener) {
      listeners.set(type, listener);
    },
    click(event = {}) {
      listeners.get("click")?.(event);
    },
    dispatch(type, event = {}) {
      listeners.get(type)?.(event);
    },
    setPointerCapture(pointerId) {
      pointerCaptures.add(pointerId);
    },
    hasPointerCapture(pointerId) {
      return pointerCaptures.has(pointerId);
    },
    releasePointerCapture(pointerId) {
      pointerCaptures.delete(pointerId);
    },
    replaceChildren() {
      this.children = [];
    },
    appendChild(child) {
      this.children.push(child);
    },
    getBoundingClientRect() {
      return { left: 0, top: 0, width: 100, height: 100 };
    },
  };
}

test("undo removes the most recently selected point and respects the lock", () => {
  const elements = new Map(
    [
      "points-layer",
      "point-count",
      "clear-points",
      "undo-point",
      "selected-image",
      "point-feedback",
    ].map((id) => [id, createElement()]),
  );
  const dispatchedEvents = [];
  const document = {
    getElementById: (id) => elements.get(id),
    createElement,
    addEventListener() {},
    dispatchEvent(event) {
      dispatchedEvents.push(event.type);
    },
  };
  const context = vm.createContext({
    document,
    window: {},
    CustomEvent: class CustomEvent {
      constructor(type) {
        this.type = type;
      }
    },
    getImageData: () => ({ id: "test-image", width: 1920, height: 1080 }),
  });

  vm.runInContext(selectorSource, context);
  vm.runInContext("initializePointSelector()", context);

  const image = elements.get("selected-image");
  image.click({ clientX: 15, clientY: 20 });
  image.click({ clientX: 50, clientY: 40 });
  assert.equal(elements.get("point-count").textContent, "2/5");
  assert.equal(elements.get("undo-point").disabled, false);

  elements.get("undo-point").click();
  assert.equal(elements.get("point-count").textContent, "1/5");
  assert.deepEqual(
    elements
      .get("points-layer")
      .children.map(({ textContent }) => textContent),
    ["1"],
  );
  assert.equal(context.window.getSelectedPoints()[0].x, (15 * 1920) / 100);

  context.window.setPointSelectionLocked(true);
  elements.get("undo-point").click();
  assert.equal(elements.get("point-count").textContent, "1/5");
  context.window.setPointSelectionLocked(false);
  elements.get("undo-point").click();
  assert.equal(elements.get("point-count").textContent, "0/5");
  assert.equal(elements.get("undo-point").disabled, true);
  assert.equal(
    dispatchedEvents.filter((type) => type === "points-changed").length,
    4,
  );
});

test("selected points can be dragged without changing their sequence order", () => {
  const elements = new Map(
    [
      "points-layer",
      "point-count",
      "clear-points",
      "undo-point",
      "selected-image",
      "point-feedback",
    ].map((id) => [id, createElement()]),
  );
  const dispatchedEvents = [];
  const document = {
    getElementById: (id) => elements.get(id),
    createElement,
    addEventListener() {},
    dispatchEvent(event) {
      dispatchedEvents.push(event.type);
    },
  };
  const context = vm.createContext({
    document,
    window: {},
    CustomEvent: class CustomEvent {
      constructor(type) {
        this.type = type;
      }
    },
    getImageData: () => ({ id: "test-image", width: 1920, height: 1080 }),
    t: () => "Points are too close.",
  });

  vm.runInContext(selectorSource, context);
  vm.runInContext("initializePointSelector()", context);

  const image = elements.get("selected-image");
  image.click({ clientX: 15, clientY: 20 });
  image.click({ clientX: 50, clientY: 40 });
  const firstMarker = elements.get("points-layer").children[0];

  firstMarker.dispatch("pointerdown", {
    pointerId: 1,
    preventDefault() {},
  });
  firstMarker.dispatch("pointermove", {
    pointerId: 1,
    clientX: 70,
    clientY: 70,
  });
  firstMarker.dispatch("pointerup", { pointerId: 1 });

  const points = context.window.getSelectedPoints();
  assert.equal(points[0].x, 0.7 * 1920);
  assert.equal(points[0].y, 0.7 * 1080);
  assert.equal(points[1].x, 0.5 * 1920);
  assert.equal(elements.get("points-layer").children[0].style.left, "70%");
  assert.deepEqual(
    dispatchedEvents.filter((type) => type === "points-changed"),
    ["points-changed", "points-changed", "points-changed"],
  );

  context.window.setPointSelectionLocked(true);
  firstMarker.dispatch("pointerdown", {
    pointerId: 2,
    preventDefault() {},
  });
  firstMarker.dispatch("pointermove", {
    pointerId: 2,
    clientX: 20,
    clientY: 30,
  });
  assert.equal(context.window.getSelectedPoints()[0].x, 0.7 * 1920);
});

test("selecting points inside each other's tolerance radius shows feedback", () => {
  const elements = new Map(
    [
      "points-layer",
      "point-count",
      "clear-points",
      "undo-point",
      "selected-image",
      "point-feedback",
      "tolerance-radius",
    ].map((id) => [id, createElement()]),
  );
  elements.get("tolerance-radius").value = "10";
  const document = {
    getElementById: (id) => elements.get(id),
    createElement,
    addEventListener() {},
    dispatchEvent() {},
  };
  const context = vm.createContext({
    document,
    window: {},
    CustomEvent: class CustomEvent {
      constructor(type) {
        this.type = type;
      }
    },
    getImageData: () => ({ id: "test-image", width: 1920, height: 1080 }),
    t: () => "Points are too close.",
  });

  vm.runInContext(selectorSource, context);
  vm.runInContext("initializePointSelector()", context);

  const image = elements.get("selected-image");
  image.click({ clientX: 25, clientY: 25 });
  image.click({ clientX: 26, clientY: 25 });

  assert.equal(elements.get("point-count").textContent, "1/5");
  assert.equal(elements.get("point-feedback").textContent, "Points are too close.");
});

test("login point selection is not constrained by a registration radius", () => {
  const elements = new Map(
    [
      "points-layer",
      "point-count",
      "clear-points",
      "undo-point",
      "selected-image",
      "point-feedback",
      "tolerance-radius",
    ].map((id) => [id, createElement()]),
  );
  elements.get("tolerance-radius").value = "20";
  const listeners = new Map();
  const document = {
    getElementById: (id) => elements.get(id),
    createElement,
    addEventListener(type, listener) {
      listeners.set(type, listener);
    },
    dispatchEvent(event) {
      listeners.get(event.type)?.(event);
    },
  };
  const context = vm.createContext({
    document,
    window: {},
    CustomEvent: class CustomEvent {
      constructor(type) {
        this.type = type;
      }
    },
    getImageData: () => ({ id: "test-image", width: 1920, height: 1080 }),
    t: () => "Points are too close.",
  });

  vm.runInContext(selectorSource, context);
  vm.runInContext("initializePointSelector()", context);
  document.dispatchEvent({
    type: "authentication-mode-changed",
    detail: { mode: "login", repeating: false },
  });

  const image = elements.get("selected-image");
  image.click({ clientX: 25, clientY: 25 });
  image.click({ clientX: 26, clientY: 25 });

  assert.equal(elements.get("point-count").textContent, "2/5");
});
