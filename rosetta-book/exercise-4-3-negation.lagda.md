# Exercise 4.3

```agda
module exercise-4-3-negation where

open import universe-levels
open import section-4-3-the-empty-type
open import section-4-4-coproducts
open import section-4-6-dependent-pair-types
```

## Problem statement

Let `P` and `Q` be types.
We will write `P↔ Q` for the type of **bi-implications** `{(P→ Q)}× {(Q→ P)}`.
Use the fact that `¬ P` is defined as the type `P→empty` of functions from `P` to the empty type to give type theoretic proofs of the constructive tautologies in this exercise.<div class="subexenum">

Show that

1.  `¬(P× ¬ P)`

2.  `¬(P↔ ¬ P)`.

Construct the following maps in the structure of the **double negation monad**:

1.  `P→¬¬ P`

2.  `(P→ Q)→(¬¬ P→¬¬ Q)`

3.  `(P→ ¬¬ Q)→ (¬¬ P →¬¬ Q)`.

Prove that the following double negations of classical laws hold:

1.  `¬¬(¬¬ P → P)`

2.  `¬¬(((P→ Q)→ P)→ P)`

3.  `¬¬((P→ Q)+(Q→ P))`

4.  `¬¬(P+¬ P)`.

Show that

1.  `(P+¬ P)→(¬¬ P→ P)`

2.  `¬¬(Q→ P)↔ ((P+¬ P)→ (Q→ P))`.

Prove the following tautologies, showing that `¬ P`, `P→¬¬ Q`, and `¬¬ P×¬¬ Q` are **double negation stable**:

1.  `¬¬¬ P → ¬ P`

2.  `¬¬(P → ¬¬ Q)→ (P→¬¬ Q)`

3.  `¬¬((¬¬ P)×(¬¬ Q))→ (¬¬ P)×(¬¬ Q)`.

Show that

1.  `¬¬(P× Q)↔ (¬¬ P)×(¬¬ Q)`

2.  `¬¬(P+Q)↔ ¬ (¬ P × ¬ Q)`

3.  `¬¬(P→ Q)↔ (¬¬ P→¬¬ Q)`.

</div>

## Solution

<!-- rosetta-item: exercise-4-3 -->

<!-- rosetta-agda-block: exercise-4-3-law-of-non-contradiction-local -->

```agda
law-of-non-contradiction : {l : Level} {P : Type l} → ¬ (P × ¬ P) 
law-of-non-contradiction (p , np) = np p
```

<!-- rosetta-agda-block: exercise-4-3-bi-implication-non-contradiction-local -->

```agda
iff : {l1 l2 : Level} (A : Type l1) (B : Type l2) → Type (l1 ⊔ l2)
iff A B = (A → B) × (B → A) 

infixr 15 _↔_
_↔_ : {l1 l2 : Level} (A : Type l1) (B : Type l2) → Type (l1 ⊔ l2)
_↔_ = iff

law-of-non-contradiction' : {l : Level} {P : Type l} → ¬ (P ↔ (¬ P))
law-of-non-contradiction' {P = P} (pnp , npp) = nnp np
    where 
        np : ¬ P  
        np p = (pnp p) p 

        nnp : ¬ ¬ P 
        nnp np = np (npp np)
```

<!-- rosetta-agda-block: exercise-4-3-double-negation-introduction-local -->

```agda
double-negation-introduction : {l : Level} {P : Type l} → P → ¬¬ P 
double-negation-introduction p np = np p
```

<!-- rosetta-agda-block: exercise-4-3-double-negation-map-local -->

```agda
double-negation-map : {l1 l2 : Level} {P : Type l1} {Q : Type l2} → (P → Q) → (¬¬ P → ¬¬ Q)
double-negation-map pq nnp nq = nnp (λ p → nq (pq p))
```

<!-- rosetta-agda-block: exercise-4-3-double-negation-kleisli-map-local -->

```agda
double-negation-kleisli-map : {l1 l2 : Level} {P : Type l1} {Q : Type l2} → (P → ¬¬ Q) → (¬¬ P → ¬¬ Q)
double-negation-kleisli-map {Q = Q} pnnq nnp = mu (double-negation-map pnnq nnp)
    where 
        mu : ¬¬ ¬¬ Q → ¬¬ Q
        mu nnnnq nq = nnnnq (λ nnq → nnq nq)
```

<!-- rosetta-agda-block: exercise-4-3-not-not-double-negation-elimination-local -->

```agda
not-not-double-negation-elimination : {l : Level} {P : Type l} → ¬¬(¬¬ P → P)
not-not-double-negation-elimination {P = P} ndne = ndne (λ nnp → ex-falso (nnp np))
    where 
        np : ¬ P
        np p = ndne (λ _ → p)
```

<!-- rosetta-agda-block: exercise-4-3-not-not-lem-local -->

```agda
not-not-lem : {l : Level} {P : Type l} → ¬¬ (P + (¬ P)) 
not-not-lem {P = P} nlem = nnp np
    where 
        np : ¬ P
        np p = nlem (inl p)

        nnp : ¬¬ P
        nnp np' = nlem (inr np')
```
