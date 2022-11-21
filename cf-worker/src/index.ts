import { Context, Hono } from "hono";

// create a new hono client
const app = new Hono();

// listen for get requests on /
app.get("/*", async (c: Context) => {
    // get the formed url from the context
    const formedUrl = new URL(c.req.url);

    // get the fqdn from the env
    let fqdn = c.env.FQDN;

    // if fqdn ends without a slash, add one to it
    if (!fqdn.endsWith("/")) fqdn = fqdn + "/";

    // slice the formed url to get the path, which is the file path
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

// export default app
export default app;
