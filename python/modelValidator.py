#!/usr/bin/python
#    Copyright 2013 Joshua Charles Campbell
#
#    This file is part of UnnaturalCode.
#    
#    UnnaturalCode is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    UnnaturalCode is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with UnnaturalCode.  If not, see <http://www.gnu.org/licenses/>.

from ucUtil import *
from unnaturalCode import *
from pythonSource import *
from mitlmCorpus import *
from sourceModel import *

from logging import debug, info, warning, error
from random import randint

class validationFile(object):
    
    def __init__(self, path, language):
        self.path = path
        self.lm = language
        self.f = open(path)
        self.original = self.f.read()
        self.lexed = self.lm(self.original)
        self.scrubbed = self.lexed.scrubbed()
        self.f.close()
        self.mutatedLexemes = None
        self.mutatedLocation = None
    
    def mutate(self, lexemes, location):
        assert isinstance(lexemes, ucSource)
        self.mutatedLexemes = lexemes
        self.mutatedLocation = location
        self.mutatedSource = lexemes.deLex()
        
        
        
class modelValidation(object):
    
    def addValidationFile(self, files):
          """Add a file for validation..."""
          files = [files] if isinstance(files, str) else files
          assert isinstance(files, list)
          for fi in files:
            self.validFiles.append(validationFile(fi, self.lm))
    
    def genCorpus(self):
          for fi in self.validFiles:
            self.sm.trainLexemes(fi.scrubbed)
    
    def validate(self, mutation, n):
        assert n > 0
        for fi in self.validFiles:
          assert isinstance(fi, validationFile)
          for i in range(0, n):
            mutation(self, fi)
            
    def deleteRandom(self, vFile):
        ls = copy(vFile.scrubbed)
        token = ls.pop(randint(0, len(ls)))
        vFile.mutate(ls, token)
            
    def insertRandom(self, vFile):
        ls = copy(vFile.scrubbed)
        token = ls[randint(0, len(ls))]
        pos = randint(0, len(ls))
        ls.insert(pos, token)
        token = ls[pos]
        vFile.mutate(ls, token)
            
    def replaceRandom(self, vFile):
      ls = copy(vFile.scrubbed)
      token = ls[randint(0, len(ls))]
      pos = randint(0, len(ls))
      ls.pop(pos)
      ls.insert(pos, token)
      token = ls[pos]
      vFile.mutate(ls, token)
      
    def __init__(self, source=None, language=pythonSource, resultsDir=None, corpus=mitlmCorpus):
        self.resultsDir = ((resultsDir or os.getenv("ucResultsDir", None)) or mkdtemp(prefix='ucValidation-'))
        if isinstance(source, str):
            raise NotImplementedError
        elif isinstance(source, list):
            self.validFileNames = source
        else:
            raise TypeError("Constructor arguments!")

        assert os.access(self.resultsDir, os.X_OK & os.R_OK & os.W_OK)
        self.corpusPath = os.path.join(self.resultsDir, 'validationCorpus')
        self.cm = corpus(readCorpus=self.corpusPath, writeCorpus=self.corpusPath, order=10)
        self.lm = language
        self.sm = sourceModel(cm=self.cm, language=self.lm)
        self.validFiles = list()
        self.addValidationFile(self.validFileNames)
        self.genCorpus()

DELETE = modelValidation.deleteRandom
INSERT = modelValidation.insertRandom
REPLACE = modelValidation.replaceRandom