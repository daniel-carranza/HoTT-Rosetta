# Exercise 3.1

```agda
module exercise-3-1-multiplication-and-exponentiation where

open import section-3-1-the-formal-specification-of-the-type-of-natural-numbers
open import section-3-2-addition-on-the-natural-numbers
open import universe-levels
```

## Problem statement

<div class="subexenum">

Define the **multiplication** operation
```text
mul :ℕ→(ℕ→ℕ).
```

Define the **exponentiation function** `n,m↦ m^n` of type `ℕ→ (ℕ→ ℕ)`.

</div>

## Solution

<!-- rosetta-item: exercise-3-1 -->

<!-- rosetta-agda-block: exercise-3-1-multiplication-and-exponentiation-block-1 -->

```agda
mul-ℕ : ℕ → ℕ → ℕ
mul-ℕ 0 n = 0
mul-ℕ (succ-ℕ m) n = (mul-ℕ m n) +ℕ n

infixl 40 _*ℕ_
_*ℕ_ = mul-ℕ

{-# BUILTIN NATTIMES _*ℕ_ #-}

mul-ℕ' : ℕ → ℕ → ℕ
mul-ℕ' x y = mul-ℕ y x
```

<!-- rosetta-agda-block: exercise-3-1-multiplication-and-exponentiation-block-2 -->

```agda
exp-ℕ : ℕ → ℕ → ℕ
exp-ℕ m zero-ℕ = 1
exp-ℕ m (succ-ℕ zero-ℕ) = m
exp-ℕ m (succ-ℕ (succ-ℕ n)) = mul-ℕ (exp-ℕ m (succ-ℕ n)) m

infixr 45 _^ℕ_
_^ℕ_ = exp-ℕ
```
