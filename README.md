## How to marry a star: probabilistic constraints for meaning in context 

This repo contains illustrative examples for the framework laid out in the following paper:

    @misc{erk2020marry,
        title={How to marry a star: probabilistic constraints for meaning in context},
        author={Katrin Erk and Aurelie Herbelot},
        year={2020},
        eprint={2009.07936},
        archivePrefix={arXiv},
        primaryClass={cs.CL}
    }

Available on arXiv at: https://arxiv.org/abs/2009.07936

### Summary

We discuss in this paper how people 'imagine' an entire situation from a few words, and how meaning is contextualised in the process. An example:

When you hear *the batter ran to the ball*, what do you imagine? A batter? A ball? But perhaps also a pitch, an audience, the sun and the cap over the eyes of the batter.

What do you imagine when you hear *the duchess drove to the ball*?

We propose a computational model which takes a (simple) sentence and builds a conceptual description for it. In the process of doing so, it captures  appropriate word senses or other lexical meaning variations. E.g. that the batter's ball is not a dancing event.

Sometimes, different interpretations compete with each other. Consider the sentence

*The astronomer married the star.*

What comes to your mind? The Hollywood star or the celestial object? Both?

To take care of this, our model generates not a single situation description but many, each one with its own probability. For some speaker, the description with the Hollywood star might be more likely than the one where the astronomer married Betelgeuse. Or vice-versa.

A situation description consists of:

* scenarios (at-the-restaurant, gothic-novel) 
* concepts (champagne, vampire)
* individuals (this bottle of champagne, Dracula)
* features of individuals (having a cork, being pale)
* roles (being the agent of a drinking event)

Technically speaking, the account is implemented as a probabilistic generative model. It takes the logical form of a sentence: 

∃x,y [astronomer(x)∧star(y)∧marry(x,y)]

and generates the conceptual descriptions most likely to account for that logical form. 

### Try out some examples

We have more examples in the Python notebook in this repo. You can clone it or run it straight from Binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/minimalparts/MeaningInContext/master?filepath=WebPPL_examples.ipynb)
