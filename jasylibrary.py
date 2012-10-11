#
# Localization tooling for JASY
#
#
# Copyright (C) 2012 Sebastian Fastner, Mainz, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import polib
from jasy.core.Console import *

class JasyPOFile(polib.POFile):
	"""
	Optimized POFile class that prevents empty first entry
	"""
	
	def __unicode__(self):
		"""
		Returns the unicode representation of the po file.
		"""
		entries = [self.metadata_as_entry()] + \
			[e for e in self if not e.obsolete]
      
		return polib.POFile.__unicode__(self).split("\n",4)[-1]



def collectTranslations(clazz, project):
	translations = clazz.getTranslations()
	trans = {}
	
	for key in translations:
		if not key in trans:
			trans[key] = []
		trans[key].append((clazz.getId(), translations[key]))
	
	return trans


def reduceTranslations(translations):
	t = {}
	
	for t1 in translations:
		for key in t1:
			if not key in t:
				t[key] = []
			for line in t1[key]:
				t[key].append(line)
	
	return t


def getTranslations(project):
	translations = []
	
	for clazz in project.getClasses():
		cls = project.getClassByName(clazz)
		translation = collectTranslations(cls, project)
		translations.append(translation)
	
	translations.reverse()
	translations = reduceTranslations(translations)
	
	return (sorted(translations.keys(), key=str.lower), translations)


def importLanguageFile(filename):
	values = {}
	
	po = polib.pofile(filename)
	for entry in po:
		values[entry.msgid] = entry.msgstr
	
	return values


def appendEntries(po, translations, oldValues={}):
	(sortedKeys, translations) = translations
		
	for key in sortedKeys:
		positions = translations[key]
		
		oldval = key
		if key in oldValues:
			oldval = oldValues[key]
		
		occurences=[]
		
		for position in positions:
			(clazz, posInClass) = position
			for pos in posInClass:
				occurences.append((clazz, pos))
		entry = polib.POEntry(
			msgid=key,
			msgstr=oldval,
			occurrences=occurences
		)
		po.append(entry)


@share
def generatePOT(session, config):
	header("Generating translation template...")
	info("Generate POT file...")
	
	project = session.getMain()
	filename = os.path.join(project.getPath(), "source", "translation", project.getName() + ".pot")
	po = JasyPOFile()
	appendEntries(po, getTranslations(project))
	po.save(filename)


@share
def generatePO(session, config, newLanguages=None):
	header("Generating translation files...")
	
	languages = session.getAvailableTranslations()
	if newLanguages:
		languages = languages | newLanguages
	project = session.getMain()
	
	info("Generate translation files...")
	indent()
	
	for language in languages:
		info("Initialize %s..." % colorize(language, "bold"))
		indent()
		
		filename = os.path.join(project.getPath(), "source", "translation", "%s.po" % language)
		
		oldValues = {}
		
		if (os.path.exists(filename)):
			info("Import old language file")
			oldValues = importLanguageFile(filename)
			
		info("Create new language file")
		
		po = JasyPOFile()
		appendEntries(po, getTranslations(project), oldValues)
		po.save(filename)
		
		outdent()


