# Edge Case Analyzer

## Purpose
Identify realistic edge cases for public API testing in the panw-takehome framework
without introducing brittle or speculative tests. This skill helps separate useful test
ideas from hallucinated or low-value scenarios.

## Use when
- Exploring edge coverage for a new endpoint
- Reviewing whether an existing test suite is too happy-path focused
- Deciding which negative cases are worth implementing for public third-party APIs

## Required inputs
- Endpoint path
- HTTP method
- Short description of expected response shape
- Any business or domain invariants already known

## Output requirements
- Return edge cases grouped by category
- Label each edge case as:
  - high-value
  - optional
  - likely hallucinated / low-value
- Explain why each case matters
- Recommend whether to automate it in this framework

## Framework constraints
- Prefer durable edge cases over brittle data assumptions
- Respect that this framework tests public third-party APIs
- Avoid suggesting exact-value assertions for volatile data
- Prioritize schema, SLA, missing fields, empty results, and domain-boundary conditions

## Do not
- Suggest internal-only failure modes with no public evidence
- Recommend fragile snapshot assertions
- Assume undocumented API behavior

## Example
Input:
- GET `/forecast`
- fields: `hourly.temperature_2m`, `timezone`

Expected output characteristics:
- Suggests missing timezone, empty hourly array, out-of-range temperatures, slow response
- Marks impossible or speculative cases as low confidence
- Recommends only robust cases for implementation
