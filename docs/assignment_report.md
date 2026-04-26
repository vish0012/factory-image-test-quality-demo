# Software Quality Engineer Assignment Report

## Summary

My approach is to treat the factory environment differently from a normal server deployment environment. The main risks are vendor-controlled networks, limited direct access, production downtime, and difficulty reproducing results after an issue happens.

For that reason, I would focus on four things:

1. safe pull-based deployment
2. reproducible image-test results
3. measurable release gates
4. communication that turns technical signals into production risk

## 1. CD / Manufacturing Floor CD

I would avoid relying on inbound VPN access from our network into the vendor factory network. Instead, each site should run a local deployment agent that pulls only approved releases.

The local agent would:

- check the approved release manifest
- verify the artifact hash and signature
- install only during an agreed maintenance window
- run local smoke tests and reference test image checks before promotion
- keep the previous version available for immediate rollback

The release manifest should be the central source of truth for site, product, machine, algorithm version, parameter version, configuration, rollout stage, and rollback version.

The rollout path should be:

**Internal lab → Pilot machine → Pilot site → Broader rollout**

This protects production because a new version is never promoted everywhere at once.

## 2. Testing Strategy for Image-Testing Software

For image-testing software, reproducibility is the first requirement. If a result cannot be reproduced later, it is very hard to decide whether the issue was caused by the algorithm, the input image, the parameter set, the machine, or the site environment.

For each test, I would record:

- input image hash
- algorithm version
- parameter hash
- binary/runtime version
- operating system
- hardware
- site
- timestamp
- output summary

To control storage cost, I would keep all failed cases, a sample of passing cases, and a fixed reference test set. Full-resolution images should be kept mainly for failures and representative samples. For routine passing cases, hashes, metadata, result maps, and compressed references may be enough.

For regression testing, I would separate bugs from intended algorithm improvements. A result change is a bug if expected invariant behavior changes without being declared. A result change can be accepted as an improvement only when the expected change is declared before merge and verified on reference datasets.

A release should not be promoted unless it passes clear gates:

- zero crashes
- no memory leaks
- no thermal throttling
- stable reference test set results
- 99th-percentile processing time within 20% of the previous stable version
- no unexplained increase in false calls or missed defects

## 3. Quality Metrics and Communication

For engineers, I would track escape rate, test coverage, flaky tests, lead time, mean time to recovery, reference-set drift, runtime trend, and rollback rate.

For factory and leadership teams, I would translate these into line uptime, yield impact, scrap impact, affected sites, affected products, recovery time, and shipment risk.

The dashboard should be one page. It should show red/amber/green status, trend, affected site/product, owner, and business impact.

For example, instead of only saying:

> processing time increased at Site C

I would communicate:

> Site C may process fewer units per hour, which puts the shift target and shipment plan at risk.

For incidents, I would use a fixed five-line update:

1. what happened
2. impact
3. current fix
4. root cause
5. prevention

## 4. Data Analysis — Coplanarity Shift

For each part, I would fit the best plane through the 10 × 10 height grid. Then I would use the residuals from that plane to calculate coplanarity metrics such as peak-to-valley residual distance and root-mean-square residual distance.

Before blaming the part, I would check the measurement system. If measurement noise is large compared with part variation, the problem may be in the measurement process rather than the product.

The analysis flow is:

1. calculate coplanarity per part
2. compare current month against previous month
3. check whether the shift is statistically meaningful
4. create an average height-map difference
5. check whether the spatial pattern suggests tilt, bow, or twist
6. regress product-test performance against coplanarity

If the coplanarity shift strongly explains the product-test performance drop, the part becomes a likely root cause.
