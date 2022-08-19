import { Context, Hono } from "hono";

// create a new hono client
const app = new Hono();

app.get("/arc-sw.js", async (c: Context) => {
    // Fetch from origin server.
    const response = await fetch(c.env.ARC_CORE);

    // Create an identity TransformStream (a.k.a. a pipe).
    // The readable side will become our new response body.
    const { readable, writable } = new TransformStream();

    // Start pumping the body. NOTE: No await!
    response.body?.pipeTo(writable);

    // ... and deliver our Response while that’s running.
    return new Response(readable, response);
});

// listen for get requests on /
app.get("/*", async (c: Context) => {
    const formedUrl = new URL(c.req.url);
    let fqdn = c.env.FQDN;
    if (!fqdn.endsWith("/")) fqdn = fqdn + "/";
    const dlUrl = fqdn + formedUrl.pathname.slice(1);

    // Fetch from origin server.
    const response = await fetch(dlUrl);

    // Create an identity TransformStream (a.k.a. a pipe).
    // The readable side will become our new response body.
    const { readable, writable } = new TransformStream();

    // Start pumping the body. NOTE: No await!
    response.body?.pipeTo(writable);

    // ... and deliver our Response while that’s running.
    return new Response(readable, response);
});

export default app;
