# Exercise 11.8

```agda
module exercise-11-8-total-map-retractions where

```

## Problem statement

<div class="subexenum">

Let `f,g:Π(x:A) B(x)→ C(x)` be two families of maps.
Show that
```text
(Π(x:A) f(x)~ g(x))→ (tot(f)~ tot(g)).
```

Let `f:Π(x:A) B(x)→ C(x)` and let `g:Π(x:A) C(x)→ D(x)`.
Show that
```text
tot(λ x. g(x)∘ f(x))~ tot(g)∘tot(f).
```

For any family `B` over `A`, show that
```text
tot(λ x. id[B(x)])~id.
```

Let `a:A`, and let `B` be a type family over `A`.
Use Exercise 10.2 to show that if each `B(x)` is a retract of `a = x`, then `B(x)` is equivalent to `a = x` for every `x:A`.

Conclude that for any family of maps
```text
f : Π(x:A) (a=x) → B(x),
```
if each `f(x)` has a section, then `f` is a family of equivalences.

</div>

## Solution

<!-- rosetta-item: exercise-11-8 -->

No formalization has been curated yet.
