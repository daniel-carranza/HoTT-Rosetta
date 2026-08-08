# Exercise 10.7

```agda
module exercise-10-7-fibers-of-projections where

```

## Problem statement

Let `B` be a family of types over `A`, and consider the projection map
```text
pr 1 : (Σ(x:A) B(x))→ A.
```

<div class="subexenum">

Show that for any `a:A`, the map
```text
λ ((x,y),p). tr_B(p,y) : fib(pr 1, a) → B(a),
```
is an equivalence.

Show that the following are equivalent:

1.  The projection map `pr 1` is an equivalence.

2.  The type `B(x)` is contractible for each `x:A`.

Consider a dependent function `b:Π(x:A) B(x)`.
Show that the following are equivalent:

1.  The map
```text
λ x. (x,b(x)) : A → Σ(x:A) B(x)
```
    is an equivalence.

2.  The type `B(x)` is contractible for each `x:A`.

</div>

## Solution

<!-- rosetta-item: exercise-10-7 -->

No formalization has been curated yet.
