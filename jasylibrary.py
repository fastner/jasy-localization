
import os
import polib
from jasy.core.Logging import *

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
def generatePOT(state):
	header("Generating translation template...")
	info("Generate POT file...")
	
	project = state.session.getMain()
	filename = os.path.join(project.getPath(), "source", "translation", project.getName() + ".pot")
	po = JasyPOFile()
	appendEntries(po, getTranslations(project))
	po.save(filename)


@share
def generatePO(state):
	header("Generating translation files...")
	
	languages = {}
	for permutation in state.session.getPermutations():
		lang = permutation.get("locale")
		languages[lang] = True
	
	languages = list(languages.keys())
	project = state.session.getMain()
	
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


