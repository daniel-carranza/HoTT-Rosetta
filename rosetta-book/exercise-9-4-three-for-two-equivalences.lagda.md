# Exercise 9.4

```agda
module exercise-9-4-three-for-two-equivalences where

```

## Problem statement

Consider a commuting triangle
<!-- rosetta-diagram: cdb284b42255; review: pending -->

*Triangle-shaped diagram (automatic draft).*

```text
 [A]                 [B]

           [X]

Arrows:
- A --h--> B
- A --f--> X
- B --g--> X
```
with `H:f~ g∘ h`.

<div class="subexenum">

Suppose that the map `h` has a section `s:B → A`.
Show that the triangle
<!-- rosetta-diagram: 5c672de7e457; review: pending -->

*Triangle-shaped diagram (automatic draft).*

```text
 [B]                 [A]

           [X]

Arrows:
- B --s--> A
- B --g--> X
- A --f--> X
```
commutes, and that `f` has a section if and only if `g` has a section.

Suppose that the map `g` has a retraction `r:X→ B`.
Show that the triangle
<!-- rosetta-diagram: 32d6c414af56; review: pending -->

*Triangle-shaped diagram (automatic draft).*

```text
 [A]                 [X]

           [B]

Arrows:
- A --f--> X
- A --h--> B
- X --r--> B
```
commutes, and that `f` has a retraction if and only if `h` has a retraction.

(The **3-for-2 property** for equivalences.) Show that if any two of the functions
```text
f, g, h
```
are equivalences, then so is the third.
Conclude that any section and any retraction of an equivalence is again an equivalence.

</div>

## Solution

<!-- rosetta-item: exercise-9-4 -->

No formalization has been curated yet.
