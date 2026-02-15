---
title: On Static Sites
date: 2026-02-15
published: true
---

So I've wanted a blog for a while, and I was out there looking at different blogging tools. They all seemed to have a lot of bells and whistles I wasn't super interested in, and would require me running a bunch of infra on the backend, which I wasn't super interested in paying for.

I remembered you could host static sites from inside an S3 bucket, and that was attractive because it's barely an infrastructure at all! I was able to put together the cloudformation templates, templating scripts, and tests with Claude Code in under an hour. Every time I make a change to the site, I just need to run the `make` file, which takes under 2 seconds, and that's including all the tests I'm writing.

I'll probably need to add some more functionality sooner or later but I'm pretty happy with how this turned out!