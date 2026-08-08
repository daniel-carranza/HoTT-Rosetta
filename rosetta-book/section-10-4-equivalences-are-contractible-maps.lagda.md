# Section 10.4 Equivalences are contractible maps

```agda
module section-10-4-equivalences-are-contractible-maps where
```

<!-- rosetta-item: section-10.4 -->

In Theorem 10.4.6 we will show the converse to Theorem 10.3.5, i.e., we will show that any equivalence is a contractible map.
We will do this in two steps.

First we introduce a new notion of *coherently invertible map*, for which we can easily show that such maps have contractible fibers.
Then we show that any equivalence is a coherently invertible map.

Recall that an invertible map is a map `f:A→ B` equipped with `g:B→ A` and homotopies
```text
G : f∘ g ~ id and H:g∘ f~ id.
```
Then we observe that both `G · f` and `f · H` are homotopies of the same type
```text
f∘ g∘ f ~ f.
```
A coherently invertible map is an invertible map for which there is a further homotopy `G · f~ f· H`.

## Definition 10.4.1

<!-- rosetta-item: definition-10.4.1 -->

Consider a map `f:A→ B`.
We say that `f` is **coherently invertible** if it comes equipped with
```text
g : B → A
G : f ∘ g ~ id
H : g ∘ f ~ id
K : G · f ~ f · H.
```
We will write `is-coh-invertible(f)` for the type of quadruples `(g,G,H,K)`.

Although we will encounter the notion of coherently invertible map on some further occasions, the following proposition is our main motivation for considering it.

## Proposition 10.4.2

<!-- rosetta-item: proposition-10.4.2; latex-label: lem:contr-inv -->

Any coherently invertible map has contractible fibers.

### Proof

<!-- rosetta-item: subheading-10.4-proof -->

*Proof.* Consider a map `f:A→ B` equipped with
```text
g : B → A
G : f ∘ g ~ id
H : g ∘ f ~ id
K : G · f ~ f · H,
```
and let `y:B`.
Our goal is to show that `fib(f, y)` is contractible.
For the center of contraction we take `(g(y),G(y))`.
In order to construct a contraction, it suffices to construct a dependent function of type
```text
Π(x:A) Π(p:f(x)=y) Eq-fib_f((g(y),G(y)),(x,p)).
```
By path induction on `p:f(x)=y` it suffices to construct a dependent function of type
```text
Π(x:A) Eq-fib_f((g(f(x)),G(f(x))),(x,refl)).
```
By definition of `Eq-fib_f`, we have to construct for each `x:A` an identification `α:g(f(x))=x` equipped with a further identification
```text
G(f(x))=ap_{f}(α) ∙ refl.
```
Such a dependent function is constructed as `λ x. (H(x),K'(x))`, where the homotopy `H:g∘ f~ id` is given by assumption, and the homotopy
```text
K' : Π(x:A) G(f(x))=ap_{f}(H(x)) ∙ refl
```
is defined as
```text
K'≔ K ∙ right-unit-htpy(f· H)^{-1}.
```
 ◻

Our next goal is to show that for any map `f:A→ B` equipped with
```text
g:B→ A, G:f∘ g ~ id, and H:g∘ f~ id,
```
we can improve the homotopy `G` to a new homotopy `G':f∘ g~ id` for which there is a further homotopy
```text
f· H~ G'· f.
```
Note that this situation is analogous to the situation in the proof of Theorem 10.2.3, where we improved the contraction `C` so that it satisfied `C(c)=refl`.
The extra coherence `f· H~ G'· f` is then used in the proof that the fibers of an equivalence are contractible.

## Definition 10.4.3

<!-- rosetta-item: definition-10.4.3; latex-label: defn:htpy_nat -->

Let `f,g:A→ B` be functions, and consider `H:f~ g` and `p:x=y` in `A`.
We define the identification
```text
nat-htpy(H,p) ≔ ap_{f}(p) ∙ H(y)=H(x) ∙ ap_{g}(p)
```
witnessing that the square
<!-- rosetta-diagram: a2f4fce2f636; review: pending -->

*Square-shaped diagram (automatic draft).*

```text
[f(x)]---->[g(x)]
  |          |
[f(y)]---->[g(y)]

Arrows:
- f(x) --H(x)--> g(x)
- f(x) --ap_{f}(p)--> f(y)
- g(x) --ap_{g}(p)--> g(y)
- f(y) --H(y)--> g(y)
```
commutes.
This square is also called the **naturality square** of the homotopy `H` at `p`.

### Construction

<!-- rosetta-item: subheading-10.4-construction -->

By path induction on `p` it suffices to construct an identification
```text
ap_{f}(refl) ∙ H(x)=H(x) ∙ ap_{g}(refl)
```
since `ap_{f}(refl)≐ refl` and `ap_{g}(refl)≐refl`, and since `refl ∙ H(x)≐ H(x)`, we see that the path `right-unit(H(x))^{-1}` is of the asserted type.

## Definition 10.4.4

<!-- rosetta-item: definition-10.4.4; latex-label: defn:retraction_swap -->

Consider `f:A→ A` and `H: f~ id[A]`.
We construct an identification `H(f(x))=ap_{f}(H(x))`, for any `x:A`.

### Construction

<!-- rosetta-item: subheading-10.4-construction-2 -->

By the naturality of homotopies with respect to identifications the square
<!-- rosetta-diagram: e9ca675c5778; review: pending -->

*Square-shaped diagram (automatic draft).*

```text
[ff(x)]---->[f(x)]
   |          |
 [f(x)]----> [x]

Arrows:
- ff(x) --ap_{f}(H(x))--> f(x)
- ff(x) --H(f(x))--> f(x)
- f(x) --H(x)--> x
- f(x) --H(x)--> x
```
commutes.
This gives the desired identification `H(f(x))=ap_{f}(H(x))`.

## Lemma 10.4.5

<!-- rosetta-item: lemma-10.4.5; latex-label: lem:coherently-invertible -->

Let `f:A→ B` be a map equipped with an inverse, i.e., consider
```text
g : B → A
G : f ∘ g ~ id
H : g ∘ f ~ id.
```
Then there is a homotopy `G':f∘ g~ id` equipped with a further homotopy
```text
K : f· H ~ G'· f.
```
Thus we obtain a map `has-inverse(f)→is-coh-invertible(f)`.

### Proof

<!-- rosetta-item: subheading-10.4-proof-2 -->

*Proof.* For each `y:B`, we construct the identification `G'(y)` as the concatenation
<!-- rosetta-diagram: b0f70c6cf179; review: pending -->

*Linear diagram (automatic draft).*

```text
[fg(y)]---->[[2.5em] fgfg(y)]---->[[2.5em] fg(y)]----> [y]

Arrows:
- fg(y) --{G(fg(y))}^{-1}--> [2.5em] fgfg(y)
- [2.5em] fgfg(y) --ap_{f}(H(g(y)))--> [2.5em] fg(y)
- [2.5em] fg(y) --G(y)--> y
```
In order to construct a homotopy `f· H ~ G'· f`, it suffices to show that the square
<!-- rosetta-diagram: d894f03c5f8d; review: pending -->

*Square-shaped diagram (automatic draft).*

```text
[fgfgf(x)]---->[fgf(x)]
    |             |
 [fgf(x)] ----> [f(x)]

Arrows:
- fgfgf(x) --{G(fgf(x))}--> fgf(x)
- fgfgf(x) --ap_{f}(H(gf(x)))--> fgf(x)
- fgf(x) --ap_{f}(H(x))--> f(x)
- fgf(x) --G(f(x))--> f(x)
```
commutes for every `x:A`.
Recall from Definition 10.4.4 that we have `H(gf(x))=ap_{gf}(H(x))`.
Using this identification, we see that it suffices to show that the square
<!-- rosetta-diagram: d5e947466295; review: pending -->

*Square-shaped diagram (automatic draft).*

```text
[fgfgf(x)]---->[fgf(x)]
    |             |
 [fgf(x)] ----> [f(x)]

Arrows:
- fgfgf(x) --(G· f)(gf(x))--> fgf(x)
- fgfgf(x) --ap_{fgf}(H(x))--> fgf(x)
- fgf(x) --ap_{f}(H(x))--> f(x)
- fgf(x) --(G· f)(x)--> f(x)
```
commutes.
Now we observe that this is just a naturality square the homotopy `G· f:fgf~ f`, which commutes by Definition 10.4.3. ◻

Now we put the pieces together to conclude that any equivalence has contractible fibers.

## Theorem 10.4.6

<!-- rosetta-item: theorem-10.4.6; latex-label: thm:contr_equiv -->

Any equivalence is a contractible map.

### Proof

<!-- rosetta-item: subheading-10.4-proof-3 -->

*Proof.* We have seen in Proposition 10.4.2 that any coherently invertible map is a contractible map.
Moreover, any equivalence has the structure of an invertible map by Proposition 9.2.7, and any invertible map is coherently invertible by Lemma 10.4.5. ◻

The following corollary is very similar to Theorem 10.1.4, which asserts that the type `Σ(x:A) a=x` is contractible.
However, we haven’t yet established that the equivalence `(a=x)≃ (x=a)` induces an equivalence on total spaces.
However, using the fact that equivalences are contractible maps we can give a direct proof.

## Corollary 10.4.7

<!-- rosetta-item: corollary-10.4.7; latex-label: cor:contr_path -->

Let `A` be a type, and let `a:A`.
Then the type
```text
Σ(x:A) x=a
```
is contractible.

### Proof

<!-- rosetta-item: subheading-10.4-proof-4 -->

*Proof.* By Example 9.2.3, the identity function is an equivalence.
Therefore, the fibers of the identity function are contractible by Theorem 10.4.6.
Note that `Σ(x:A) x=a` is exactly the fiber of `id[A]` at `a:A`. ◻
