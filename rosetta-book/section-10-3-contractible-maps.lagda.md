# Section 10.3 Contractible maps

```agda
module section-10-3-contractible-maps where
```

<!-- rosetta-item: section-10.3 -->

## Definition 10.3.1

<!-- rosetta-item: definition-10.3.1 -->

Let `f:A→ B` be a function, and let `b:B`.
The **fiber** of `f` at `b` is defined to be the type
```text
fib(f, b)≔Σ(a:A) f(a)=b.
```

In other words, the fiber of `f` at `b` is the type of `a:A` that get mapped by `f` to `b`.
One may think of the fiber as a type theoretic version of the preimage of a point.

It will be useful to have a characterization of the identity type of a fiber.
In order to identify any `(x,p)` and `(x',p')` in `fib(f, y)`, we may first construct an identification `α:x=x'`.
Then we obtain a triangle
<!-- rosetta-diagram: 64b5b852d28b; review: pending -->

*Triangle-shaped diagram (automatic draft).*

```text
[f(x)]               [f(x')]

            [y]

Arrows:
- f(x) --p--> y
- f(x) --{ap_{f}(α)}--> f(x')
- f(x') --{p'}--> y
```
so we may consider the type of identifications `β:p=ap_{f}(α) ∙ p'`.
We will show that the type of all identifications `(x,p)=(x',p')` is equivalent to the type of such pairs `(α,β)`.

## Definition 10.3.2

<!-- rosetta-item: definition-10.3.2 -->

Let `f:A → B` be a map, and let `(x,p),(x',p'):fib(f, y)` for some `y:B`.
Then we define
```text
Eq-fib_f((x,p),(x',p'))≔ Σ(α:x=x') p=ap_{f}(α) ∙ p'
```
The relation `Eq-fib_f:fib(f, y)→fib(f, y)→𝒰` is a reflexive relation, since we have
```text
λ (x,p). (refl,refl):Π((x,p):fib(f, y)) Eq-fib_f((x,p),(x,p)).
```

## Proposition 10.3.3

<!-- rosetta-item: proposition-10.3.3 -->

Consider a map `f:A→ B` and let `y:B`.
The canonical map
```text
((x,p)=(x',p'))→Eq-fib_f((x,p),(x',p'))
```
induced by the reflexivity of `Eq-fib_f` is an equivalence for any `(x,p),(x',p'):fib(f, y)`.

### Proof

<!-- rosetta-item: subheading-10.3-proof -->

*Proof.* The converse map
```text
Eq-fib_f((x,p),(x',p'))→ ((x,p)=(x',p'))
```
is easily defined by `Σ`-induction, and then path induction twice.
The homotopies witnessing that this converse map is indeed a right inverse as well as a left inverse are similarly constructed by induction. ◻

Now we define at the notion of contractible map.

## Definition 10.3.4

<!-- rosetta-item: definition-10.3.4 -->

We say that a function `f:A→ B` is **contractible** if it comes equipped with an element of type
```text
is-contr(f)≔Π(b:B) is-contr(fib(f, b)).
```

## Theorem 10.3.5

<!-- rosetta-item: theorem-10.3.5; latex-label: thm:equiv_contr -->

Any contractible map is an equivalence.

### Proof

<!-- rosetta-item: subheading-10.3-proof-2 -->

*Proof.* Let `f:A→ B` be a contractible map.
Using the center of contraction of each `fib(f, y)`, we obtain the dependent function
```text
λ y. (g(y),G(y)):Π(y:B) fib(f, y).
```
Thus, we get map `g:B→ A`, and a homotopy `G:Π(y:B) f(g(y))=y`.
In other words, we get a section of `f`.

It remains to construct a retraction of `f`.
Taking `g` as our retraction, we have to show that `Π(x:A) g(f(x))=x`.
Note that we get an identification `p:f(g(f(x)))=f(x)` since `g` is a section of `f`.
Therefore, it follows that `(g(f(x)),p):fib(f, f(x))`.
Moreover, since `fib(f, f(x))` is contractible we get an identification `q:(g(f(x)),p)=(x,refl)`.
The base path `ap_{pr 1}(q)` of this identification is an identification of type `g(f(x))=x`, as desired. ◻
