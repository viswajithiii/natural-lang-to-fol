import subprocess
import xml.etree.ElementTree as ET
import sys


# Global vars
CANDC_LOC = '/home/viswa/Downloads/candc-1.00/bin/candc'
MODELS_LOC = '/home/viswa/Downloads/models'


class Predicate:
    def __init__ (self, attrib):
        self.attrib = attrib
        self.name = attrib['word']
        self.lemma = attrib['lemma']
        if(attrib['cat']=='(S\NP)/NP'):
            self.lmbd = [1,0]
            self.args = [None,None]
        elif(attrib['cat']=='S\NP'):
            self.lmbd = [0]
            self.args = [None]
        elif(attrib['cat']=='NP'):
            self.lmbd = []
            self.args = []
        elif(attrib['cat']=='S/NP'):
            self.lmbd = [0]
            self.args = [None]
        else:
            self.lmbd = []
            self.args = []

    def combine(self, other):

        self.args[self.lmbd[0]] = other.attrib
        self.lmbd = self.lmbd[1:]

    def printunary (self):
        """Prints unary predicates, which are specified using a form of the word be."""
        if self.attrib['word'] == 'is':
            print self.args[1]['word'] + '(' + self.args[0]['word'] + ')'
        if self.attrib['word'] == 'are':
            print 'Forall x [' + self.args[0]['lemma'] + '(x) --> ' +  self.args[1]['word'] + '(x)]'


    def printsingularsubject(self):
        """Prints binary predicates with a singular subject."""

        if not len(self.args) == 2:
            print 'printsingularsubject error: Not a binary predicate'
            return

        #Index for quantifiers
        quant_index = 1
        quantifier = []
        firstbit = []


        op = [self.name, '(']

        #For singular noun objects.
        if self.args[1]['pos'] == 'NNP' or self.args[1]['pos'] == 'NN':

            for x in self.args:
                #Proper noun.
                if x['pos'] == 'NNP':
                    op.append(x['word'])
                else: #Common noun.
                    op.append('x' + str(quant_index))
                    firstbit.append(x['lemma'] + '(x' + str(quant_index) + ') and ')
                    quantifier.append('There_exists x' + str(quant_index) + ' ')
                    quant_index = quant_index + 1

                op.append(',')
            op = op[:-1] #To remove trailing comma.
            op.append(')')
        #For plural noun objects.
        if self.args[1]['pos'] == 'NNS' or self.args[1]['pos'] == 'NNPS':

            #Proper noun
            if self.args[0]['pos'] == 'NNP':
                op.append(self.args[0]['word'])
            else: #Common noun.
                op.append('x'+str(quant_index))
                firstbit.append(x['lemma'] + '(x' + str(quant_index) + ') and')
                quantifier.append('There_exists x' + str(quant_index)+ ' ')
                quant_index = quant_index + 1
            op.append(',')

            quantifier.append('For_all x' + str(quant_index) + ' ')
            op.append('x' + str(quant_index) + ')')
            firstbit.append(self.args[1]['lemma']+'(x' + str(quant_index) + ') --> ')


        print ''.join(quantifier), ''.join(firstbit), ''.join(op)

    def printpluralsubject(self):


        #For singular proper noun object.
        if self.args[1]['pos'] == 'NNP':
            print 'For_all x [' + self.args[0]['lemma'] + '(x) --> ' +  self.attrib['word'] + '(x, ' + self.args[1]['word'] + ')]'

        #For singular common noun object.
        if self.args[1]['pos'] == 'NN' or self.args[1]['pos'] == 'JJ':
            print 'There_exists x1 ' + self.args[1]['word'] + '(x1) and For_all x2 ' + self.args[0]['lemma'] + '(x2) --> ' + self.attrib['word'] + '(x2, x1)'
        #For plural noun objects.
        if self.args[1]['pos'] == 'NNS' or self.args[1]['pos'] == 'NNPS':
            print 'For_all x1 For_all x2 ' + self.args[0]['lemma'] + '(x1) and ' + self.args[1]['lemma'] + '(x2) --> ' + self.attrib['word'] + '(x1, x2)'


    def prettyPrint(self):
        
        #To handle Unary Predicates, which are specified using a form of the word be.
        if self.attrib['lemma'] == 'be':
            self.printunary()
        else:

            if self.args[0]['pos'] == 'NN' or self.args[0]['pos'] == 'NNP':
                self.printsingularsubject()
            if self.args[0]['pos'] == 'NNS' or self.args[0]['pos'] == 'NNPS':
                self.printpluralsubject()



def stripSqBkts(root):
    cat = []
    skip = False
    if root != None:
        for child in root:
            child = stripSqBkts(child)
        for c in root.attrib['cat']:
            if(c=='['):
                skip = True
            elif(c==']'):
                skip = False
                continue
            if(skip==False):
                cat.append(c)
        root.attrib['cat'] = ''.join(cat)
    return root


def postorder(root):
    retval = []
    if root != None:
        for child in root:
            retval.append(postorder(child))
        if(root.tag=='lf'):
            lmb_exp = Predicate(root.attrib)
        elif(len(retval)==2):
            if(len(retval[0].lmbd)==0):
                retval[1].combine(retval[0])
                lmb_exp = retval[1]
            elif(len(retval[1].lmbd)==0):
                if(retval[1].lemma=='JJ'):
                    lmb_exp = retval[1]
                else:
                    retval[0].combine(retval[1])
                    lmb_exp = retval[0]
        else:
            lmb_exp = retval[0]
    return lmb_exp


def main(argv):
    args = (CANDC_LOC + ' --models ' + MODELS_LOC + ' --log /dev/null --candc-printer xml').split()
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output = p.communicate(sys.stdin.readline())[0]
    root = ET.fromstring(output)[0][0]
    root = stripSqBkts(root)
    final = postorder(root)
    final.prettyPrint()


if __name__ == '__main__':
    main(sys.argv)
