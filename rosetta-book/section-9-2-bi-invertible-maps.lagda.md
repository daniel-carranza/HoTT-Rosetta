# Section 9.2 Bi-invertible maps

```agda
module section-9-2-bi-invertible-maps where
```

<!-- rosetta-item: section-9.2 -->

We use homotopies to define sections and retractions of a map `f`, and to define what it means for a map `f` to be an equivalence.

## Definition 9.2.1

<!-- rosetta-item: definition-9.2.1 -->

Let `f:A→ B` be a function.

1.  The type of **sections** of `f` is defined to be the type
```text
sec(f) ≔ Σ(g:B→ A) f∘ g~ id[B].
```
In other words, a **section** of `f` is a map `g:B→ A` equipped with a homotopy `f∘ g~ id`.

2.  The type of **retractions** of `f` is defined to be the type
```text
retr(f) ≔ Σ(h:B→ A) h∘ f~ id[A].
```
If a map `f:A → B` has a retraction, we also say that `A` is a **retract** of `B`.

3.  We say that a function `f:A→ B` is an **equivalence** if it has both a section and a retraction, i.e., if it comes equipped with an element of type
```text
is-equiv(f)≔sec(f)×retr(f).
```
We will write `A ≃ B` for the type `Σ(f:A→ B) is-equiv(f)` of all equivalences from `A` to `B`.
For any equivalence `e:A≃ B` we define `e^{-1}` to be the section of `e`.

## Remark 9.2.2

<!-- rosetta-item: remark-9.2.2 -->

An equivalence, as we defined it here, can be thought of as a *bi-invertible map*, since it comes equipped with a separate left and right inverse.
Explicitly, if `f` is an equivalence, then there are
```text
g : B→ A h : B→ A
G : f∘ g ~ id[B] H : h∘ f ~ id[A].
```

## Example 9.2.3

<!-- rosetta-item: example-9.2.3; latex-label: thm:id_equiv -->

For any type `A`, the identity function `id:A→ A` is an equivalence, since it is its own section and its own retraction

## Example 9.2.4

<!-- rosetta-item: example-9.2.4; latex-label: ex:neg_equiv -->

Since we have seen in Remark 9.1.1 that the negation function `neg-bool:bool→bool` on the booleans is its own inverse, it follows that `neg-bool` is an equivalence.

## Example 9.2.5

<!-- rosetta-item: example-9.2.5; latex-label: eg:is-equiv-succ-Z -->

The successor and predecessor functions on `ℤ` are equivalences by Exercise 5.6.
Furthermore, the function
```text
x↦ x+k
```
is an equivalence from `ℤ` to `ℤ`, for each `k:ℤ`.
This follows from the group laws on `ℤ`, proven in Exercise 5.7.
Indeed, the inverse of `x↦ x+k` is the map `x↦ x+(-k)`.
Finally, it also follows from the group laws on `ℤ` that the map `x↦ -x` is an equivalence.

The same holds for the finite types: the maps `succ-Fin_{k}`, `pred-Fin_{k}`, `add-Fin_{k}(x)` and `neg-Fin_{k}` are all equivalences on `Fin{k}`.

## Remark 9.2.6

<!-- rosetta-item: remark-9.2.6; latex-label: rmk:has-inverse -->

More generally, if `f` **has an inverse** in the sense that we have a function `g:B→ A` equipped with homotopies `f∘ g~id[B]` and `g∘ f~id[A]`, then `f` is an equivalence.
We write
```text
has-inverse(f)≔Σ(g:B→ A) (f∘ g~ id[B])× (g∘ f~id[A]).
```
However, we did *not* define equivalences to be functions that have inverses.
The reason is that we would like that being an equivalence is a *property*, not a non-trivial structure on the map `f`.
This fact requires the function extensionality axiom, but we can already say that if a map `f` is an equivalence, then it has up to homotopy only one section and only one retraction (see Exercise 13.4).

The type `has-inverse(f)` on the other hand, turns out to be homotopically complicated.
In Exercise 22.5 we will see that the identity function `id[S^1]:S^1→S^1` on the circle is an example of a map for which
```text
has-inverse(id[S^1])≃ ℤ.
```

Even though `is-equiv(f)` and `has-inverse(f)` can be wildly different types, there are maps back and forth between the two.
We have already observed in Remark 9.2.6 that there is a map
```text
has-inverse(f)→is-equiv(f).
```
The following proposition gives the converse implication.

## Proposition 9.2.7

<!-- rosetta-item: proposition-9.2.7; latex-label: lem:inv_equiv -->

Any map `f:A→ B` which is an equivalence, can be given the structure of an invertible map i.e., there is a map
```text
is-equiv(f)→has-inverse(f).
```

### Proof

<!-- rosetta-item: subheading-9.2-proof -->

*Proof.* First we construct for any equivalence `f` with right inverse `g` and left inverse `h` a homotopy `K:g~ h`.
For any `y:B`, we have
<!-- rosetta-diagram: cd2afc403d22; review: pending -->

*Linear diagram (automatic draft).*

```text
[g(y)]---->[hfg(y)]---->[h(y)]

Arrows:
- g(y) --H(g(y))^{-1}--> hfg(y)
- hfg(y) --ap_{h}(G(y))--> h(y)
```
In other words, the homotopy `K:g~ h` is defined to be `(H· g)^{-1} ∙ (h· G)`.
Using the homotopy `K` we are able to show that `g` is also a left inverse of `f`.
For `x:A` we have the identification
<!-- rosetta-diagram: c4fea148de3a; review: pending -->

*Linear diagram (automatic draft).*

```text
[gf(x)]---->[hf(x)]----> [x]

Arrows:
- gf(x) --K(f(x))--> hf(x)
- hf(x) --H(x)--> x
```
 ◻

## Corollary 9.2.8

<!-- rosetta-item: corollary-9.2.8 -->

The inverse of an equivalence is again an equivalence.

### Proof

<!-- rosetta-item: subheading-9.2-proof-2 -->

*Proof.* Let `f:A→ B` be an equivalence.
By Proposition 9.2.7 it follows that the section of `f` is also a retraction.
Therefore it follows that the section is itself an invertible map, with inverse `f`.
Hence it is an equivalence. ◻

## Example 9.2.9

<!-- rosetta-item: example-9.2.9; latex-label: eg:laws-products-coproducts -->

Types, just as sets in classical mathematics, satisfy the usual laws of coproducts and products, such as unit laws, commutativity, and associativity.
These laws are formulated as equivalences:
```text
empty+B ≃ B A+empty ≃ A
A+B ≃ B+A (A+B)+C ≃ A+(B+C)
empty× B ≃ empty A×empty ≃ empty
unit× B ≃ B A×unit ≃ A
A× B ≃ B× A (A × B) × C ≃ A × (B × C)
A× (B+C) ≃ (A× B)+(A× C) (A+B)× C ≃ (A× C)+(B× C).
```
All of these equivalences are constructed in a similar way: the maps back and forth as well as the required homotopies are constructed using induction, or, more efficiently, using pattern matching.
For example, to show that cartesian products distribute from the left over coproducts, we construct maps
```text
α : A×(B+C)→ (A× B)+(A× C)
β : (A× B)+(A× C)→ A×(B+C)
```
as follows:
```text
α(x,inl(y)) ≔ inl(x,y) β(inl(x,y)) ≔ (x,inl(y))
α(x,inr(z)) ≔ inr(x,z) β(inr(x,z)) ≔ (x,inr(z)).
```
The homotopies `G:α∘β~id` and `H:β∘α~ id` are then defined by
```text
G(inl(x,y)) ≔ refl H(x,inl(y)) ≔ refl
G(inr(x,z)) ≔ refl H(x,inr(z)) ≔ refl.
```
We encourage the reader to write out the definitions of at least a few of these equivalences.

## Example 9.2.10

<!-- rosetta-item: example-9.2.10; latex-label: eg:laws-Sigma-types -->

The laws for cartesian products can be generalized to arbitrary `Σ`-types.
The absorption laws and unit laws, for instance, are as follows:
```text
Σ(x:empty) B(x) ≃ empty Σ(x:A) empty ≃ empty
Σ(x:unit) B(x) ≃ B(⋆) Σ(x:A) unit ≃ A.
```
Note that the right absorption law and the right unit law are exactly the same as the right absorption and unit laws for cartesian products.
The left absorption and unit laws are, however, formulated with a type family `B` over `empty` and over `unit`, and therefore they are slightly more general.

Commutativity cannot be generalized to `Σ`-types.
Associativity, on the other hand, can be expressed in two ways:
```text
Σ(w:Σ(x:A) B(x)) C(w) ≃Σ(x:A) Σ(y:B) C(pair(x,y))
Σ(w:Σ(x:A) B(x)) C(pr 1(w),pr 2(w)) ≃ Σ(x:A) Σ(y:B(x)) C(x,y).
```
In the first of these equivalences associativity is stated using a type family `C` over `Σ(x:A) B(x)` while in the second it is stated using a family of types `C(x,y)` indexed by `x:A` and `y:B(x)`.

Finally, we note that `Σ` also distributes over coproducts.
In other words, there are the following two equivalences:
```text
Σ(x:A) B(x)+C(x) ≃ (Σ(x:A) B(x))+(Σ(x:A) C(x))
Σ(w:A+B) C(w) ≃ (Σ(x:A) C(inl(x)))+(Σ(y:B) C(inr(y))).
```

## Remark 9.2.11

<!-- rosetta-item: remark-9.2.11 -->

We haven’t stated any laws involving function types or dependent function types, because it requires the function extensionality principle to prove them.
