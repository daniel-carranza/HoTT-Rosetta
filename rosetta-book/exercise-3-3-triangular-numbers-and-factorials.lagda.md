# Exercise 3.3

```agda
module exercise-3-3-triangular-numbers-and-factorials where

open import section-3-1-the-formal-specification-of-the-type-of-natural-numbers
open import section-3-2-addition-on-the-natural-numbers
open import exercise-3-1-multiplication-and-exponentiation
```

## Problem statement

<div class="subexenum">

Define the **triangular numbers**
```text
1+⋯+n.
```

Define the **factorial** operation `n↦ n!`.

</div>

## Solution

<!-- rosetta-item: exercise-3-3 -->

<!-- rosetta-agda-block: exercise-3-3-triangular-numbers-and-factorials-block-1 -->

```agda
inductive-triangular-number-ℕ : ℕ → ℕ
inductive-triangular-number-ℕ 0 = 0
inductive-triangular-number-ℕ (succ-ℕ n) =
  inductive-triangular-number-ℕ n +ℕ succ-ℕ n
```

<!-- rosetta-agda-block: exercise-3-3-triangular-numbers-and-factorials-block-2 -->

```agda
factorial-ℕ : ℕ → ℕ
factorial-ℕ 0 = 1
factorial-ℕ (succ-ℕ m) = (factorial-ℕ m) *ℕ (succ-ℕ m)
```
