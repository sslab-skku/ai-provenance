# AI Provenance Framework

This framework aims to automatically validate data privacy compiliance (e.g., GDPR) on python scripts that interact directly or indirectly via ML frameworks with the sensitive data. 



## Python instrumentation framework (`{ROOT}/python-inst`)
This framework instruments the python scripts to produce provenance information in the server's backend




---

# Current Design
## Threat Model
- Comany is not malicious, but data scientist in company might be malicious. He or she could perform forbidden process against the regulation by intentionaly or mistakenly.

## Overall Design
- The user will run the ML training code on the trusted server, which this project provides. The server will be connected to the training dataset's database. The user could not make a direct access to the database, but only with connection through codes.
- In the training process, there will be three steps - Finding dataset-variable and model-variable, Tracking dataset-variable, and recording dataset-variable and model-variable. If there is any vulnerable usage of the training set, the system will warn about the user and does not run the code.
- After finishing training process, the information of the training dataset and model will be saved on the provenance.

## Finding dataset-variable & model-variable
- The dataset variable could be found in two ways - By regulating the connection between database and the code, or by the static analysis.
- By the static analysis done in the Vamsa, we should have derivation extractor and KB-based annotator. By derivation extractor, we will get the flow of the variables as a graph. Then, with KB-based annotator, we could get which API is for training or making the model. With this knowledge, we could find out which variable is training data set or a model.


## Tracking dataset-variable
- As the first thought, when we found a dataset-variable, we could instrument python code as save those inputs and outputs between dataset-variable used APIs, and find out what was changed through those columns.
- Dynamic analysis could be used also if there is a loop or conditional code inside the ML code.
- Of course, this could be handled with the provenance tracker machanism in the Vamsa paper, but it has some errors due to there are lots of functions, and knowledge base does not have full information about it.
- Tracking data wrangling with semantic way [link](https://arxiv.org/pdf/2209.13995.pdf)

## Recording dataset-variable & model-variable
- The actual dataset would not be saved to the provenance - due to it is so large - so we should find what is important and not. We should record the example of training data, and column name, type to find out if it was private data or not by manually after the training section.
- The whole model will be saved with input example and output example, to find out if it's model is for making private data.

## Arising Challenges
- It is really enough to follow all of the usage of the variables? - Might have serious overhead.
- What this design really different from Vamsa?




