---
slug: getting-our-bearings
id: s4xdjzaiupch
type: challenge
title: Getting our bearings
notes:
- type: text
  contents: |-
    Welcome to this 15-20 minute interactive Elastic Observability 101 experience!

    In the background we are creating a whole Elasticsearch cluster just for you, loading some data and setting up some challenges. This process will take 2 - 3 minutes to complete before you get started. Once we're ready to go, click Start in the bottom right to head to the introduction.
tabs:
- id: hxjostup7jv2
  title: Elasticsearch
  type: service
  hostname: kubernetes-vm
  path: /app/apm/service-map?comparisonEnabled=false&environment=ENVIRONMENT_ALL&rangeFrom=now-15m&rangeTo=now
  port: 30001
difficulty: basic
timelimit: 600
enhanced_loading: null
---
To better appreciate how Elastic can help us quickly and definitively Root Cause Analyze (RCA) problems that arise, we will be working with an example stock trading system, comprised of several services and their dependencies, all instrumented using [OpenTelemetry](https://opentelemetry.io).

We will be working with a live Elasticsearch instance, displayed in the browser tab to the left. We are currently looking at Elastic's dynamically generated Service Map. It shows all of the services that comprise our system, and how they interact with one another.

![service-map.png](../assets/service-map.png)

Our trading system is composed of:
* `trader`: a python application that trades stocks on orders from customers
* `router`: a node.js application that routes committed trade records
* `recorder-java`: a Java application that records trades to a PostgreSQL database
* `notifier`: a .NET application that notifies an external system of completed trades

Finally, we have `monkey`, a python application we use for testing our system that makes periodic, automated trade requests on behalf of fictional customers.

> [!NOTE]
> You are welcome to explore each service and our APM solution by clicking on each service icon in the Service Map and selecting `Service Details`

When you are ready, click the `Next` button to continue.