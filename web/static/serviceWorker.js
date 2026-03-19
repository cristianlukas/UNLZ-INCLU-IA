const staticDevIncluIA = "incluIA-v1";
const assets = [
  "/",
  "/templates/index.html",
  "/static/styles.css",
  "/static/app.js",
  "/icon-128.png",
  "/icon-512.png"
]

self.addEventListener("install", installEvent => {
  installEvent.waitUntil(
    caches.open(staticDevIncluIA).then(cache => {
      cache.addAll(assets)
    })
  )
})

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(res => {
      return res || fetch(event.request);
    })
  );
});

self.addEventListener("activate", event => {
  const whitelist = ["incluIA-v1"];
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (!whitelist.includes(key)) {
            return caches.delete(key);
          }
        })
      )
    )
  );
});