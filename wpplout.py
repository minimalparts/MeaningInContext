# functions for parsing webppl output
# for experiments for the paper
# How to marry a star: probabilistic constraints for meaning in context
# Katrin Erk, August 2020

import pandas as pd


#################################################
# webppl output where each line has a list of groups
# followewd by a list of roles
#
# example:
# "x0|0|Bat|bat,-idea,-sleep,animate|bat,animate x1|0|Idea|-bat,idea,-sleep,-animate|idea x2|0|Sleep|-bat,-idea,sleep,-animate|sleep ; Agent|x2|x0" : 1
###############3
# parsing a single sample with an output comprising
# groups, roles and a probability
# a group, and likewise a role, is a tuple,
# groups: a dictionary mapping group indices to groups.
# roles: a list of tuples
#
# return value:  a pair of a group dictionary, and a roles list
def parse_groupformat_samplestring(sample_string):
    pieces = sample_string.split(":")
    prob = float(pieces[1])
    groups_str, roles_str = pieces[0].strip('" ').split(";")

    groups = { }
    for groupstr in groups_str.split():
        pieces = groupstr.split("|")
        index = int(pieces[0][1:])
        scenarios = pieces[1].split(",")
        concepts = pieces[2].split(",")
        features = pieces[3].split(",")
        conditions = pieces[4].split(",")
        
        groups[index] = (index, scenarios, concepts, features, conditions)
    
    roles = [ ]
    for rolestr in roles_str.split():
        pieces = rolestr.split("|")
        rolelabel = pieces[0]
        eventindex= int(pieces[1][1:])
        fillerindex = int(pieces[2][1:])
        roles.append((rolelabel, eventindex, fillerindex))
    
    return( prob, groups, roles)

# given a file name,
# parse all samples
#
# returns a list of (groups, roles) pairs,
# where groups is a dictionary mapping group indices to groups,
# and roles is a list of role tuples
def parse_webppl_groupformat(filename):
    
    with open(filename) as f:
        sampled_lines = f.readlines()
    
    # ditch the first line, which just says Marginal:
    actual_sampled_lines = sampled_lines[1:]
    
    samples = [ parse_groupformat_samplestring(s) for s in actual_sampled_lines]
    
    return samples

# given a list of samples created by parse_webppl_groupformat,
# return a pandas data frame with probabilities for collections of
# roles and fillers (one sorted collection per sample)
def webppl_groupformat_eventspd(samples):
    prob_event = { }
        
    for sample in samples:
        prob, groups, roles = sample
        if len(roles) > 0:
            eventrep = [ ]
            for role in roles:
                rolename, evix, fillix = role
                evnames = groups[evix][2]
                fillnames = groups[fillix][2]
                evrep = "event:" + "/".join(evnames) + " role:" + rolename + " filler:" + "/".join(fillnames)
                eventrep.append(evrep)
                
            eventrep_s = ", ".join(sorted(eventrep))
            prob_event[ eventrep_s] = prob_event.get(eventrep_s, 0) + prob
                
    df =  pd.DataFrame(prob_event.items())
    df.columns = ["condition", "probability"]
    return df

# combination of file parsing and returning events dataframe
def parse_webppl_groupformat_eventspd(filename):
    samples = parse_webppl_groupformat(filename)
    return webppl_groupformat_eventspd(samples)

# given a list of samples created by parse_webppl_groupformat,
# return a pandas data frame listing probabilities for sorted lists of scenarios
def webppl_groupformat_scenariopd(samples):
    prob_scenario = { }
    for sample in samples:
        prob, groups, roles = sample
        scenarios = set()
        for group in groups.values():
            scenarios.update(group[1])

        sckey = ", ".join(sorted(scenarios))
        prob_scenario[ sckey] = prob_scenario.get(sckey, 0) + prob

    df = pd.DataFrame(prob_scenario.items())
    df.columns = ["scenarios", "prob"]
    return df

##
# make a pandas data frame with one column for number of referents,
# one column for probability.
# samples: output of parse_webppl_groupformat
def webppl_groupformat_referentspd(samples):
    prob_numref = { }
    
    for sample in samples:
        prob, groups, roles = sample
        numref = len(groups.keys())
        prob_numref[ numref] = prob_numref.get(numref, 0) + prob

    df = pd.DataFrame(prob_numref.items())
    df.columns = ["num referents", "prob"]
    return df
    

##
# make a pandas data frame with one column for number of referents,
# one column for the collection of scenarios sampled,
# one column for probability.
# samples: output of parse_webppl_groupformat
def webppl_groupformat_scenarios_referentspd(samples):
    prob_numref_scen = { }
    
    for sample in samples:
        prob, groups, roles = sample
        numref = len(groups.keys())
        
        scenarios = { }
        for group in groups.values():
            this_scenario = "/".join(sorted(group[1]))
            scenarios[ this_scenario] = scenarios.get(this_scenario, 0) + 1

        sckey = (numref, ", ".join( ", ".join([str(s)] * n) for s, n in sorted(scenarios.items())))
        prob_numref_scen[ sckey ] = prob_numref_scen.get(sckey, 0) + prob

    df_rows = [ [nscen[0], nscen[1], prob] for nscen, prob in prob_numref_scen.items() ]
    df = pd.DataFrame(df_rows)
    df.columns = ["num referents", "scenarios", "prob"]
    return df
    
##
# make a pandas data frame with one column for number of referents,
# one column for the collection of scenario/concept pairs sampled,
# one column for probability.
# samples: output of parse_webppl_groupformat
def webppl_groupformat_concepts_referentspd(samples):
    prob_numref_scen = { }
    
    for sample in samples:
        prob, groups, roles = sample
        # number of referents: number of entries in the group dictionary
        numref = len(groups.keys())

        # list of scenario/concept pairs
        scenario_concepts = [ ]
        # each value of the groups dictionary is one group
        for group in groups.values():
            # make string:
            # scenario/concept+scenario/concept+...
            scenario_concepts.append( "+".join(sorted(a + "/" + b for a, b in zip(group[1], group[2]))))

        sckey = (numref, ", ".join( sorted(scenario_concepts)))
        prob_numref_scen[ sckey ] = prob_numref_scen.get(sckey, 0) + prob

    df_rows = [ [nscen[0], nscen[1], prob] for nscen, prob in prob_numref_scen.items() ]
    df = pd.DataFrame(df_rows)
    df.columns = ["num referents", "concepts", "prob"]
    return df
    
   
##
# make a pandas data frame with one column for concept + feature vectors sampled,
# one column for probability. 
# samples: output of parse_webppl_groupformat
def webppl_groupformat_fvectors_pd(samples):
    prob_dict = { }
    
    for sample in samples:
        prob, groups, roles = sample
        # number of referents: number of entries in the group dictionary
        numref = len(groups.keys())

        # list of feature vectors
        groupstrings = [ ]
        # each value of the groups dictionary is one group
        for group in groups.values():
            # make string:
            # concepts + feature vector
            groupstrings.append( "+".join(group[2]) + ":" + ",".join(group[3]))

        sckey = ", ".join( sorted(groupstrings))
        prob_dict[ sckey ] = prob_dict.get(sckey, 0) + prob

    df = pd.DataFrame(prob_dict.items())
    df.columns = ["feature vectors", "prob"]
    return df

##
# make a pandas data frame with one column for concept + conditions sampled,
# one column for probability. 
# samples: output of parse_webppl_groupformat
def webppl_groupformat_conditions_pd(samples):
    prob_dict = { }
    
    for sample in samples:
        prob, groups, roles = sample
        # number of referents: number of entries in the group dictionary
        numref = len(groups.keys())

        # list of feature vectors
        groupstrings = [ ]
        # each value of the groups dictionary is one group
        for group in groups.values():
            # make string:
            # concepts + feature vector
            groupstrings.append( "+".join(group[2]) + ":" + ",".join(group[4]))

        sckey = ", ".join( sorted(groupstrings))
        prob_dict[ sckey ] = prob_dict.get(sckey, 0) + prob

    df = pd.DataFrame(prob_dict.items())
    df.columns = ["conditions", "prob"]
    return df

# a very specific function:
# counting occurrences of bat/animal versus bat/stick
# return as a data frame
def webppl_probbats(samples):
    prob_stick = 0
    prob_animal = 0

    for sample in samples:
        prob, groups, roles = sample
        
        # each value of the groups dictionary is one group
        for group in groups.values():
            # is there a bat-stick in this group? count. likewise for bat-animal
            # group[2] contains the concepts
            if "Bat-stick" in group[2]:
                prob_stick += prob
            if "Bat-animal" in group[2]:
                prob_animal += prob

    return pd.DataFrame({ "Concept" : ["Bat-stick", "Bat-animal"], "Empirical probability" : [prob_stick, prob_animal]})

## compute empirical probabilities of features
def webppl_groupformat_featureprob(samples):
    prob_dict = { }
    
    for sample in samples:
        prob, groups, roles = sample

        # list of feature vectors
        groupstrings = [ ]
        # each value of the groups dictionary is one group
        for group in groups.values():
            for feature in group[3]:
                if feature.startswith("-"):
                    # we only need to record probabilities of positive features
                    # since probabilities of all samples sum up to one
                    continue
                prob_dict[ feature] = prob_dict.get(feature, 0) + prob
                
    df = pd.DataFrame(prob_dict.items())
    df.columns = ["feature", "prob"]
    return df
    

# given a list of samples created by parse_webppl_groupformat,
# return a pandas data frame with probabilities for DRS-like output
def webppl_groupformat_drspd(samples):
    prob_drs = { }
        
    for sample in samples:
        prob, groups, roles = sample

        # make canonical ordering of groups and of roles
        grouptuples = [(scen, conc, fea, cond, ix) for ix, scen, conc, fea, cond in groups.values()]
        newgroups = { }
        oldindex_newindex = { }
        for index, group in enumerate(sorted(grouptuples)):
            scen, conc, fea, cond, oldix = group
            newgroups[index ] = (index, scen, conc, fea, cond)
            oldindex_newindex[ oldix] = index

        newroles = [ (r[0], oldindex_newindex[r[1]], oldindex_newindex[r[2]]) for r in roles]
            
        
        drs = ", ".join("x" + str(group[0]) + ":" + "/".join(group[2]) for group in newgroups.values())
        rolestrings = [ ]
        for role in newroles:
            rolename, evix, fillix = role
            rolestrings.append(rolename + "(x" + str(evix) + ", x" + str(fillix) + ")")

        if len(rolestrings) > 0:
            drs += " " + ", ".join(rolestrings)
        prob_drs[ drs] = prob_drs.get(drs, 0) + prob
                
    df =  pd.DataFrame(prob_drs.items())
    df.columns = ["drs", "probability"]
    return df
