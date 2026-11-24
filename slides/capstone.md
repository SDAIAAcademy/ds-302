---
course: "Online Experiments and A/B Testing"
code: "DS-302"
version: "2027.2.0"
deck: "capstone"
day: 5
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-302/slides/capstone.html"
---

# Online Experiments and A/B Testing

## Capstone: The capstone review board

Each participant defends a design and analysis pack in ten minutes: seven to present, three for the board

#### [capstone#title] The capstone review board

*SDAIA Academy · Online Experiments and A/B Testing*

Capstone: Each participant defends a design and analysis pack in ten minutes: seven to present, three for the board

Data Science Track · 4 teaching days + capstone day · 7 min talk and demo · 3 min Q&A · DS-302

#### [capstone#agenda] How the review board runs

*Capstone*

- **The brief and final prep**: the rubric, the board's questions, a last rerun of each analysis
- **Defences**: seven minutes to present, three for the board, one participant at a time
- **Review and closing**: peer feedback, the trainer's review, what next

#### [capstone#the-brief] One AI-feature change, designed, analysed and decided

*The brief*

| Change | Goal | Harm to guard against |
| --- | --- | --- |
| C1 · AI-written dish descriptions | more orders from menus without a description | an ingredient the dish does not have |
| C2 · Luqma with an allergen checker | keep Luqma's lift without T-401's harm | a wrong ingredient or allergen answer |
| C3 · AI-ranked restaurant list | more first orders in a session | small restaurants pushed off the first screen |

The pack: pre-registration, sequential plan, trust checks, variance-reduced analysis, guardrails, one-page recommendation. Data from `sufrah.capstone_data()`; brief in `labs/capstone/README.md`.

#### [capstone#rubric] The rubric

*How packs are scored*

| Item | Value |
| --- | --- |
| Design and power | 25% |
| Analysis | 25% |
| Monitoring and guardrails | 20% |
| Recommendation | 20% |
| Reproducibility | 10% |

> **Every number reruns.** A number the board cannot regenerate from the repository scores as a claim, not a result.

#### [capstone#format] Ten minutes: seven to present, three for the board

*Format*

- **1 · The change and its risk.** Who it is for, what could go wrong, the harm guardrail. One slide.
- **2 · The design.** Unit, metrics, limits, power, the sequential plan, the rule.
- **3 · The result and the decision.** The effect with its interval, the guardrails, launch, iterate or stop.

> **Peer feedback.** After each defence, everyone writes one strength, one question and one suggestion.

#### [capstone#board-questions] One live change, then two questions

*What the board asks*

- **The live change.** The assessor changes the traffic (for example, halves it) or the pre-period (for example, 14 days in place of 28). The participant reruns the power calculation and says what can still be detected and what they would change.

- "Your harm rate is lower in treatment. Is that evidence the harm is gone?"
- "Why this spending function, not a fixed horizon?"
- "Your raw interval includes zero and the adjusted one does not. Which do you report?"
- "What would make you stop this test on day 10?"

#### [capstone#running-order] Who defends when

*Running order*

| # | Participant | Change |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |

#### [capstone#final-prep] Final prep · 20 minutes

*Before the first defence*

Rerun your analysis from a clean clone, rehearse once, open your repository on this screen.

#### [capstone#now-presenting] Present

*Now defending*

##### The board

#### [capstone#review] What the defences showed

*Trainer review*

- **Strongest patterns.** What several packs got right.
- **Common gaps.** What most packs would fix next.
- **One surprise.** Something nobody expected.

#### [capstone#what-next] Keep going

*After the course*

- **Follow-up task:** review one experiment from your workplace, or a public write-up, against the board's checklist of Lab 4.4.
- **Your pack stays yours:** keep it rerunnable and add the next design you named today.
- **When you cannot randomise:** DS-303 Causal Inference from Observational Data.
- **Deciding with heterogeneous effects:** DS-402 Causal Machine Learning and Policy Evaluation.

#### [capstone#thanks] Thank you

*SDAIA Academy*

Online Experiments and A/B Testing
