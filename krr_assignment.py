import subprocess
import xml.etree.ElementTree as ET
import sys


# Global vars
CANDC_LOC = '/run/media/sriram/8163f884-43b4-46a5-b61d-3a274dcd690a/sriram/Downloads/candc-1.00/bin/candc'
MODELS_LOC = '/run/media/sriram/8163f884-43b4-46a5-b61d-3a274dcd690a/sriram/Downloads/models'


class Predicate:
    def __init__ (self, cat, name):
        if(cat=='(S[dcl]\NP)/NP'):
            self.lmbd = [1,0]
            self.name = name
            self.args = [None,None]
        else:
            self.lmbd = []
            self.name = name
            self.args = []

    def combine(self, other):
        self.args[self.lmbd[0]] = other.name
        self.lmbd = self.lmbd[1:]

    def prettyPrint(self):
        op = [self.name, '(']
        for x in self.args:
            op.append(x)
            op.append(',')
        op = op[:-1]
        op.append(')')
        print ''.join(op)


def postorder(root):
    retval = []
    string = ''
    if root != None:
        for child in root:
            retval.append(postorder(child))
        if(root.tag=='lf'):
            string = root.attrib['word']
            lmb_exp = Predicate(root.attrib['cat'],string)
        elif(len(retval)==2):
            if(len(retval[0].lmbd)==0):
                retval[1].combine(retval[0])
                lmb_exp = retval[1]
            elif(len(retval[1].lmbd)==0):
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
    final = postorder(root)
    final.prettyPrint()


if __name__ == '__main__':
    main(sys.argv)
