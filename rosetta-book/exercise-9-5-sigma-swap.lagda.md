# Exercise 9.5

```agda
module exercise-9-5-sigma-swap where

```

## Problem statement

<div class="subexenum">

Let `A` and `B` be types, and let `C` be a family over `x:A,y:B`.
Construct an equivalence
```text
(Σ(x:A) Σ(y:B) C(x,y)) ≃ (Σ(y:B) Σ(x:A) C(x,y)).
```

Let `A` be a type, and let `B` and `C` be type families over `A`.
Construct an equivalence
```text
(Σ(u:Σ(x:A) B(x)) C(pr 1(u))) ≃ (Σ(v:Σ(x:A) C(x)) B(pr 1(v))).
```

</div>

## Solution

<!-- rosetta-item: exercise-9-5 -->

No formalization has been curated yet.
