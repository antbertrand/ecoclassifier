# majurca-ecoclassifier

Eco-classifier for Majurca. Contains both capture solution, experiments and the global solution used for the production machine.





# Installation / Configuration

## FOR ALL CONTAINERS EXCEPT majurca-ecoclassifier

Use NumeriCube's 'dmake' program (even if Docker is not supported)

dmake stack start as usual.

## For majurca-ecoclassifier

As this module is meant to be deployed in an embarked PC, one has to install it from outside Docker.


# Generate and read docs

Execute `dmake doc` and look at the `docs/build` folder for auto-generated documentation.


# Update labelling interface

Labelling is done with "cloudlabel". To update it, go to the 'cloudlabel' GH project and do the following:

$ dmake --azure --machine=cloudlabel-prod shell
$ docker ps # then spot one of Django's running instances
$ 

Go see how http://52.143.156.104/webapp/projects images count increases. It might get a while to get started.

