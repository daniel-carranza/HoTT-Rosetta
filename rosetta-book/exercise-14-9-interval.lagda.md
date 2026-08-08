# Exercise 14.9

```agda
module exercise-14-9-interval where

```

## Problem statement

In this exercise we introduce the **interval** as a higher inductive type `\I`, equipped with two point constructors and one path constructor
```text
source,target : \I
path : source=target.
```
The induction principle of `\I` asserts that for any type family `P` over `\I`, if we have
```text
u : P(source)
v : P(target)
p : tr_P(path,u)=v,
```
then there is a section `f:Π(x:\I) P(x)` equipped with identifications
```text
α : f(source) = u
β : f(target) = v
```
and an identification `γ` witnessing that the square
<!-- rosetta-diagram: e110adfc08e3; review: pending -->

*Square-shaped diagram (automatic draft).*

```text
[tr_P(path,f(source))]---->[tr_P(path,u)]
          |                      |
     [f(target)]      ---->     [v]

Arrows:
- tr_P(path,f(source)) --ap_{tr_P(path)}(α)--> tr_P(path,u)
- tr_P(path,f(source)) --apd_{f}(path)--> f(target)
- tr_P(path,u) --p--> v
- f(target) --β--> v
```
commutes.
Note that the constructors of `\I` induce a map
```text
ε: (Π(x:\I) P(x))→ (Σ(u:P(source)) Σ(v:P(target)) tr_P(path,u)=v).
```
given by `f↦ (f(source),f(target),apd_{f}(path))`.

<div class="subexenum">

Characterize the identity types of the codomain of the map `ε` in the following way: Construct an equivalence from the type `(u,v,q)=(u',v',q')` to the type
```text
Σ(α:u=u') Σ(β:v=v') q ∙ β=ap_{tr_P(path)}(α) ∙ q',
```
for any `(u,v,q)` and `(u',v',q')` in the codomain of `ε`.

Prove the dependent universal property of `\I`, i.e., show that the map `ε` is an equivalence.

Show that `\I` is contractible.

</div>

## Solution

<!-- rosetta-item: exercise-14-9 -->

No formalization has been curated yet.
