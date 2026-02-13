import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Values

    Here is a first pass at designing some measures.

    The first two involve L2 (apportionment) only.

    **V1**: **Apportionment Weight**. We simply divide the electors for each state by the population, giving $x_s \propto \frac{e_s}{n_s}$ for state $s$, then scale so they sum to $N$:

    $$
    \begin{align}
    x_s &= \frac{e_s / E}{n_s / N} \\
    \sum_s n_s x_s &= N \sum_s \frac{e_s}{E} = N
    \end{align}
    $$

    This is "L2" measure--it depends on apportionment only, and knows nothing of "swing states" or the like. It might also be called "relative representation". It could be easily adapted into meaures on the House and Senate as well.

    - can this be written as an appropriate generalization of the derivative above?
    - this measure would treat perfectly proportional apportionments $e_i \propto \frac{n_i}{N}$ as perfectly fair, even if they are WTA.

    **V2**, wasted votes at L2.

    - Without using party affiliation at all, how "susceptible" is an apportionment scheme to wasting votes, just due to the fact that $e_s$ votes swing together?
    - The idea here is to use to only L2 apportionment data, but to penalize WTA at the state/district level.
    - It will simplest to try to distinguish just the effects of grouping $n_s$ voters into "states" with vote $n_s$. We can handle the uneven apportionment separately (e.g. by V1). Ideally this will make V1 and V2 "orthogonal" to each other.
    - V2 is basically a measure of "coarse graining", then. The value of a vote in state should go down as the size of the state grows.
      - But when the state size reaches $N$, we just have a general election again, but now at a lower level: the entire election is decided "within the state".
      - Does this mean the valuation has a minimum? Or should it go to zero, but the valuation "within the state" then dominates?
      - Could it just be a sum like $\propto \frac{1}{n_s} + \frac{n_s}{N}$?
      - Of course, within a WTA state, a vote is perfectly fair. Where it's unfair is the level above this.
    - Everyone in the same state should have the same value. Once a state reaches 50% of the population the value of all other states becomes exactly zero, and its members reach 1.
    - We probably cannot require that coarse-graining affects only the voters within the affected states.
    - We may not be able to meet all those demands with the same measure, especially if it's normalized.

    **V3**: wasted votes at L3.

    - Here we can use the outcomes/party affiliations, either ex ante or ex post.
    - This should capture the size of the "flat" region in which a change in $r_s$ does not affect $r$.
    - That is, it should capture "waste from districts".
    - Ideally it would also depend on the national margin.


    - One idea: $x_i = 0$ for losing party, $x_i = \frac{1/2}{p_s}$ for winning party. Harsh for losers but basically captures the winner-take-all nature of state electors.
    - Another idea: $1 - \frac{L_s + (W_s - \frac{1}{2})}{n_s} = \frac{1}{2} - |p_s - \frac{1}{2}|$
      - $p_s = 0, 1 \to 0$, $p_s = \frac12 \to \frac{1}{2}$.

    - Might be better to think about "influence on candidates"
      - Some function of the margin of victory with $f(0) = 1$, decreasing?
        - Could compare to national margin: $\frac{f(m_s)}{f(m)}$.
        - What function? tanh? or just $1 - 2m$.



    **V4**: probability of a decisive vote?
    - there's established theory here.


    **V5**: some kind of smoothed $\tanh$ derivative things?

    $$
    \text{sign}(r_s) \longrightarrow \sigma(r_s / \tau_s)
    $$

    - Can get V1 in the vicinity of $r_s = 0$ if we take $\sigma'(0) = \frac{1}{n_s}$, maybe?

    **V6**: some other interpretation of the derivative $\frac{\partial r}{\partial  v_{s,i}}$, like an expectation over permutations of voters or something.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Measures

    Based on values?
    - mean absolute deviation (MAD)
    - mean square deviation (MSD), or Var
    - Shannon entropy of the set $\{x_i\}$, or perhaps relative entropy to the uniform

    **M1**. Apportionment only, L2

    **M2**. Wasted-vote efficiency gap?
    - wasted votes assigning zero value to losers feels weird, but maybe that's right for winner-take-all.
    - [see here](https://www.brennancenter.org/sites/default/files/legal-work/How_the_Efficiency_Gap_Standard_Works.pdf)
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
