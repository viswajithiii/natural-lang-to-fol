import subprocess
import xml.etree.ElementTree as ET
import sys


# Global vars
CANDC_LOC = '/run/media/sriram/8163f884-43b4-46a5-b61d-3a274dcd690a/sriram/Downloads/candc-1.00/bin/candc'
MODELS_LOC = '/run/media/sriram/8163f884-43b4-46a5-b61d-3a274dcd690a/sriram/Downloads/models'


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

    def prettyPrint(self):
        
        if self.attrib['lemma'] == 'be':
            if self.attrib['word'] == 'is':
                print self.args[1]['word'] + '(' + self.args[0]['word'] + ')'
            if self.attrib['word'] == 'are':
                print 'Forall x [' + self.args[0]['lemma'] + '(x) --> ' +  self.args[1]['word'] + '(x)]'

        else:
            num = 1
            firstbit = []
            there_exists = []
            if self.attrib['pos'] == 'VBZ':
                op = [self.name, '(']
                for x in self.args:
                    if(x['pos']=='NNP' or x['pos']=='NNPS'):
                        op.append(x['word'])
                    elif(x['pos']=='NN' or x['pos']=='NNS'):
                        op.append('x'+str(num))
                        firstbit.append(x['lemma']+'(x'+str(num)+') and ')
                        there_exists.append(' There_exists x'+str(num))
                        num = num+1
                    op.append(',')
                op = op[:-1]
                op.append(')')
                print ''.join(there_exists), ''.join(firstbit), ''.join(op)
            if self.attrib['pos'] == 'VBP':
                print 'Forall x [' + self.args[0]['lemma'] + '(x) --> ' +  self.attrib['lemma'] + '(x, ' + self.args[1]['word'] + ')]'



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
