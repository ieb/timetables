import re

crsid_re = re.compile(r"\[(.*?)\]")

class Verifier:
    def verify_head(self,id,what,who,where):
        pass

    def verify_row(self,name,type,who,what,when,where,merge):
        if not crsid_re.search(who):
            err = "{{bad name '%s': it needs their crsid in square brackets after it.}}" % (who,)
            raise Exception(err)
