# Exercise 4.4

```agda
module exercise-4-4-lists where

open import universe-levels
open import section-3-1-the-formal-specification-of-the-type-of-natural-numbers
open import section-3-2-addition-on-the-natural-numbers
open import exercise-3-1-multiplication-and-exponentiation
```

## Problem statement

For any type `A` we can define the type `list(A)` of **lists** of elements of `A` as the inductive type with constructors
```text
nil : list(A)
cons : A → (list(A) → list(A)).
```

<div class="subexenum">

Write down the induction principle and the computation rules for `list(A)`.

Let `A` and `B` be types, suppose that `b:B`, and consider a binary operation `μ:A→ (B → B)`.
Define a function
```text
fold-list(μ) : list(A)→ B
```
that iterates the operation `μ`, starting with `fold-list(μ,nil)≔ b`.

Define the operation
```text
map-list : (A→ B) → (list(A)→list(B))
```
for any two types `A` and `B`.

Define a function `length-list:list(A)→ℕ`.

Define the functions
```text
sum-list : list(ℕ) → ℕ
product-list : list(ℕ)→ℕ,
```
where `sum-list` adds all the elements in a list of natural numbers, and `product-list` takes their product.

Define a function
```text
concat-list : list(A) → (list(A) → list(A))
```
that concatenates any two lists of elements in `A`.

Define a function
```text
flatten-list : list(list(A)) → list(A)
```
that concatenates all the lists in a lists of lists in `A`.

Define a function `reverse-list : list(A) → list(A)` that reverses the order of the elements in any list.

</div>

## Solution

<!-- rosetta-item: exercise-4-4 -->

<!-- rosetta-agda-block: exercise-4-4-list-type-local -->

```agda
data list {l : Level} (A : Type l) : Type l where
  nil : list A
  cons : A → (list A) → (list A)
```

<!-- rosetta-agda-block: exercise-4-4-list-induction-local -->

```agda
ind-list :
  {l1 l2 : Level} (A : Type l1) → (P : list A → Type l2) → P nil →
  ((a : A) (as : list A) → P as → P (cons a as)) → (x : list A) → P x
ind-list A P Pnil Pcons nil = Pnil
ind-list A P Pnil Pcons (cons a as) = Pcons a as (ind-list A P Pnil Pcons as)
```

<!-- rosetta-agda-block: exercise-4-4-fold-list-local -->

```agda
fold-list :
  {l1 l2 : Level} {A : Type l1} {B : Type l2} (b : B)
  (μ : A → B → B) → list A → B
fold-list b μ nil = b
fold-list b μ (cons a l) = μ a (fold-list b μ l)
```

<!-- rosetta-agda-block: exercise-4-4-map-list-local -->

```agda
map-list :
  {l1 l2 : Level} {A : Type l1} {B : Type l2} → (A → B) → list A → list B
map-list f = fold-list nil (λ a → cons (f a))
```

<!-- rosetta-agda-block: exercise-4-4-map-list-direct-local -->

```agda
map-list2 :
  {l1 l2 : Level} {A : Type l1} {B : Type l2} → (A → B) → list A → list B
map-list2 f nil = nil
map-list2 f (cons a l) = cons (f a) (map-list f l)
```

<!-- rosetta-agda-block: exercise-4-4-length-list-adapted -->

```agda
length-list : {l : Level} {A : Type l} → list A → ℕ
length-list = fold-list 0 (λ a → succ-ℕ)
```

<!-- rosetta-agda-block: exercise-4-4-length-list-direct-local -->

```agda
length-list2 : {l : Level} {A : Type l} → list A → ℕ
length-list2 nil = 0
length-list2 (cons x l) = succ-ℕ (length-list l)
```

<!-- rosetta-agda-block: exercise-4-4-sum-list-local -->

```agda
sum-list : list ℕ → ℕ
sum-list = fold-list 0 add-ℕ
```

<!-- rosetta-agda-block: exercise-4-4-product-list-local -->

```agda
prod-list : list ℕ → ℕ
prod-list = fold-list 1 mul-ℕ
```

<!-- rosetta-agda-block: exercise-4-4-concat-list-local -->

```agda
concat-list : {l : Level} {A : Type l} → list A → list A → list A
concat-list l1 l2 = (fold-list l2 cons) l1
```

<!-- rosetta-agda-block: exercise-4-4-concat-list-alternative-local -->

```agda
concat-list2 : {l : Level} {A : Type l} → list A → list A → list A
concat-list2 l1 = fold-list l1 cons
```

<!-- rosetta-agda-block: exercise-4-4-flatten-list-adapted -->

```agda
flatten-list : {l : Level} {A : Type l} → list (list A) → list A
flatten-list = fold-list nil concat-list
```

<!-- rosetta-agda-block: exercise-4-4-reverse-list-local -->

```agda
reverse-list : {l : Level} {A : Type} → list A → list A
reverse-list nil = nil
reverse-list (cons a l) = concat-list l (cons a nil)
```
