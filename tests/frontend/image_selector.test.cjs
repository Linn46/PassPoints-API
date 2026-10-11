const assert = require("node:assert/strict");
const { existsSync, readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const selectorPath = path.resolve(
  __dirname,
  "../../frontend/js/image-selector.js",
);
const selectorSource = readFileSync(selectorPath, "utf8");
const selectorContext = vm.createContext({ window: {} });
vm.runInContext(selectorSource, selectorContext);

test("image catalog contains at least twenty distinct image IDs", () => {
  const images = vm.runInContext(
    "PASSPOINT_IMAGES.map(({id, src}) => ({id, src}))",
    selectorContext,
  );
  const imageIds = Array.from(images, (image) => image.id);

  assert.ok(imageIds.length >= 20);
  assert.equal(new Set(imageIds).size, imageIds.length);
  assert.ok(
    Array.from(images, (image) =>
      existsSync(path.resolve(__dirname, "../../frontend", image.src)),
    ).every(Boolean),
  );
});

test("registration image sampling returns five unique catalog images", () => {
  const selected = vm.runInContext(
    "selectRandomImages(PASSPOINT_IMAGES, 5, () => 0)",
    selectorContext,
  );
  const selectedIds = Array.from(selected, (image) => image.id);
  const catalogIds = vm.runInContext(
    "PASSPOINT_IMAGES.map((image) => image.id)",
    selectorContext,
  );

  assert.equal(selectedIds.length, 5);
  assert.equal(new Set(selectedIds).size, 5);
  assert.ok(selectedIds.every((id) => catalogIds.includes(id)));
});

test("registration sampling can produce different sets on a later selection", () => {
  const seededRandom = (seed) => () => {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
  selectorContext.random = seededRandom(1);
  const first = vm.runInContext(
    "selectRandomImages(PASSPOINT_IMAGES, 5, random)",
    selectorContext,
  );
  selectorContext.random = seededRandom(2);
  const second = vm.runInContext(
    "selectRandomImages(PASSPOINT_IMAGES, 5, random)",
    selectorContext,
  );
  delete selectorContext.random;

  const firstIds = Array.from(first, (image) => image.id).sort();
  const secondIds = Array.from(second, (image) => image.id).sort();
  assert.notDeepEqual(firstIds, secondIds);
});

test("registration image sampling fails if the catalog is too small", () => {
  assert.throws(
    () =>
      vm.runInContext(
        "selectRandomImages([{id: 'one'}, {id: 'one'}], 5)",
        selectorContext,
      ),
    /Cannot choose 5 images/,
  );
});
