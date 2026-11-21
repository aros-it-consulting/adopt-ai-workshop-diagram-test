# Results

## haiku, low effort

### 1_data_model

| File | Success | Relative cost | Q1 | Q2 | Q3 | Q4 | Average cost ($) | Average turns |
|---|---|---|---|---|---|---|---|---|
| order_model.mmd | 5/5 | 100% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0035 | 4.0 |
| order_model.svg | 5/5 | 339% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0119 | 13.0 |
| order_model.png | 0/5 | 211% | 2/5 | 2/5 | 0/5 | 2/5 | 0.0074 | 16.6 |

### 2_deployment

| File | Success | Relative cost | Q1 | Q2 | Q3 | Q4 | Average cost ($) | Average turns |
|---|---|---|---|---|---|---|---|---|
| topology.mmd | 5/5 | 100% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0040 | 4.0 |
| topology.svg | 5/5 | 259% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0104 | 4.8 |
| topology.png | 0/5 | 91% | 2/5 | 2/5 | 0/5 | 0/5 | 0.0037 | 5.0 |

### 3_specification

| File | Success | Relative cost | Q1 | Q2 | Q3 | Q4 | Average cost ($) | Average turns |
|---|---|---|---|---|---|---|---|---|
| spec.md | 5/5 | 100% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0042 | 3.6 |
| spec.html | 5/5 | 144% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0060 | 3.2 |
| spec.bad.pdf | 5/5 | 194% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0081 | 3.0 |
| spec.good.pdf | 4/5 | 221% | 5/5 | 5/5 | 4/5 | 5/5 | 0.0093 | 3.4 |
| spec.bad.docx | 4/5 | 531% | 5/5 | 5/5 | 5/5 | 4/5 | 0.0223 | 25.8 |
| spec.good.docx | 0/5 | 137% | 5/5 | 5/5 | 0/5 | 5/5 | 0.0057 | 5.8 |

The costs are net of the control case of haiku: $0.0020.

## sonnet, low effort

### 1_data_model

| File | Success | Relative cost | Q1 | Q2 | Q3 | Q4 | Average cost ($) | Average turns |
|---|---|---|---|---|---|---|---|---|
| order_model.mmd | 5/5 | 100% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0281 | 3.0 |
| order_model.svg | 5/5 | 348% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0981 | 11.6 |
| order_model.png | 1/5 | 466% | 4/5 | 5/5 | 2/5 | 5/5 | 0.1311 | 20.2 |

### 2_deployment

| File | Success | Relative cost | Q1 | Q2 | Q3 | Q4 | Average cost ($) | Average turns |
|---|---|---|---|---|---|---|---|---|
| topology.mmd | 5/5 | 100% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0447 | 3.0 |
| topology.svg | 5/5 | 365% | 5/5 | 5/5 | 5/5 | 5/5 | 0.1631 | 4.0 |
| topology.png | 0/5 | 51% | 5/5 | 5/5 | 0/5 | 2/5 | 0.0226 | 4.6 |

### 3_specification

| File | Success | Relative cost | Q1 | Q2 | Q3 | Q4 | Average cost ($) | Average turns |
|---|---|---|---|---|---|---|---|---|
| spec.md | 5/5 | 100% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0551 | 3.0 |
| spec.good.pdf | 5/5 | 132% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0727 | 5.6 |
| spec.good.docx | 5/5 | 160% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0881 | 6.4 |
| spec.html | 5/5 | 171% | 5/5 | 5/5 | 5/5 | 5/5 | 0.0943 | 3.0 |
| spec.bad.pdf | 5/5 | 253% | 5/5 | 5/5 | 5/5 | 5/5 | 0.1395 | 19.0 |
| spec.bad.docx | 5/5 | 534% | 5/5 | 5/5 | 5/5 | 5/5 | 0.2940 | 24.0 |

The costs are net of the control case of sonnet: $0.0362.

- Success is the number of trials that answered every question right.
- The relative cost compares the cost with the one of the text format of the folder, at 100%.
- A question shows the number of trials that answered it right.
- The cost is the mean of the trials, net of the control case of their model.
