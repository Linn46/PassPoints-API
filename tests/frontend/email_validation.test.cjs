const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const authSource = readFileSync(
  path.resolve(__dirname, "../../frontend/js/auth.js"),
  "utf8",
);
const context = vm.createContext({});
vm.runInContext(authSource, context);

test("email validation rejects empty, too-short, and oversized values", () => {
  assert.equal(context.validateEmailAddress("  "), "emailRequired");
  assert.equal(context.validateEmailAddress("a@b."), "emailTooShort");
  assert.equal(context.validateEmailAddress(`${"a".repeat(251)}@b.c`), "emailTooLong");
});

test("email validation rejects malformed addresses and accepts normalized input", () => {
  for (const email of [
    "name.example.com",
    "name@localhost",
    "name@@example.com",
    "name @example.com",
    "name@example .com",
  ]) {
    assert.equal(context.validateEmailAddress(email), "emailInvalid", email);
  }

  assert.equal(context.validateEmailAddress("  Name@Example.com  "), "");
  assert.equal(context.validateEmailAddress(`${"a".repeat(250)}@b.c`), "");
});
