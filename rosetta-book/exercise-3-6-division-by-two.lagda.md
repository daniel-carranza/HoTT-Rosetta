# Exercise 3.6

```agda
module exercise-3-6-division-by-two where

open import section-3-1-the-formal-specification-of-the-type-of-natural-numbers
```

## Problem statement

Define division by two rounded down as a function `ℕ→ℕ` in two ways: first by pattern matching, and then directly by the induction principle of `ℕ`.

## Solution

<!-- rosetta-item: exercise-3-6 -->

<!-- rosetta-agda-block: exercise-3-6-division-by-two-block-1 -->

```agda
division-by-two : ℕ → ℕ 
division-by-two zero-ℕ = 0
division-by-two (succ-ℕ zero-ℕ) = 0
division-by-two (succ-ℕ (succ-ℕ n)) = succ-ℕ (division-by-two n)
```
