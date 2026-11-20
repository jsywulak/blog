---
title: On Static Sites, part ii
date: 2026-11-20
published: false
---

Put this on the backburner while real life got in the way, but had some free time and wanted to come back to it.

The downside of hosting sites in S3 is you can't do https, which really isn't a dealbreaker for this use case but does make every browser mad. The solution to that is Cloudfront, which I had been under the impression was super expensive, but I had missed them [changing their pricing structure](https://aws.amazon.com/cloudfront/pricing/) a while back. The pricing plans don't make a huge difference since it's unlikely I'll write anything interesting enough to get me using more than the free tier, but by signing up for a free plan will keep my bill from going out of control: if you exceed your plan tier, you get throttled instead of them just happily serving the traffic and charging you for it. 

Site seems super zippy so I'm pretty happy with how this turned out.