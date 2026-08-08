# Exercise 2.4

```agda
module exercise-2-4-exercise where

```

## Problem statement

<div class="subexenum">

Define the **swap function**

<!-- rosetta-proof-tree: d7366097dc2c; review: pending -->

*Proof tree (automatic faithful draft).*

```text
  Γ⊢ A type   Γ⊢ B type   Γ,x:A,y:B⊢ C(x,y) type
──────────────────────────────────────────────────
Γ⊢ σ:(Π(x:A) Π(y:B) C(x,y))→(Π(y:B) Π(x:A) C(x,y))
```

that swaps the order of the arguments.

Show that

</div>

<div class="small">

<!-- rosetta-proof-tree: e2ad895faccd; review: pending -->

*Proof tree (automatic faithful draft).*

```text
     Γ⊢ A type   Γ⊢ B type   Γ,x:A,y:B⊢ C(x,y) type
────────────────────────────────────────────────────────
Γ⊢ σ∘σ≐id:(Π(x:A) Π(y:B) C(x,y))→ (Π(x:A) Π(y:B) C(x,y))
```

</div>

## Solution

<!-- rosetta-item: exercise-2-4 -->

No formalization has been curated yet.
