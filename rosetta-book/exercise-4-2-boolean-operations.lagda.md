# Exercise 4.2

```agda
module exercise-4-2-boolean-operations where

open import universe-levels
```

## Problem statement

The type of **booleans** is defined to be an inductive type `bool` that comes equipped with
```text
false : bool and true : bool.
```
The induction principle of the booleans asserts that for any family of types `P(x)` indexed by `x:bool`, there is a term
```text
ind-bool : P(false)→ (P(true)→ Π(x:bool) P(x))
```
for which the computation rules
```text
ind-bool(p_0,p_1,false) ≐ p_0
ind-bool(p_0,p_1,true) ≐ p_1
```
hold.

<div class="subexenum">

Construct the **boolean negation** function `neg-bool:bool→bool`.

Construct the **boolean conjunction** operation `_∧_ : bool→(bool→bool)`.

Construct the **boolean disjunction** operation `_∨_ : bool→(bool→bool)`.

</div>

## Solution

<!-- rosetta-item: exercise-4-2 -->

<!-- rosetta-agda-block: exercise-4-2-booleans-adapted -->

```agda
data bool : Type lzero where
  true false : bool

ind-bool : {l : Level} {P : bool → Type l} → P true → P false → (b : bool) → P b
ind-bool pt pf true = pt
ind-bool pt pf false = pf
```

<!-- rosetta-agda-block: exercise-4-2-boolean-negation -->

```agda
neg-bool : bool → bool
neg-bool true = false
neg-bool false = true
```

<!-- rosetta-agda-block: exercise-4-2-boolean-conjunction-adapted -->

```agda
and-bool : bool → bool → bool
and-bool true q = q
and-bool false q = false
```

<!-- rosetta-agda-block: exercise-4-2-boolean-disjunction-adapted -->

```agda
or-bool : bool → bool → bool
or-bool true q = true
or-bool false q = q
```
