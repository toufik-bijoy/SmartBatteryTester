const esbuild = require("esbuild"), fs = require("fs");
fs.mkdirSync("www", { recursive: true });
esbuild.buildSync({ entryPoints: ["src/ble-shim.js"], bundle: true, format: "iife", minify: true, outfile: "www/ble-shim.js" });
fs.copyFileSync("src/index.html", "www/index.html");
console.log("www/ ready");
