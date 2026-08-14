# Exercise 3.5

```agda
module exercise-3-5-fibonacci-sequence where

open import section-3-1-the-formal-specification-of-the-type-of-natural-numbers
open import section-3-2-addition-on-the-natural-numbers
```

## Problem statement

Use the induction principle of `ℕ` to define the **Fibonacci sequence** as a function `F:ℕ→ℕ` that satisfies the equations

```text
F(0) ≐ 0
F(1) ≐ 1
F(succ-ℕ(succ-ℕ(n))) ≐ F(succ-ℕ(n))+F(n).
```

## Solution

<!-- rosetta-item: exercise-3-5 -->

<!-- rosetta-agda-block: exercise-3-5-fibonacci-sequence-block-1 -->

```agda
Fibonacci-ℕ : ℕ → ℕ
Fibonacci-ℕ 0 = 0
Fibonacci-ℕ (succ-ℕ 0) = 1
Fibonacci-ℕ (succ-ℕ (succ-ℕ n)) = (Fibonacci-ℕ (succ-ℕ n)) +ℕ (Fibonacci-ℕ n)
```

<!-- rosetta-agda-block: exercise-3-5-fibonacci-sequence-block-2 -->

```agda
shift-one : ℕ → (ℕ → ℕ) → (ℕ → ℕ)
shift-one n f = ind-ℕ n (λ x y → f x)

shift-two : ℕ → ℕ → (ℕ → ℕ) → (ℕ → ℕ)
shift-two m n f = shift-one m (shift-one n f)

Fibo-zero-ℕ : ℕ → ℕ
Fibo-zero-ℕ = shift-two 0 1 (λ x → 0)

Fibo-succ-ℕ : (ℕ → ℕ) → (ℕ → ℕ)
Fibo-succ-ℕ f = shift-two (f 1) ((f 1) +ℕ (f 0)) (λ x → 0)

Fibo-function : ℕ → ℕ → ℕ
Fibo-function =
  ind-ℕ
    ( Fibo-zero-ℕ)
    ( λ n → Fibo-succ-ℕ)

Fibo : ℕ → ℕ
Fibo k = Fibo-function k 0
```
