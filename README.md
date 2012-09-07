# Localization tooling for JASY

Localization and internationalization tool support for Jasy

## About

Localization tooling for JASY consists of two different language file generators.
You can create .pot files that are translation templates used to generate
translation files from. If you don't plan to give your translation files to an
external translation service provider you can also use the easier po file handling.
These files are updated if new entries occure so you don't have to diff the old
and the new translation files.

## Import to your jasy project

To use localization tooling within your project add the following part to your jasyproject.json:

    "requires" : [ "https://github.com/fastner/jasy-localization.git" ]
    
## Usage

You can create POT files with the following jasy task:

    @task
    def translationtemplate():
        localization.generatePOT(jasy.env.State)
        
If you want to create the po files of the languages defined in your jasyscript file use

    @task
    def translation():
        localization.generatePO(jasy.env.State)