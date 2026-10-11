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
  return {
    children: [],
    disabled: false,
    style: {},
    textContent: "",
    addEventListener(type, listener) {
      listeners.set(type, listener);
    },
    click(event = {}) {
      listeners.get("click")?.(event);
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
